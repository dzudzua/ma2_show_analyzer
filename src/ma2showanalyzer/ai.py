from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest

PROMPT_VERSION = "cs_strict_v3"


class CueAnalysisError(RuntimeError):
    """Raised when AI cue analysis cannot be completed."""


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _safe_json_loads(value: str | None) -> Any:
    text = (value or "").strip()
    if not text:
        return []
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def load_cue_options(output_dir: Path) -> list[dict[str, str]]:
    rows = _read_csv_rows(output_dir / "main_cue_analysis.csv")
    options: list[dict[str, str]] = []
    for row in rows:
        sequence_number = (row.get("sequence_number") or "").strip()
        cue_number = (row.get("cue_number") or "").strip()
        if not sequence_number or not cue_number:
            continue
        cue_name = (row.get("cue_name") or "").strip() or f"Cue {cue_number}"
        label = f"Seq {sequence_number} / Cue {cue_number} - {cue_name}"
        options.append(
            {
                "sequence_number": sequence_number,
                "cue_number": cue_number,
                "cue_name": cue_name,
                "label": label,
            }
        )
    return options


def load_sequence_options(output_dir: Path) -> list[dict[str, str]]:
    rows = _read_csv_rows(output_dir / "sequences.csv")
    if not rows:
        rows = _read_csv_rows(output_dir / "main_cue_analysis.csv")

    options: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        sequence_number = (row.get("number") or row.get("sequence_number") or "").strip()
        if not sequence_number or sequence_number in seen:
            continue
        seen.add(sequence_number)
        sequence_name = (row.get("name") or row.get("sequence_name") or "").strip() or f"Sekvence {sequence_number}"
        cue_count = (row.get("cue_count") or "").strip()
        is_main = str(row.get("is_main_cue_list", "")).strip().lower() == "true"
        suffix = " (hlavni cue list)" if is_main else ""
        if cue_count:
            suffix = f"{suffix} - {cue_count} cue"
        options.append(
            {
                "sequence_number": sequence_number,
                "sequence_name": sequence_name,
                "label": f"Sekvence {sequence_number} - {sequence_name}{suffix}",
            }
        )
    return options


def build_cue_payload(output_dir: Path, sequence_number: str, cue_number: str) -> dict[str, Any]:
    main_rows = _read_csv_rows(output_dir / "main_cue_analysis.csv")
    if not main_rows:
        raise CueAnalysisError("Chybi main_cue_analysis.csv. Nejdriv vygenerujte reporty.")

    target_row: dict[str, str] | None = None
    row_index = -1
    for index, row in enumerate(main_rows):
        if (row.get("sequence_number") or "").strip() == sequence_number and (row.get("cue_number") or "").strip() == cue_number:
            target_row = row
            row_index = index
            break
    if not target_row:
        raise CueAnalysisError(f"Cue sequence={sequence_number} cue={cue_number} nebyla nalezena.")

    details_path = output_dir / "main_cue_analysis.json"
    detail_rows: list[dict[str, Any]] = []
    if details_path.exists():
        raw_details = json.loads(details_path.read_text(encoding="utf-8"))
        detail_rows = list(raw_details.get("sequence_content_rows", []))

    fixture_rows = [
        row for row in detail_rows
        if str(row.get("sequence_number", "")) == sequence_number and str(row.get("cue_number", "")) == cue_number
    ]

    context = {
        "job_files": {
            "main_cue_analysis_csv": str(output_dir / "main_cue_analysis.csv"),
            "main_cue_analysis_json": str(details_path) if details_path.exists() else "",
        },
        "cue": {
            "sequence_number": sequence_number,
            "sequence_name": target_row.get("sequence_name", ""),
            "cue_number": cue_number,
            "cue_name": target_row.get("cue_name", ""),
            "trigger": target_row.get("trigger", ""),
            "trigger_time": target_row.get("trigger_time", ""),
            "fade": target_row.get("fade", ""),
            "delay": target_row.get("delay", ""),
            "down_delay": target_row.get("down_delay", ""),
            "command": target_row.get("command", ""),
            "fixture_count": len(_safe_json_loads(target_row.get("fixture_ids"))),
            "fixtures": _safe_json_loads(target_row.get("fixture_details"))[:18],
            "references": _safe_json_loads(target_row.get("references")),
            "preset_refs": _safe_json_loads(target_row.get("preset_refs")),
            "effect_refs": _safe_json_loads(target_row.get("effect_refs")),
            "group_refs": _safe_json_loads(target_row.get("group_refs")),
            "hard_value_count": target_row.get("hard_value_count", "0"),
            "hard_value_attributes": _safe_json_loads(target_row.get("hard_value_attributes")),
            "hard_value_preview": _safe_json_loads(target_row.get("hard_value_preview"))[:24],
            "source_file": target_row.get("source_file", ""),
        },
        "neighbor_cues": {
            "previous": main_rows[row_index - 1] if row_index > 0 else None,
            "next": main_rows[row_index + 1] if row_index + 1 < len(main_rows) else None,
        },
        "fixture_samples": fixture_rows[:14],
    }
    return context


