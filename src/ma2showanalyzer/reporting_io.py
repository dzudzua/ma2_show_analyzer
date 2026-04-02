from __future__ import annotations

import base64
import csv
import json
import shutil
from pathlib import Path

from .models import ShowData


def copy_shared_assets(writer: object, output_dir: Path) -> None:
    logo_path = Path(__file__).resolve().parents[2] / "img" / "logo_graindma.png"
    if logo_path.exists():
        shutil.copy2(logo_path, output_dir / logo_path.name)
    assets_dir = Path(__file__).resolve().parents[2] / "templates" / "assets"
    if assets_dir.exists():
        for asset_path in assets_dir.iterdir():
            if asset_path.is_file():
                shutil.copy2(asset_path, output_dir / asset_path.name)


def write_json(writer: object, show: ShowData, output_dir: Path) -> None:
    payload = writer._rounded_summary(show)
    model_v2 = writer._show_model_v2(show)
    (output_dir / "summary.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "relationships.json").write_text(json.dumps(payload["relationships"], indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "fixtures.json").write_text(json.dumps(model_v2.get("fixtures", []), indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "patch_registry.json").write_text(json.dumps(model_v2.get("fixtures", []), indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "patch_summary.json").write_text(json.dumps(model_v2.get("patch_summary", {}), indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "fixture_types.json").write_text(json.dumps(model_v2.get("fixture_types", []), indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "normalized_references.json").write_text(json.dumps(model_v2.get("references", []), indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "object_index.json").write_text(json.dumps(model_v2.get("object_index", {}), indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "source_index.json").write_text(json.dumps(model_v2.get("source_index", {}), indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "warnings.json").write_text(json.dumps(model_v2.get("warnings", []), indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "patch_fixtures.json").write_text(json.dumps(payload["patch_fixtures"], indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "show_model_v2.json").write_text(json.dumps(model_v2, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(writer: object, show: ShowData, output_dir: Path) -> None:
    patch_index = writer._patch_index(show)
    model_v2 = writer._show_model_v2(show)
    writer._write_table(
        output_dir / "sequences.csv",
        [
            {
                "id": s.id,
                "number": s.number,
                "name": s.name,
                "cue_count": len(s.cues),
                "source_file": s.source_file,
                "is_main_cue_list": s.is_main_cue_list,
            }
            for s in show.sequences
        ],
    )
    writer._write_table(
        output_dir / "cues.csv",
        [
            {
                "id": c.id,
                "sequence_number": c.sequence_number,
                "cue_number": c.cue_number,
                "name": c.name,
                "fade": c.fade,
                "delay": c.delay,
                "trigger": c.trigger,
                "trigger_time": c.trigger_time,
                "down_delay": c.down_delay,
                "command": c.command,
                "part": c.part,
                "fixture_ids": " ".join(map(str, c.fixture_ids)),
                "channel_ids": " ".join(map(str, c.channel_ids)),
                "patch_target_keys": " | ".join(c.patch_target_keys),
                "fixture_details": " || ".join(writer._fixture_summary(c.fixture_ids, patch_index)),
                "references": " | ".join(c.references),
                "source_file": c.source_file,
                "is_main_cue_list": c.is_main_cue_list,
            }
            for s in show.sequences for c in s.cues
        ],
    )
    writer._write_table(
        output_dir / "presets.csv",
        [
            {
                "id": p.id,
                "preset_type": p.preset_type,
                "number": p.number,
                "name": p.name,
                "fixture_ids": " ".join(map(str, p.fixture_ids)),
                "channel_ids": " ".join(map(str, p.channel_ids)),
                "patch_target_keys": " | ".join(p.patch_target_keys),
                "fixture_details": " || ".join(writer._fixture_summary(p.fixture_ids, patch_index)),
                "references": " | ".join(p.references),
                "source_file": p.source_file,
            }
            for p in show.presets
        ],
    )
    writer._write_table(
        output_dir / "groups.csv",
        [
            {
                "id": g.id,
                "number": g.number,
                "name": g.name,
                "fixture_ids": " ".join(map(str, g.fixture_ids)),
                "channel_ids": " ".join(map(str, g.channel_ids)),
                "patch_target_keys": " | ".join(g.patch_target_keys),
                "fixture_details": " || ".join(writer._fixture_summary(g.fixture_ids, patch_index)),
                "fixture_count": len(g.fixture_ids),
                "source_file": g.source_file,
            }
            for g in show.groups
        ],
    )
    writer._write_table(
        output_dir / "effects.csv",
        [
            {
                "id": e.id,
                "number": e.number,
                "name": e.name,
                "fixture_ids": " ".join(map(str, e.fixture_ids)),
                "channel_ids": " ".join(map(str, e.channel_ids)),
                "patch_target_keys": " | ".join(e.patch_target_keys),
                "fixture_details": " || ".join(writer._fixture_summary(e.fixture_ids, patch_index)),
                "references": " | ".join(e.references),
                "source_file": e.source_file,
            }
            for e in show.effects
        ],
    )
    writer._write_table(output_dir / "relationships.csv", [r.to_dict() for r in show.relationships])
    writer._write_table(
        output_dir / "value_atoms.csv",
        [
            {
                "owner_type": owner_type,
                "owner_id": owner_id,
                "fixture_name": (patch_index.get(atom.fixture_id, {}).get("label") or patch_index.get(atom.fixture_id, {}).get("name")) if atom.fixture_id is not None else None,
                "fixture_type": patch_index.get(atom.fixture_id, {}).get("fixture_type") if atom.fixture_id is not None else None,
                "fixture_patch": patch_index.get(atom.fixture_id, {}).get("patch") if atom.fixture_id is not None else None,
                **{
                    **atom.to_dict(),
                    "raw_value": writer._format_attribute_raw_value(atom.raw_value),
                },
            }
            for s in show.sequences for c in s.cues
            for owner_type, owner_id, atom in [("cue", c.id, a) for a in c.values]
        ] + [
            {
                "owner_type": "preset",
                "owner_id": p.id,
                "fixture_name": (patch_index.get(atom.fixture_id, {}).get("label") or patch_index.get(atom.fixture_id, {}).get("name")) if atom.fixture_id is not None else None,
                "fixture_type": patch_index.get(atom.fixture_id, {}).get("fixture_type") if atom.fixture_id is not None else None,
                "fixture_patch": patch_index.get(atom.fixture_id, {}).get("patch") if atom.fixture_id is not None else None,
                **{
                    **atom.to_dict(),
                    "raw_value": writer._format_attribute_raw_value(atom.raw_value),
                },
            }
            for p in show.presets for atom in p.values
        ],
    )
    writer._write_table(
        output_dir / "fixture_usage.csv",
        [
            {
                **usage,
                "fixture_name": patch_index.get(int(usage["fixture_id"]), {}).get("label") or patch_index.get(int(usage["fixture_id"]), {}).get("name"),
                "fixture_type": patch_index.get(int(usage["fixture_id"]), {}).get("fixture_type"),
                "fixture_mode": patch_index.get(int(usage["fixture_id"]), {}).get("mode"),
                "fixture_patch": patch_index.get(int(usage["fixture_id"]), {}).get("patch"),
            }
            for usage in show.fixture_usage.values()
        ],
    )
    writer._write_table(output_dir / "patch_registry.csv", list(model_v2.get("fixtures", [])))
    writer._write_table(output_dir / "patch_fixtures.csv", [patch.to_dict() for patch in show.patch_fixtures])


def write_table(writer: object, path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    fieldset = set()
    for row in rows:
        for key in row.keys():
            if key not in fieldset:
                fieldset.add(key)
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv_writer = csv.DictWriter(handle, fieldnames=fieldnames)
        csv_writer.writeheader()
        for row in rows:
            csv_writer.writerow({key: writer._serialize_csv(value) for key, value in row.items()})


def serialize_csv(value: object) -> str | object:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value
