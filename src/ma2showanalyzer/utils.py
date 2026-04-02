from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, TypeVar
import xml.etree.ElementTree as ET


RE_INT = re.compile(r"\b\d+\b")
RE_DEC = re.compile(r"\b\d+(?:\.\d+)?\b")
RE_PRESET = re.compile(r"\bPreset\s*(\d{1,2})\.(\d+)\b", re.IGNORECASE)
RE_PRESET_COMPACT = re.compile(r"\b(\d{1,2})\.(\d+)\b")
RE_GROUP = re.compile(r"\bGroup\s*(\d+)\b", re.IGNORECASE)
RE_EFFECT = re.compile(r"\bEffect\s*(\d+)\b", re.IGNORECASE)
RE_SEQUENCE = re.compile(r"\bSequence\s*(\d+)\b", re.IGNORECASE)
RE_CUE = re.compile(r"\bCue\s*([\d\.]+)\b", re.IGNORECASE)
RE_FIXTURE = re.compile(r"\b(?:Fixture|FID|Channel|Ch)\s*#?\s*(\d+)\b", re.IGNORECASE)
RE_TRIGGER = re.compile(r"\b(go|follow|time|sound|bpm|manual)\b", re.IGNORECASE)


def strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def normalize_key(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def safe_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def unique_preserve(items: Iterable[T]) -> list[T]:
    seen: set[T] = set()
    out: list[T] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def xml_path_for_element(path_stack: list[str]) -> str:
    return "/".join(path_stack)


def parse_xml_file(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


def text_blob_from_element(elem: ET.Element) -> str:
    parts: list[str] = []
    for x in elem.iter():
        if x.text and x.text.strip():
            parts.append(x.text.strip())
        if x.tail and x.tail.strip():
            parts.append(x.tail.strip())
        for k, v in x.attrib.items():
            parts.append(f"{k}={v}")
    return " | ".join(parts)


def try_json_dump(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
T = TypeVar("T")