def build_sequence_payload(output_dir: Path, sequence_number: str) -> dict[str, Any]:
    sequence_rows = _read_csv_rows(output_dir / "sequences.csv")
    cue_rows = _read_csv_rows(output_dir / "cues.csv")
    if not sequence_rows or not cue_rows:
        raise CueAnalysisError("Chybi sequences.csv nebo cues.csv. Nejdriv vygenerujte reporty.")

    sequence_row = next(
        (row for row in sequence_rows if (row.get("number") or "").strip() == sequence_number),
        None,
    )
    selected_cues = [row for row in cue_rows if (row.get("sequence_number") or "").strip() == sequence_number]
    if not sequence_row or not selected_cues:
        raise CueAnalysisError(f"Sekvence {sequence_number} nebyla nalezena.")

    risk_rows = _read_csv_rows(output_dir / "risk_hotspots.csv")
    sequence_risks = [row for row in risk_rows if f"Seq {sequence_number} " in (row.get("subject") or "")]

    cue_summaries: list[dict[str, Any]] = []
    for row in selected_cues[:160]:
        cue_summaries.append(
            {
                "cue_number": row.get("cue_number", ""),
                "cue_name": row.get("name", "") or row.get("cue_name", ""),
                "trigger": row.get("trigger", ""),
                "trigger_time": row.get("trigger_time", ""),
                "fade": row.get("fade", ""),
                "delay": row.get("delay", ""),
                "down_delay": row.get("down_delay", ""),
                "command": row.get("command", ""),
                "is_main_cue_list": row.get("is_main_cue_list", ""),
                "fixture_count": len(str(row.get("fixture_ids", "")).split()) if str(row.get("fixture_ids", "")).strip() else 0,
                "references": str(row.get("references", "")).split(" | ")[:12] if str(row.get("references", "")).strip() else [],
                "value_count": row.get("value_count", "0"),
                "source_file": row.get("source_file", ""),
            }
        )

    return {
        "job_files": {
            "sequences_csv": str(output_dir / "sequences.csv"),
            "cues_csv": str(output_dir / "cues.csv"),
            "risk_hotspots_csv": str(output_dir / "risk_hotspots.csv"),
        },
        "sequence": {
            "sequence_number": sequence_number,
            "sequence_name": sequence_row.get("name", ""),
            "is_main_cue_list": sequence_row.get("is_main_cue_list", ""),
            "cue_count": len(selected_cues),
            "cue_summaries": cue_summaries,
            "top_risk_rows": sequence_risks[:15],
        },
    }


