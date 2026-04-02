from __future__ import annotations

import io
import json
import os
import shutil
import stat
import threading
import time
import traceback
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from email.parser import BytesParser
from email.policy import default as email_policy
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs

from .parser import XMLShowParser
from .reporters import ReportWriter


@dataclass
class UploadedField:
    filename: str
    file: io.BytesIO


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sanitize_name(name: str) -> str:
    safe = Path(name or "").name.strip().replace("\x00", "")
    if not safe:
        return "upload.bin"
    return safe


def ensure_within(base: Path, target: Path) -> Path:
    resolved_base = base.resolve()
    resolved_target = target.resolve()
    if resolved_base not in resolved_target.parents and resolved_target != resolved_base:
        raise ValueError("Path escapes base directory")
    return resolved_target


def parse_post_body(headers: object, body: bytes) -> tuple[dict[str, list[str]], list[UploadedField]]:
    content_type = ""
    if hasattr(headers, "get"):
        content_type = str(headers.get("Content-Type", ""))

    if "application/x-www-form-urlencoded" in content_type:
        params = parse_qs(body.decode("utf-8"))
        return ({key: list(values) for key, values in params.items()}, [])

    if "multipart/form-data" not in content_type:
        return ({}, [])

    raw_message = f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8") + body
    message = BytesParser(policy=email_policy).parsebytes(raw_message)
    fields: dict[str, list[str]] = {}
    uploads: list[UploadedField] = []

    for part in message.iter_parts():
        if part.get_content_disposition() != "form-data":
            continue
        name = part.get_param("name", header="content-disposition") or ""
        filename = part.get_filename()
        payload = part.get_payload(decode=True) or b""
        if filename:
            uploads.append(UploadedField(filename=filename, file=io.BytesIO(payload)))
            continue
        value = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
        fields.setdefault(name, []).append(value)
    return (fields, uploads)


def _rmtree_with_retries(target: Path, attempts: int = 6, delay_seconds: float = 0.35) -> None:
    def onerror(func: object, path: str, exc_info: object) -> None:
        try:
            os.chmod(path, stat.S_IWRITE)
        except OSError:
            pass
        func(path)

    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            shutil.rmtree(target, onerror=onerror)
            return
        except PermissionError as exc:
            last_error = exc
            if attempt == attempts - 1:
                break
            time.sleep(delay_seconds)
    if last_error:
        raise last_error


