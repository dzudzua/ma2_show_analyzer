from __future__ import annotations

import json
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs, quote, urlparse

from .ai import (
    PROMPT_VERSION,
    CueAnalysisError,
    OpenAICueAnalyzer,
    build_cue_payload,
    build_risk_payload,
    build_sequence_payload,
    cache_key,
)
from .web_jobs import (
    JobStore,
    ensure_within,
    parse_post_body,
    sanitize_name,
    save_uploads_to_job,
    start_background_job,
)
from .web_pages import IMG_DIR, build_home_page, build_job_page


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "web_jobs"


class AnalyzerWebHandler(BaseHTTPRequestHandler):
    store: JobStore

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/":
            message = parse_qs(parsed.query).get("message", [""])[0]
            self._send_html(build_home_page(self.store, message))
            return
        if parsed.path.startswith("/static/"):
            self._serve_static(parsed.path[len("/static/"):])
            return
        if parsed.path.startswith("/jobs/"):
            parts = [part for part in parsed.path.split("/") if part]
            if len(parts) == 2:
                self._send_html(build_job_page(self.store, parts[1]))
                return
            if len(parts) >= 4 and parts[2] == "reports":
                self._serve_report(parts[1], "/".join(parts[3:]))
                return
        self.send_error(HTTPStatus.NOT_FOUND, "Stranka nebyla nalezena")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/delete-job":
            self._handle_delete_job()
            return
        if parsed.path == "/ai-analyze-cue":
            self._handle_ai_analyze_cue()
            return
        if parsed.path == "/ai-analyze-sequence":
            self._handle_ai_analyze_sequence()
            return
        if parsed.path == "/ai-risk-cues":
            self._handle_ai_risk_cues()
            return
        if parsed.path != "/analyze":
            self.send_error(HTTPStatus.NOT_FOUND, "Stranka nebyla nalezena")
            return
        content_length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(max(0, content_length))
        _, fields = parse_post_body(self.headers, body)
        source_names = [sanitize_name(field.filename) for field in fields if getattr(field, "filename", None)]
        if not source_names:
            self._redirect("/?message=" + quote("Nebyl nahran zadny soubor."))
            return
        job_id = self.store.create_job(source_names)
        saved_names = save_uploads_to_job(self.store, job_id, fields)
        self.store.update_meta(job_id, source_names=saved_names or source_names, stage="Uploads stored", progress=8)
        start_background_job(self.store, job_id)
        self._redirect(f"/jobs/{quote(job_id)}")

    def _handle_delete_job(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(max(0, content_length))
        fields, _ = parse_post_body(self.headers, body)
        raw_job_id = (fields.get("job_id") or [""])[0]
        job_id = str(raw_job_id).strip()
        if not job_id:
            self._redirect("/?message=" + quote("Chybi job_id pro smazani."))
            return
        deleted, message = self.store.delete_job(job_id)
        self._redirect("/?message=" + quote(message))

    def _handle_ai_analyze_cue(self) -> None:
        payload = self._read_json_or_form_payload()
        if payload is None:
            return
        job_id = str(payload.get("job_id", "")).strip()
        cue_key = str(payload.get("cue_key", "")).strip()
        if not job_id or "::" not in cue_key:
            self._send_json({"ok": False, "error": "Chybi job_id nebo cue_key."}, status=HTTPStatus.BAD_REQUEST)
            return
        if not self.store.load_meta(job_id):
            self._send_json({"ok": False, "error": "Job nebyl nalezen."}, status=HTTPStatus.NOT_FOUND)
            return

        sequence_number, cue_number = cue_key.split("::", 1)
        analyzer = OpenAICueAnalyzer()
        cache_dir = self.store.ai_cache_dir(job_id)
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"{cache_key(PROMPT_VERSION, 'cue', sequence_number, cue_number, analyzer.provider, analyzer.model)}.json"
        if cache_path.exists():
            cached_payload = json.loads(cache_path.read_text(encoding="utf-8"))
            cached_payload["ok"] = True
            cached_payload["cached"] = True
            self._send_json(cached_payload)
            return

        try:
            cue_payload = build_cue_payload(self.store.output_dir(job_id), sequence_number, cue_number)
            result = analyzer.analyze_cue(cue_payload)
        except CueAnalysisError as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:  # pragma: no cover - network / external API
            self._send_json({"ok": False, "error": f"AI analyza selhala: {exc}"}, status=HTTPStatus.BAD_GATEWAY)
            return

        response_payload = {
            "ok": True,
            "cached": False,
            "provider": result.get("provider", ""),
            "model": result["model"],
            "analysis": result["analysis"],
            "sequence_number": sequence_number,
            "cue_number": cue_number,
        }
        cache_path.write_text(json.dumps(response_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self._send_json(response_payload)

    def _handle_ai_analyze_sequence(self) -> None:
        payload = self._read_json_or_form_payload()
        if payload is None:
            return
        job_id = str(payload.get("job_id", "")).strip()
        sequence_number = str(payload.get("sequence_number", "")).strip()
        if not job_id or not sequence_number:
            self._send_json({"ok": False, "error": "Chybi job_id nebo sequence_number."}, status=HTTPStatus.BAD_REQUEST)
            return
        if not self.store.load_meta(job_id):
            self._send_json({"ok": False, "error": "Job nebyl nalezen."}, status=HTTPStatus.NOT_FOUND)
            return

        analyzer = OpenAICueAnalyzer()
        cache_dir = self.store.ai_cache_dir(job_id)
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = cache_dir / f"{cache_key(PROMPT_VERSION, 'sequence', sequence_number, analyzer.provider, analyzer.model)}.json"
        if cache_path.exists():
            cached_payload = json.loads(cache_path.read_text(encoding="utf-8"))
            cached_payload["ok"] = True
            cached_payload["cached"] = True
            self._send_json(cached_payload)
            return

        try:
            sequence_payload = build_sequence_payload(self.store.output_dir(job_id), sequence_number)
            result = analyzer.analyze_sequence(sequence_payload)
        except CueAnalysisError as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:  # pragma: no cover
            self._send_json({"ok": False, "error": f"AI analyza sekvence selhala: {exc}"}, status=HTTPStatus.BAD_GATEWAY)
            return

        response_payload = {
            "ok": True,
            "cached": False,
            "provider": result.get("provider", ""),
            "model": result["model"],
            "analysis": result["analysis"],
            "sequence_number": sequence_number,
        }
        cache_path.write_text(json.dumps(response_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self._send_json(response_payload)

    def _handle_ai_risk_cues(self) -> None:
        payload = self._read_json_or_form_payload()
        if payload is None:
            return
        job_id = str(payload.get("job_id", "")).strip()
        sequence_number = str(payload.get("sequence_number", "")).strip() or None
        if not job_id:
            self._send_json({"ok": False, "error": "Chybi job_id."}, status=HTTPStatus.BAD_REQUEST)
            return
        if not self.store.load_meta(job_id):
            self._send_json({"ok": False, "error": "Job nebyl nalezen."}, status=HTTPStatus.NOT_FOUND)
            return

        analyzer = OpenAICueAnalyzer()
        cache_dir = self.store.ai_cache_dir(job_id)
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_scope = sequence_number or "show"
        cache_path = cache_dir / f"{cache_key(PROMPT_VERSION, 'risks', cache_scope, analyzer.provider, analyzer.model)}.json"
        if cache_path.exists():
            cached_payload = json.loads(cache_path.read_text(encoding="utf-8"))
            cached_payload["ok"] = True
            cached_payload["cached"] = True
            self._send_json(cached_payload)
            return

        try:
            risk_payload = build_risk_payload(self.store.output_dir(job_id), sequence_number)
            result = analyzer.analyze_risks(risk_payload)
        except CueAnalysisError as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:  # pragma: no cover
            self._send_json({"ok": False, "error": f"AI analyza rizik selhala: {exc}"}, status=HTTPStatus.BAD_GATEWAY)
            return

        response_payload = {
            "ok": True,
            "cached": False,
            "provider": result.get("provider", ""),
            "model": result["model"],
            "analysis": result["analysis"],
            "sequence_number": sequence_number or "",
        }
        cache_path.write_text(json.dumps(response_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self._send_json(response_payload)

    def _read_json_or_form_payload(self) -> dict[str, object] | None:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            content_length = int(raw_length)
        except ValueError:
            content_length = 0
        body = self.rfile.read(max(0, content_length))
        content_type = self.headers.get("Content-Type", "")
        try:
            if "application/json" in content_type:
                return json.loads(body.decode("utf-8") or "{}")
            return {key: values[0] for key, values in parse_qs(body.decode("utf-8")).items()}
        except json.JSONDecodeError:
            self._send_json({"ok": False, "error": "Neplatny JSON v AI requestu."}, status=HTTPStatus.BAD_REQUEST)
            return None

    def _serve_report(self, job_id: str, relative_name: str) -> None:
        safe_name = PurePosixPath(relative_name)
        if any(part in ("..", "") for part in safe_name.parts):
            self.send_error(HTTPStatus.BAD_REQUEST, "Neplatna cesta")
            return
        path = ensure_within(self.store.output_dir(job_id), self.store.output_dir(job_id).joinpath(*safe_name.parts))
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Report nebyl nalezen")
            return
        suffix = path.suffix.lower()
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".mjs": "text/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".csv": "text/csv; charset=utf-8",
            ".md": "text/markdown; charset=utf-8",
            ".txt": "text/plain; charset=utf-8",
        }.get(suffix, "application/octet-stream")
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_static(self, relative_name: str) -> None:
        safe_name = PurePosixPath(relative_name)
        if any(part in ("..", "") for part in safe_name.parts):
            self.send_error(HTTPStatus.BAD_REQUEST, "Neplatna cesta")
            return
        path = ensure_within(IMG_DIR, IMG_DIR.joinpath(*safe_name.parts))
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Staticky soubor nebyl nalezen")
            return
        suffix = path.suffix.lower()
        content_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".webp": "image/webp",
            ".ico": "image/x-icon",
        }.get(suffix, "application/octet-stream")
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_html(self, markup: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = markup.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def create_server(host: str, port: int, data_dir: Path) -> ThreadingHTTPServer:
    store = JobStore(data_dir)

    class BoundHandler(AnalyzerWebHandler):
        pass

    BoundHandler.store = store
    return ThreadingHTTPServer((host, port), BoundHandler)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="grandMA2 Show Analyzer Web Server")
    parser.add_argument("--host", default="127.0.0.1", help="Adresa rozhrani pro naslouchani")
    parser.add_argument("--port", default=8765, type=int, help="Port serveru")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR), help="Adresar pro ulozene joby")
    parser.add_argument("--open-browser", action="store_true", help="Po startu otevrit vychozi prohlizec")
    args = parser.parse_args(argv)

    server = create_server(args.host, args.port, Path(args.data_dir))
    url = f"http://{args.host}:{args.port}/"
    print(f"grandMA2 Show Analyzer bezi na {url}")
    print(f"Adresar jobu: {Path(args.data_dir).resolve()}")
    if args.open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nZastavuji server...")
    finally:
        server.server_close()
    return 0