def build_risk_payload(output_dir: Path, sequence_number: str | None = None) -> dict[str, Any]:
    risk_rows = _read_csv_rows(output_dir / "risk_hotspots.csv")
    if not risk_rows:
        raise CueAnalysisError("Chybi risk_hotspots.csv. Nejdriv vygenerujte reporty.")

    main_rows = _read_csv_rows(output_dir / "main_cue_analysis.csv")
    if sequence_number:
        filtered_risks = [row for row in risk_rows if f"Seq {sequence_number} " in (row.get("subject") or "")]
        filtered_rows = [row for row in main_rows if (row.get("sequence_number") or "").strip() == sequence_number]
    else:
        filtered_risks = risk_rows
        filtered_rows = main_rows

    cue_index = {
        f"Seq {row.get('sequence_number', '')} Cue {row.get('cue_number', '')} {row.get('cue_name', '')}".strip(): row
        for row in filtered_rows
    }

    enriched_risks: list[dict[str, Any]] = []
    for row in filtered_risks[:20]:
        subject = row.get("subject", "")
        cue_row = cue_index.get(subject)
        enriched_risks.append(
            {
                "subject": subject,
                "risk_score": row.get("risk_score", ""),
                "details": row.get("details", ""),
                "cue_number": cue_row.get("cue_number", "") if cue_row else "",
                "cue_name": cue_row.get("cue_name", "") if cue_row else "",
                "hard_value_count": cue_row.get("hard_value_count", "") if cue_row else "",
                "fixture_count": len(_safe_json_loads(cue_row.get("fixture_ids"))) if cue_row else "",
                "preset_refs": _safe_json_loads(cue_row.get("preset_refs"))[:8] if cue_row else [],
                "hard_value_attributes": _safe_json_loads(cue_row.get("hard_value_attributes"))[:8] if cue_row else [],
            }
        )

    return {
        "job_files": {
            "risk_hotspots_csv": str(output_dir / "risk_hotspots.csv"),
            "main_cue_analysis_csv": str(output_dir / "main_cue_analysis.csv"),
        },
        "scope": {
            "sequence_number": sequence_number or "",
            "item_count": len(enriched_risks),
        },
        "risk_hotspots": enriched_risks,
    }