class JobStore:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_job(self, source_names: list[str]) -> str:
        job_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
        self.input_dir(job_id).mkdir(parents=True, exist_ok=True)
        self.output_dir(job_id).mkdir(parents=True, exist_ok=True)
        self._write_meta(
            job_id,
            {
                "job_id": job_id,
                "created_at": utc_now_iso(),
                "updated_at": utc_now_iso(),
                "status": "uploaded",
                "stage": "Upload received",
                "progress": 5,
                "source_names": source_names,
                "error": "",
            },
        )
        return job_id

    def job_dir(self, job_id: str) -> Path:
        return self.base_dir / job_id

    def input_dir(self, job_id: str) -> Path:
        return self.job_dir(job_id) / "uploads"

    def output_dir(self, job_id: str) -> Path:
        return self.job_dir(job_id) / "out"

    def meta_path(self, job_id: str) -> Path:
        return self.job_dir(job_id) / "meta.json"

    def error_path(self, job_id: str) -> Path:
        return self.job_dir(job_id) / "error.txt"

    def ai_cache_dir(self, job_id: str) -> Path:
        return self.job_dir(job_id) / "ai_cache"

    def _write_meta(self, job_id: str, meta: dict[str, object]) -> None:
        meta["updated_at"] = utc_now_iso()
        self.meta_path(job_id).write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    def load_meta(self, job_id: str) -> dict[str, object] | None:
        path = self.meta_path(job_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def update_meta(self, job_id: str, **updates: object) -> dict[str, object]:
        meta = self.load_meta(job_id) or {"job_id": job_id}
        meta.update(updates)
        self._write_meta(job_id, meta)
        return meta

    def list_jobs(self) -> list[dict[str, object]]:
        jobs: list[dict[str, object]] = []
        for path in sorted(self.base_dir.iterdir(), reverse=True):
            if not path.is_dir():
                continue
            meta = self.load_meta(path.name)
            if meta:
                jobs.append(meta)
        return jobs

    def report_files(self, job_id: str) -> list[Path]:
        out_dir = self.output_dir(job_id)
        if not out_dir.exists():
            return []
        return sorted([path for path in out_dir.iterdir() if path.is_file()], key=lambda item: item.name.lower())

    def delete_job(self, job_id: str) -> tuple[bool, str]:
        job_dir = self.job_dir(job_id)
        if not job_dir.exists() or not job_dir.is_dir():
            return (False, "Job nebyl nalezen.")
        ensure_within(self.base_dir, job_dir)
        meta = self.load_meta(job_id) or {}
        status = str(meta.get("status", "") or "")
        if status == "processing":
            return (False, "Job se prave zpracovava a zatim ho nelze smazat.")
        try:
            _rmtree_with_retries(job_dir)
        except PermissionError:
            return (False, "Job se nepodarilo smazat, protoze nektery soubor je stale otevreny nebo zamceny.")
        except OSError as exc:
            return (False, f"Job se nepodarilo smazat: {exc}")
        return (True, f"Job {job_id} byl smazan.")


def save_uploads_to_job(store: JobStore, job_id: str, fields: list[UploadedField]) -> list[str]:
    uploaded_names: list[str] = []
    input_dir = store.input_dir(job_id)
    for field in fields:
        if not getattr(field, "filename", None):
            continue
        filename = sanitize_name(field.filename)
        uploaded_names.append(filename)
        if filename.lower().endswith(".zip"):
            extract_zip_upload(field.file, input_dir, filename)
            continue
        target = ensure_within(input_dir, input_dir / filename)
        with target.open("wb") as handle:
            shutil.copyfileobj(field.file, handle)
    return uploaded_names


def extract_zip_upload(fileobj: io.BufferedIOBase, input_dir: Path, archive_name: str) -> None:
    archive_dir = input_dir / Path(archive_name).stem
    archive_dir.mkdir(parents=True, exist_ok=True)
    data = fileobj.read()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            member_path = PurePosixPath(member.filename)
            safe_parts = [part for part in member_path.parts if part not in ("", ".", "..")]
            if not safe_parts:
                continue
            target = archive_dir.joinpath(*safe_parts)
            ensure_within(archive_dir, target)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target.open("wb") as dest:
                shutil.copyfileobj(source, dest)


def analyze_job(store: JobStore, job_id: str) -> None:
    store.update_meta(job_id, status="processing", stage="Preparing analysis", progress=10, error="")
    input_dir = store.input_dir(job_id)
    output_dir = store.output_dir(job_id)
    try:
        store.update_meta(job_id, status="processing", stage="Parsing uploads", progress=25, error="")
        show = XMLShowParser().parse_folder(input_dir, recursive=True, glob="*.xml")
        store.update_meta(job_id, status="processing", stage="Building reports", progress=72, error="")
        ReportWriter().write_all(show, output_dir)
        generated = [path.name for path in store.report_files(job_id)]
        store.update_meta(
            job_id,
            status="completed",
            stage="Completed",
            progress=100,
            generated_files=generated,
        )
    except Exception as exc:  # pragma: no cover - defensive for app flow
        store.error_path(job_id).write_text(traceback.format_exc(), encoding="utf-8")
        store.update_meta(job_id, status="failed", stage="Failed", progress=100, error=str(exc))


def start_background_job(store: JobStore, job_id: str) -> threading.Thread:
    worker = threading.Thread(target=analyze_job, args=(store, job_id), daemon=True, name=f"job-{job_id}")
    worker.start()
    return worker