class OpenAICueAnalyzer:
    def __init__(self) -> None:
        self.provider = (os.getenv("MA2_AI_PROVIDER", "ollama") or "ollama").strip().lower()
        self.model = self._resolve_model()
        self.base_url = self._resolve_base_url()

    def _resolve_model(self) -> str:
        explicit_model = (os.getenv("MA2_AI_MODEL", "") or "").strip()
        if explicit_model:
            return explicit_model
        if self.provider == "ollama":
            return "llama3.1:8b"
        return "gpt-5-mini"

    def _resolve_base_url(self) -> str | None:
        explicit_base = (os.getenv("MA2_AI_BASE_URL", "") or "").strip()
        if explicit_base:
            return explicit_base
        if self.provider == "ollama":
            return "http://127.0.0.1:11434"
        return (os.getenv("OPENAI_BASE_URL", "") or "").strip() or None

    def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.provider == "ollama":
            return self._analyze_with_ollama(payload)
        return self._analyze_with_openai(payload)

    def analyze_cue(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.analyze(payload)

    def analyze_sequence(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.analyze(
            {
                "analysis_type": "sequence_review",
                **payload,
            }
        )

    def analyze_risks(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.analyze(
            {
                "analysis_type": "risk_review",
                **payload,
            }
        )

    def _analyze_with_ollama(self, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = self._build_prompt(payload)
        analysis = self._ollama_generate(prompt)
        if self._looks_too_english(analysis):
            analysis = self._ollama_force_czech(analysis)
        if self._looks_too_english(analysis):
            analysis = self._prepend_czech_warning(analysis)
        return {
            "provider": self.provider,
            "model": self.model,
            "analysis": analysis,
        }

    def _ollama_generate(self, prompt: str) -> str:
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        base_url = (self.base_url or "http://127.0.0.1:11434").rstrip("/")
        endpoint = f"{base_url}/api/generate"
        req = urlrequest.Request(
            endpoint,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlrequest.urlopen(req, timeout=180) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urlerror.URLError as exc:
            raise CueAnalysisError(f"Ollama neni dostupna na {endpoint}. Spustte Ollamu a overte model `{self.model}`.") from exc
        except json.JSONDecodeError as exc:
            raise CueAnalysisError("Ollama vratila neplatnou odpoved.") from exc

        analysis = str(data.get("response", "")).strip()
        if not analysis:
            raise CueAnalysisError("Ollama nevratila zadny text analyzy.")
        return analysis

    def _analyze_with_openai(self, payload: dict[str, Any]) -> dict[str, Any]:
        api_key = self._resolve_openai_api_key()
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise CueAnalysisError("Pro OpenAI provider chybi balicek `openai`. Nainstalujte ho jen pokud chcete OpenAI rezim.") from exc

        client_kwargs: dict[str, Any] = {"api_key": api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        client = OpenAI(**client_kwargs)
        response = client.responses.create(
            model=self.model,
            instructions=(
                "Jsi senior grandMA2 lighting programmer a show analyst. "
                "Z poskytnutych dat vysvetli, co cue dela umelecky i technicky. "
                "Bud konkretni, nehalucinuj nepritomne informace a pracuj jen s dodanymi daty. "
                "Odpovez cesky v Markdownu v sekcich: Shrnuti, Co se v cue deje, Rizika / nejasnosti, Doporuceni."
            ),
            input=self._build_prompt(payload),
        )
        return {
            "provider": self.provider,
            "model": self.model,
            "analysis": response.output_text.strip(),
        }

    def _resolve_openai_api_key(self) -> str:
        api_key = (os.getenv("OPENAI_API_KEY", "") or "").strip()
        if not api_key:
            raise CueAnalysisError("Chybi OPENAI_API_KEY. Pro lokalni beh nastavte `MA2_AI_PROVIDER=ollama`.")
        return api_key

    def _build_prompt(self, payload: dict[str, Any]) -> str:
        analysis_type = str(payload.get("analysis_type", "cue_review"))
        if analysis_type == "sequence_review":
            task = (
                "Vyhodnot celou sekvenci. Popis dramaturgii, programatorske vzory, opakujici se problemy, "
                "silne momenty a navrhni konkretni cleanup nebo refaktor cue listu."
            )
        elif analysis_type == "risk_review":
            task = (
                "Vyhodnot nejrizikovejsi cue. U kazde z nich vysvetli, proc je rizikova, co muze zlobit pri dalsim editovani "
                "a kterou cue by mel programmer zkontrolovat jako prvni."
            )
        else:
            task = (
                "Popis zamer cue, dominantni fixture/preset patterny, vazbu na sousedni cue a technicke nebo programatorske zlepseni."
            )
        prompt = json.dumps(payload, ensure_ascii=False, indent=2)
        return (
            "Jsi senior grandMA2 lighting programmer a show analyst.\n"
            "Odpovidej vyhradne cesky.\n"
            "Nikdy nevysvetluj hlavni cast odpovedi anglicky.\n"
            "Anglicky smi zustat pouze puvodni nazvy objektu, presetu, cue, fixture typu, atributu a technicke identifikatory presne tak, jak prichazeji ve vstupnich datech.\n"
            "Vsechny popisy, shrnuti, zavery, doporuceni, odrazky i nadpisy musi byt cesky.\n"
            "Nevracej obecnou definici JSON ani obecne poucky o datech. Pis prakticky a konkretne k dodanym datum.\n"
            "Nehalucinuj nepritomne informace a pracuj jen s dodanymi daty.\n"
            "Odpovez v Markdownu v sekcich: Shrnuti, Co se v cue nebo sekvenci deje, Rizika / nejasnosti, Doporuceni.\n\n"
            f"Ukol: {task}\n\n"
            f"{prompt}"
        )

    def _ollama_force_czech(self, analysis: str) -> str:
        prompt = (
            "Prepis nasledujici analyzu vyhradne do cestiny.\n"
            "Zachovej vecny obsah, ale vsechny vysvetlujici vety, nadpisy a odrazky napis cesky.\n"
            "Anglicky smi zustat pouze puvodni nazvy objektu, cue, fixture typu, atributu, presetu a technicke identifikatory.\n"
            "Nevysvetluj, co delas. Vrat jen finalni ceskou verzi v Markdownu.\n\n"
            f"{analysis}"
        )
        return self._ollama_generate(prompt)

    def _looks_too_english(self, text: str) -> bool:
        lowered = (text or "").lower()
        if not lowered.strip():
            return False
        english_markers = [
            "this is",
            "the following",
            "each object",
            "each array",
            "main object",
            "top risk",
            "array elements",
            "properties",
            "represents",
            "contains",
            "performance",
            "lighting",
            "sequence name",
        ]
        marker_hits = sum(1 for marker in english_markers if marker in lowered)
        english_words = re.findall(r"\b(the|and|with|this|that|each|array|object|contains|representing|following|settings|number|name)\b", lowered)
        czech_words = re.findall(r"\b(a|je|jsou|ktery|ktera|sekvence|cue|rizika|doporuceni|shrnuti|popis|hodnoty)\b", lowered)
        return marker_hits >= 2 or (len(english_words) >= 12 and len(english_words) > len(czech_words) * 2)

    def _prepend_czech_warning(self, analysis: str) -> str:
        return (
            "## Shrnuti\n"
            "Model i po opakovani cast odpovedi vratil anglicky. Nize je surovy vystup, ktery je vhodne brat s rezervou.\n\n"
            f"{analysis}"
        )


def cache_key(*parts: str) -> str:
    raw = "::".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
