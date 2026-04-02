from __future__ import annotations

import csv
import json
import base64
import shutil
from pathlib import Path
from collections import defaultdict
from collections import Counter

from .models import ShowData
from . import reporting_html, reporting_io


class ReportWriter:
    def __init__(self) -> None:
        self._model_v2_cache: dict[int, dict[str, object]] = {}
        self._logo_data_uri_cache: str | None = None

    def _show_model_v2(self, show: ShowData) -> dict[str, object]:
        cache_key = id(show)
        if cache_key not in self._model_v2_cache:
            self._model_v2_cache[cache_key] = show.to_model_v2()
        return self._model_v2_cache[cache_key]

    def _format_attribute_raw_value(self, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return f"{float(value):.2f}"
        text = str(value).strip()
        if not text:
            return text
        try:
            return f"{float(text):.2f}"
        except (TypeError, ValueError):
            return value

    def _logo_data_uri(self) -> str:
        if self._logo_data_uri_cache is not None:
            return self._logo_data_uri_cache
        logo_path = Path(__file__).resolve().parents[2] / "img" / "logo_graindma.png"
        if not logo_path.exists():
            self._logo_data_uri_cache = "logo_graindma.png"
            return self._logo_data_uri_cache
        encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
        self._logo_data_uri_cache = f"data:image/png;base64,{encoded}"
        return self._logo_data_uri_cache

    def _inline_branding_assets(self, html: str) -> str:
        return html.replace("logo_graindma.png", self._logo_data_uri())

    def _rounded_summary(self, show: ShowData) -> dict[str, object]:
        summary = show.to_dict()
        for sequence in summary.get("sequences", []):
            for cue in sequence.get("cues", []):
                for atom in cue.get("values", []):
                    atom["raw_value"] = self._format_attribute_raw_value(atom.get("raw_value"))
        for preset in summary.get("presets", []):
            for atom in preset.get("values", []):
                atom["raw_value"] = self._format_attribute_raw_value(atom.get("raw_value"))
        model_v2 = self._show_model_v2(show)
        summary["model_version"] = model_v2.get("model_version")
        summary["fixture_registry"] = model_v2.get("fixtures", [])
        summary["patch_summary"] = model_v2.get("patch_summary", {})
        summary["fixture_types"] = model_v2.get("fixture_types", [])
        summary["normalized_references"] = model_v2.get("references", [])
        summary["source_index"] = model_v2.get("source_index", {})
        summary["warnings"] = model_v2.get("warnings", [])
        return summary

    def _patch_index(self, show: ShowData) -> dict[int, dict]:
        model = self._show_model_v2(show)
        fixtures = model.get("fixtures", [])
        return {
            int(fixture["fixture_id"]): fixture
            for fixture in fixtures
            if fixture.get("fixture_id") is not None and fixture.get("patch_target_type") != "channel"
        }

    def _reference_index(self, show: ShowData) -> dict[tuple[str, str], list[dict[str, object]]]:
        model = self._show_model_v2(show)
        buckets: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
        for reference in model.get("references", []):
            owner_type = str(reference.get("owner_type") or "")
            owner_id = str(reference.get("owner_id") or "")
            if owner_type and owner_id:
                buckets[(owner_type, owner_id)].append(reference)
        return buckets

    def _fixture_summary(self, fixture_ids: list[int], patch_index: dict[int, dict]) -> list[str]:
        summaries: list[str] = []
        for fixture_id in fixture_ids:
            patch = patch_index.get(fixture_id)
            if not patch:
                summaries.append(str(fixture_id))
                continue
            name = patch.get("label") or patch.get("name") or f"Fixture {fixture_id}"
            fixture_type = patch.get("fixture_type") or ""
            patch_value = patch.get("patch") or ""
            parts = [str(fixture_id), name]
            if fixture_type:
                parts.append(fixture_type)
            if patch_value:
                parts.append(patch_value)
            summaries.append(" | ".join(parts))
        return summaries

    def write_all(self, show: ShowData, output_dir: Path, template_path: Path | None = None) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        self._copy_shared_assets(output_dir)
        audit = self._build_audit(show)
        self._write_json(show, output_dir)
        self._write_csv(show, output_dir)
        self._write_graph(show, output_dir)
        self._write_audit_reports(show, audit, output_dir)
        self._write_html(show, audit, output_dir, template_path)
        self._write_patch_html(show, output_dir)
        self._write_cue_list_html(show, output_dir)
        self._write_sequence_content_html(show, output_dir)
        self._write_sequence_inspector_html(show, output_dir)
        self._write_preset_logic_breaks_html(show, audit, output_dir)
        self._write_missing_preset_opportunities_html(show, audit, output_dir)
        self._write_cue_quality_html(show, audit, output_dir)
        self._write_warnings_html(show, output_dir)
        self._write_explorer_html(show, output_dir)
        self._write_topology_graphs_html(show, output_dir)
        self._write_explorer_d3_html(show, output_dir)
        self._write_explorer_radial_html(show, output_dir)
        self._write_explorer_sankey_html(show, output_dir)
        self._write_main_cue_reports(show, output_dir)
        self._write_overview(show, audit, output_dir)

    def _copy_shared_assets(self, output_dir: Path) -> None:
        reporting_io.copy_shared_assets(self, output_dir)

    def _write_json(self, show: ShowData, output_dir: Path) -> None:
        reporting_io.write_json(self, show, output_dir)

    def _build_graph(self, show: ShowData) -> dict[str, object]:
        patch_index = self._patch_index(show)
        reference_index = self._reference_index(show)
        nodes: dict[str, dict[str, object]] = {}
        links: list[dict[str, object]] = []

        def add_node(node_id: str, node_type: str, label: str, **extra: object) -> None:
            if node_id not in nodes:
                nodes[node_id] = {"id": node_id, "type": node_type, "label": label, **extra}

        def add_link(source: str, target: str, link_type: str, weight: int = 1, **extra: object) -> None:
            links.append({"source": source, "target": target, "type": link_type, "weight": weight, **extra})

        preset_index = {preset.number: preset for preset in show.presets if preset.number}
        group_index = {group.number: group for group in show.groups if group.number}
        main_cue_ids: list[str] = []
        cue_summaries: list[dict[str, object]] = []

        for fixture_id, patch in sorted(patch_index.items()):
            label = patch.get("display_name") or patch.get("label") or patch.get("name") or f"Fixture {fixture_id}"
            add_node(
                f"fixture:{fixture_id}",
                "fixture",
                label,
                fixture_id=fixture_id,
                fixture_type=patch.get("fixture_type"),
                patch=patch.get("patch"),
            )

        for preset in show.presets:
            add_node(
                f"preset:{preset.number or preset.id}",
                "preset",
                preset.name or f"Preset {preset.number or preset.id}",
                preset_number=preset.number,
                preset_type=preset.preset_type,
                preset_xml_index=(preset.metadata or {}).get("index"),
            )
            for fixture_id in preset.fixture_ids:
                patch = patch_index.get(fixture_id, {})
                add_node(
                    f"fixture:{fixture_id}",
                    "fixture",
                    patch.get("label") or patch.get("name") or f"Fixture {fixture_id}",
                    fixture_id=fixture_id,
                    fixture_type=patch.get("fixture_type"),
                    patch=patch.get("patch"),
                )
                add_link(
                    f"preset:{preset.number or preset.id}",
                    f"fixture:{fixture_id}",
                    "preset_fixture",
                    weight=1,
                )

        for group in show.groups:
            add_node(f"group:{group.number or group.id}", "group", group.name or f"Group {group.number or group.id}", group_number=group.number)
            for fixture_id in group.fixture_ids:
                patch = patch_index.get(fixture_id, {})
                add_node(
                    f"fixture:{fixture_id}",
                    "fixture",
                    patch.get("label") or patch.get("name") or f"Fixture {fixture_id}",
                    fixture_id=fixture_id,
                    fixture_type=patch.get("fixture_type"),
                    patch=patch.get("patch"),
                )
                add_link(f"group:{group.number or group.id}", f"fixture:{fixture_id}", "group_fixture", weight=1)

        for sequence in show.sequences:
            for cue in sequence.cues:
                cue_id = f"cue:{cue.sequence_number}:{cue.cue_number}"
                add_node(
                    cue_id,
                    "cue",
                    cue.name or f"Cue {cue.cue_number}",
                    cue_number=cue.cue_number,
                    sequence_number=cue.sequence_number,
                    fade=cue.fade,
                    delay=cue.delay,
                    trigger=cue.trigger,
                    trigger_time=cue.trigger_time,
                    is_main=cue.is_main_cue_list,
                )
                if cue.is_main_cue_list:
                    main_cue_ids.append(cue_id)

                hard_by_fixture: dict[int, list[str]] = defaultdict(list)
                preset_targets: set[str] = set()
                group_targets: set[str] = set()
                cue_refs = reference_index.get(("cue", cue.id), [])

                for atom in cue.values:
                    if atom.value_type == "hard" and atom.fixture_id is not None and not self._is_dimmer_family(atom.attribute):
                        if atom.attribute and atom.attribute not in hard_by_fixture[atom.fixture_id]:
                            hard_by_fixture[atom.fixture_id].append(atom.attribute)
                for ref in cue_refs:
                    target = str(ref.get("target") or "")
                    kind = str(ref.get("kind") or "")
                    if target.startswith("preset:") or kind == "preset_ref":
                        preset_targets.add(target.split(":", 1)[1] if ":" in target else target)
                    elif target.startswith("group:") or kind == "group_ref":
                        group_targets.add(target.split(":", 1)[1] if ":" in target else target)

                for fixture_id, attributes in hard_by_fixture.items():
                    patch = patch_index.get(fixture_id, {})
                    add_node(
                        f"fixture:{fixture_id}",
                        "fixture",
                        patch.get("label") or patch.get("name") or f"Fixture {fixture_id}",
                        fixture_id=fixture_id,
                        fixture_type=patch.get("fixture_type"),
                        patch=patch.get("patch"),
                    )
                    add_link(
                        cue_id,
                        f"fixture:{fixture_id}",
                        "cue_fixture_hard",
                        weight=len(attributes),
                        attributes=attributes,
                    )

                for preset_number in sorted(preset_targets):
                    preset = preset_index.get(preset_number)
                    add_node(
                        f"preset:{preset_number}",
                        "preset",
                        (preset.name if preset else None) or f"Preset {preset_number}",
                        preset_number=preset_number,
                        preset_type=(preset.preset_type if preset else None),
                        preset_xml_index=((preset.metadata or {}).get("index") if preset else None),
                    )
                    add_link(cue_id, f"preset:{preset_number}", "cue_preset", weight=1)

                for group_number in sorted(group_targets):
                    group = group_index.get(group_number)
                    add_node(
                        f"group:{group_number}",
                        "group",
                        (group.name if group else None) or f"Group {group_number}",
                        group_number=group_number,
                    )
                    add_link(cue_id, f"group:{group_number}", "cue_group", weight=1)

                cue_summaries.append(
                    {
                        "id": cue_id,
                        "sequence_number": cue.sequence_number,
                        "cue_number": cue.cue_number,
                        "name": cue.name,
                        "fade": cue.fade,
                        "delay": cue.delay,
                        "trigger": cue.trigger,
                        "trigger_time": cue.trigger_time,
                        "is_main": cue.is_main_cue_list,
                        "hard_fixture_count": len(hard_by_fixture),
                        "hard_value_count": sum(len(attributes) for attributes in hard_by_fixture.values()),
                        "preset_count": len(preset_targets),
                        "group_count": len(group_targets),
                    }
                )

        return {
            "nodes": list(nodes.values()),
            "links": links,
            "main_cue_ids": main_cue_ids,
            "cue_summaries": cue_summaries,
        }

    def _write_graph(self, show: ShowData, output_dir: Path) -> None:
        graph = self._build_graph(show)
        (output_dir / "graph.json").write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")

    def _write_csv(self, show: ShowData, output_dir: Path) -> None:
        reporting_io.write_csv(self, show, output_dir)

    def _write_table(self, path: Path, rows: list[dict]) -> None:
        reporting_io.write_table(self, path, rows)

    def _serialize_csv(self, value: object) -> str | object:
        return reporting_io.serialize_csv(value)

    def _write_html(self, show: ShowData, audit: dict[str, object], output_dir: Path, template_path: Path | None) -> None:
        reporting_html.write_dashboard_html(self, show, audit, output_dir, template_path)

    def _write_explorer_html(self, show: ShowData, output_dir: Path) -> None:
        reporting_html.write_explorer_html(self, show, output_dir)

    def _write_topology_graphs_html(self, show: ShowData, output_dir: Path) -> None:
        reporting_html.write_topology_graphs_html(self, show, output_dir)

    def _write_patch_html(self, show: ShowData, output_dir: Path) -> None:
        reporting_html.write_patch_html(self, show, output_dir)

    def _write_cue_list_html(self, show: ShowData, output_dir: Path) -> None:
        reporting_html.write_cue_list_html(self, show, output_dir)

    def _write_sequence_content_html(self, show: ShowData, output_dir: Path) -> None:
        reporting_html.write_sequence_content_html(self, show, output_dir)

    def _write_sequence_inspector_html(self, show: ShowData, output_dir: Path) -> None:
        reporting_html.write_sequence_inspector_html(self, show, output_dir)

    def _write_preset_logic_breaks_html(self, show: ShowData, audit: dict[str, object], output_dir: Path) -> None:
        reporting_html.write_preset_logic_breaks_html(self, show, audit, output_dir)

    def _write_missing_preset_opportunities_html(self, show: ShowData, audit: dict[str, object], output_dir: Path) -> None:
        reporting_html.write_missing_preset_opportunities_html(self, show, audit, output_dir)

    def _write_warnings_html(self, show: ShowData, output_dir: Path) -> None:
        reporting_html.write_warnings_html(self, show, output_dir)

    def _write_cue_quality_html(self, show: ShowData, audit: dict[str, object], output_dir: Path) -> None:
        reporting_html.write_cue_quality_html(self, show, audit, output_dir)

    def _write_explorer_d3_html(self, show: ShowData, output_dir: Path) -> None:
        reporting_html.write_explorer_d3_html(self, show, output_dir)

    def _write_explorer_radial_html(self, show: ShowData, output_dir: Path) -> None:
        reporting_html.write_explorer_radial_html(self, show, output_dir)

    def _write_explorer_sankey_html(self, show: ShowData, output_dir: Path) -> None:
        reporting_html.write_explorer_sankey_html(self, show, output_dir)

    def _write_main_cue_reports(self, show: ShowData, output_dir: Path) -> None:
        patch_index = self._patch_index(show)
        main_sequences = [sequence for sequence in show.sequences if sequence.is_main_cue_list]
        cue_rows: list[dict[str, object]] = []
        atom_rows: list[dict[str, object]] = []
        sequence_content_rows: list[dict[str, object]] = []
        preset_index = {preset.number: preset for preset in show.presets if preset.number}

        for sequence in main_sequences:
            for cue in sequence.cues:
                hard_atoms = [atom for atom in cue.values if atom.value_type == "hard" and not self._is_dimmer_family(atom.attribute)]
                dimmer_atoms = [atom for atom in cue.values if atom.value_type == "hard" and self._is_dimmer_family(atom.attribute)]
                preset_refs = [atom.reference_target for atom in cue.values if atom.value_type == "preset_ref" and atom.reference_target]
                effect_refs = [atom.reference_target for atom in cue.values if atom.value_type == "effect_ref" and atom.reference_target]
                group_refs = [atom.reference_target for atom in cue.values if atom.value_type == "group_ref" and atom.reference_target]

                cue_rows.append(
                    {
                        "sequence_number": cue.sequence_number,
                        "sequence_name": sequence.name,
                        "cue_number": cue.cue_number,
                        "cue_name": cue.name,
                        "trigger": cue.trigger,
                        "trigger_time": cue.trigger_time,
                        "fade": cue.fade,
                        "delay": cue.delay,
                        "down_delay": cue.down_delay,
                        "command": cue.command,
                        "fixture_ids": cue.fixture_ids,
                        "fixture_details": self._fixture_summary(cue.fixture_ids, patch_index),
                        "references": cue.references,
                        "preset_refs": sorted(set(preset_refs)),
                        "effect_refs": sorted(set(effect_refs)),
                        "group_refs": sorted(set(group_refs)),
                        "dimmer_value_count": len(dimmer_atoms),
                        "hard_value_count": len(hard_atoms),
                        "hard_value_attributes": sorted({atom.attribute for atom in hard_atoms if atom.attribute}),
                        "hard_value_preview": [
                            {
                                "attribute": atom.attribute,
                                "raw_value": self._format_attribute_raw_value(atom.raw_value),
                                "fixture_id": atom.fixture_id,
                            }
                            for atom in hard_atoms[:20]
                        ],
                        "source_file": cue.source_file,
                    }
                )

                for atom in cue.values:
                    atom_rows.append(
                        {
                            "sequence_number": cue.sequence_number,
                            "sequence_name": sequence.name,
                            "cue_number": cue.cue_number,
                            "cue_name": cue.name,
                            "attribute": atom.attribute,
                            "raw_value": self._format_attribute_raw_value(atom.raw_value),
                            "value_type": atom.value_type,
                            "fixture_id": atom.fixture_id,
                            "fixture_name": (patch_index.get(atom.fixture_id, {}).get("label") or patch_index.get(atom.fixture_id, {}).get("name")) if atom.fixture_id is not None else None,
                            "fixture_type": patch_index.get(atom.fixture_id, {}).get("fixture_type") if atom.fixture_id is not None else None,
                            "fixture_patch": patch_index.get(atom.fixture_id, {}).get("patch") if atom.fixture_id is not None else None,
                            "reference_target": atom.reference_target,
                            "flags": atom.flags,
                            "source_path": atom.source_path,
                            "is_hard_value": atom.value_type == "hard" and not self._is_dimmer_family(atom.attribute),
                            "is_dimmer_value": atom.value_type == "hard" and self._is_dimmer_family(atom.attribute),
                            "source_file": cue.source_file,
                        }
                    )

                sequence_content_rows.extend(
                    self._build_sequence_content_rows(
                        sequence_number=cue.sequence_number,
                        sequence_name=sequence.name,
                        cue_number=cue.cue_number,
                        cue_name=cue.name,
                        cue=cue,
                        patch_index=patch_index,
                        preset_index=preset_index,
                    )
                )

        self._write_table(output_dir / "main_cue_analysis.csv", cue_rows)
        self._write_table(output_dir / "main_cue_value_atoms.csv", atom_rows)
        self._write_table(output_dir / "sequence_content.csv", sequence_content_rows)

        summary = {
            "main_sequence_numbers": show.main_sequence_numbers,
            "main_sequence_count": len(main_sequences),
            "cue_count": len(cue_rows),
            "patch_fixture_count": len(show.patch_fixtures),
            "dimmer_value_atom_count": sum(1 for row in atom_rows if row["is_dimmer_value"]),
            "hard_value_atom_count": sum(1 for row in atom_rows if row["is_hard_value"]),
            "preset_ref_atom_count": sum(1 for row in atom_rows if row["value_type"] == "preset_ref"),
            "effect_ref_atom_count": sum(1 for row in atom_rows if row["value_type"] == "effect_ref"),
            "group_ref_atom_count": sum(1 for row in atom_rows if row["value_type"] == "group_ref"),
            "sequence_content_rows": sequence_content_rows,
            "cues": cue_rows,
        }
        (output_dir / "main_cue_analysis.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    def _build_sequence_content_rows(
        self,
        sequence_number: str | None,
        sequence_name: str | None,
        cue_number: str | None,
        cue_name: str | None,
        cue,
        patch_index: dict[int, dict],
        preset_index: dict[str, object],
    ) -> list[dict[str, object]]:
        families = ("Dimmer", "Position", "Gobo", "Color", "Beam", "Focus", "Control")
        fixture_map: dict[int, dict[str, object]] = {}

        def ensure_fixture(fixture_id: int) -> dict[str, object]:
            if fixture_id not in fixture_map:
                patch = patch_index.get(fixture_id, {})
                fixture_map[fixture_id] = {
                    "fixture_id": fixture_id,
                    "fixture_name": patch.get("label") or patch.get("name"),
                    "fixture_type": patch.get("fixture_type"),
                    "fixture_patch": patch.get("patch"),
                    "preset_refs": set(),
                    "dimmer_value_count": 0,
                    "hard_value_count": 0,
                    "preset_value_count": 0,
                    **{family.lower(): [] for family in families},
                }
            return fixture_map[fixture_id]

        for fixture_id in cue.fixture_ids:
            ensure_fixture(fixture_id)

        for atom in cue.values:
            if atom.fixture_id is None:
                continue
            row = ensure_fixture(atom.fixture_id)
            family = self._attribute_family(atom.attribute).lower()
            if family not in row:
                family = "control"
            if atom.value_type == "hard":
                if self._is_dimmer_family(atom.attribute):
                    row[family].append(f"D {atom.attribute or '?'}={self._format_attribute_raw_value(atom.raw_value)}")
                    row["dimmer_value_count"] += 1
                else:
                    row[family].append(f"H {atom.attribute or '?'}={self._format_attribute_raw_value(atom.raw_value)}")
                    row["hard_value_count"] += 1
            elif atom.value_type == "preset_ref" and atom.reference_target:
                row["preset_refs"].add(atom.reference_target.split(":", 1)[1])

        cue_preset_numbers = sorted({
            ref.split(":", 1)[1]
            for ref in cue.references
            if ref.startswith("preset:")
        } | {
            atom.reference_target.split(":", 1)[1]
            for atom in cue.values
            if atom.value_type == "preset_ref" and atom.reference_target
        })

        for preset_number in cue_preset_numbers:
            preset = preset_index.get(preset_number)
            if not preset:
                continue
            for atom in preset.values:
                if atom.fixture_id is None:
                    continue
                row = ensure_fixture(atom.fixture_id)
                family = self._attribute_family(atom.attribute).lower()
                if family not in row:
                    family = "control"
                row[family].append(f"P{preset_number} {atom.attribute or '?'}={self._format_attribute_raw_value(atom.raw_value)}")
                row["preset_refs"].add(preset_number)
                row["preset_value_count"] += 1

        rows: list[dict[str, object]] = []
        for fixture_id in sorted(fixture_map):
            row = fixture_map[fixture_id]
            rows.append(
                {
                    "sequence_number": sequence_number,
                    "sequence_name": sequence_name,
                    "cue_number": cue_number,
                    "cue_name": cue_name,
                    "fixture_id": fixture_id,
                    "fixture_name": row["fixture_name"],
                    "fixture_type": row["fixture_type"],
                    "fixture_patch": row["fixture_patch"],
                    "dimmer": row["dimmer"],
                    "position": row["position"],
                    "gobo": row["gobo"],
                    "color": row["color"],
                    "beam": row["beam"],
                    "focus": row["focus"],
                    "control": row["control"],
                    "preset_refs": sorted(row["preset_refs"]),
                    "dimmer_value_count": row["dimmer_value_count"],
                    "hard_value_count": row["hard_value_count"],
                    "preset_value_count": row["preset_value_count"],
                }
            )
        return rows

    def _write_overview(self, show: ShowData, audit: dict[str, object], output_dir: Path) -> None:
        patch_index = self._patch_index(show)
        main_sequences = [sequence for sequence in show.sequences if sequence.is_main_cue_list]
        main_cues = [cue for sequence in main_sequences for cue in sequence.cues]
        top_cues = sorted(main_cues, key=lambda cue: len([atom for atom in cue.values if atom.value_type == "hard" and not self._is_dimmer_family(atom.attribute)]), reverse=True)[:10]
        top_fixtures = sorted(show.fixture_usage.values(), key=lambda usage: int(usage.get("cue_count", 0)), reverse=True)[:10]
        unmapped_fixtures = sorted(fid for fid in show.fixture_usage.keys() if fid not in patch_index)
        preset_heatmap = audit.get("preset_heatmap", [])
        fixture_coverage = audit.get("fixture_coverage", [])
        risk_hotspots = audit.get("risk_hotspots", [])
        consistency_issues = audit.get("consistency_issues", [])
        cue_quality = audit.get("cue_quality", [])
        worst_blocks = audit.get("worst_blocks", [])
        fixture_inconsistency = audit.get("fixture_inconsistency", [])
        repeated_hard_values = audit.get("repeated_hard_values", [])
        dead_objects = [row for row in audit.get("object_liveness", []) if row.get("status") == "dead"]
        model_warnings = self._show_model_v2(show).get("warnings", [])

        lines = [
            "# grandMA2 Show Analysis",
            "",
            "## Summary",
            f"- Main sequences: {len(main_sequences)}",
            f"- Main cue count: {len(main_cues)}",
            f"- Presets loaded: {len(show.presets)}",
            f"- Groups loaded: {len(show.groups)}",
            f"- Effects loaded: {len(show.effects)}",
              f"- Patch fixtures loaded: {len(show.patch_fixtures)}",
              f"- Used fixtures total: {len(show.fixture_usage)}",
              f"- Used fixtures without patch mapping: {len(unmapped_fixtures)}",
              "- Unified model export: `show_model_v2.json`",
              f"- Validation warnings: {len(model_warnings)}",
              "",
              "## Top cues by hard values",
          ]

        for cue in top_cues:
            hard_atoms = [atom for atom in cue.values if atom.value_type == "hard" and not self._is_dimmer_family(atom.attribute)]
            dimmer_atoms = [atom for atom in cue.values if atom.value_type == "hard" and self._is_dimmer_family(atom.attribute)]
            lines.append(
                f"- Cue {cue.cue_number} `{cue.name}`: H={len(hard_atoms)}, D={len(dimmer_atoms)}, fixtures={len(cue.fixture_ids)}, fade={cue.fade or '-'}, trigger={cue.trigger or '-'}"
            )

        lines.extend(["", "## Top fixtures by cue usage"])
        for usage in top_fixtures:
            fixture_id = int(usage["fixture_id"])
            patch = patch_index.get(fixture_id, {})
            label = patch.get("label") or patch.get("name") or str(fixture_id)
            fixture_type = patch.get("fixture_type") or "-"
            patch_addr = patch.get("patch") or "-"
            lines.append(
                f"- Fixture {fixture_id} `{label}`: type={fixture_type}, patch={patch_addr}, cues={usage.get('cue_count', 0)}, H={usage.get('hard_value_atoms', 0)}, D={usage.get('dimmer_value_atoms', 0)}"
            )

        if preset_heatmap:
            lines.extend(["", "## Hottest presets"])
            for row in preset_heatmap[:10]:
                lines.append(
                    f"- Preset {row.get('preset_number') or '?'} `{row.get('preset_name') or ''}`: cues={row.get('cue_count', 0)}, sequences={row.get('sequence_count', 0)}, fixtures={row.get('fixture_count', 0)}, status={row.get('usage_status')}"
                )

        if fixture_coverage:
            lines.extend(["", "## Fixture coverage risks"])
            for row in [r for r in fixture_coverage if r.get("orphan_patch") or r.get("is_sparse")][:10]:
                lines.append(
                    f"- Fixture {row.get('fixture_id')} `{row.get('fixture_name') or ''}`: type={row.get('fixture_type') or '-'}, cues={row.get('cue_count', 0)}, presets={row.get('preset_count', 0)}, orphan_patch={row.get('orphan_patch')}"
                )

        if consistency_issues:
            lines.extend(["", "## Consistency issues"])
            for row in consistency_issues[:10]:
                lines.append(
                    f"- {row.get('issue_type')}: {row.get('subject')} | severity={row.get('severity')} | {row.get('details')}"
                )

        if risk_hotspots:
            lines.extend(["", "## Risk hotspots"])
            for row in risk_hotspots[:10]:
                lines.append(
                    f"- {row.get('subject')}: score={row.get('risk_score')} | {row.get('details')}"
                )

        if cue_quality:
            lines.extend(["", "## Worst cues"])
            for row in list(cue_quality)[:10]:
                lines.append(
                    f"- Seq {row.get('sequence_number')} Cue {row.get('cue_number')} `{row.get('cue_name') or ''}`: score={row.get('quality_risk_score')} | {row.get('reasons_text')}"
                )

        if worst_blocks:
            lines.extend(["", "## Worst blocks"])
            for row in list(worst_blocks)[:8]:
                lines.append(
                    f"- Seq {row.get('sequence_number')} cues {row.get('cue_range')}: avg_score={row.get('average_score')} | worst={row.get('worst_cue_score')} | {row.get('summary')}"
                )

        if fixture_inconsistency:
            lines.extend(["", "## Fixture inconsistency"])
            for row in list(fixture_inconsistency)[:10]:
                lines.append(
                    f"- Fixture {row.get('fixture_id')} `{row.get('fixture_name') or ''}` / {row.get('feature_group')}: hard={row.get('hard_cue_count')}, preset={row.get('preset_cue_count')} | {row.get('details')}"
                )

        if repeated_hard_values:
            lines.extend(["", "## Repeated hard values"])
            for row in list(repeated_hard_values)[:10]:
                lines.append(
                    f"- Fixture {row.get('fixture_id')} {row.get('attribute')}={row.get('raw_value')}: cues={row.get('cue_count')} | {row.get('cue_list_preview')}"
                )

        if dead_objects:
            lines.extend(["", "## Dead objects"])
            for row in dead_objects[:10]:
                lines.append(f"- {row.get('object_type')} {row.get('object_number')}: {row.get('object_name') or '-'}")

        if model_warnings:
            severity_counter = Counter(str(row.get("severity", "low")) for row in model_warnings)
            kind_counter = Counter(str(row.get("kind", "warning")) for row in model_warnings)
            lines.extend(["", "## Validation warnings"])
            lines.append(
                f"- Severity breakdown: high={severity_counter.get('high', 0)}, medium={severity_counter.get('medium', 0)}, low={severity_counter.get('low', 0)}"
            )
            top_kinds = ", ".join(f"{kind}={count}" for kind, count in kind_counter.most_common(8))
            if top_kinds:
                lines.append(f"- Top kinds: {top_kinds}")
            for row in model_warnings[:15]:
                lines.append(
                    f"- {row.get('severity', 'info')}: {row.get('kind')} | {row.get('subject')} | {row.get('details')}"
                )

        if unmapped_fixtures:
            preview = ", ".join(str(fid) for fid in unmapped_fixtures[:25])
            lines.extend([
                "",
                "## Fixtures used without patch metadata",
                f"- {preview}" + (" ..." if len(unmapped_fixtures) > 25 else ""),
            ])

        (output_dir / "analysis_overview.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _build_audit(self, show: ShowData) -> dict[str, object]:
        patch_index = self._patch_index(show)
        reference_index = self._reference_index(show)
        cue_dependency_map: list[dict[str, object]] = []
        preset_usage_map: dict[str, dict[str, set[str]]] = defaultdict(lambda: {"cues": set(), "sequences": set(), "main_cues": set()})
        group_usage_map: dict[str, dict[str, set[str]]] = defaultdict(lambda: {"cues": set(), "sequences": set()})
        effect_usage_map: dict[str, dict[str, set[str]]] = defaultdict(lambda: {"cues": set(), "sequences": set()})
        fixture_attribute_usage: dict[int, Counter[str]] = defaultdict(Counter)
        fixture_feature_usage: dict[int, Counter[str]] = defaultdict(Counter)
        fixture_hard_vs_ref: dict[int, Counter[str]] = defaultdict(Counter)
        fixture_family_modes_global: dict[int, dict[str, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
        fixture_type_attribute_modes: dict[tuple[str, str], dict[str, set[str] | int]] = defaultdict(lambda: {
            "hard_atoms": 0,
            "preset_refs": 0,
            "fixtures": set(),
            "cues": set(),
        })
        repeated_hard_tracker: dict[tuple[int, str, str], dict[str, object]] = {}
        preset_signature_map: dict[tuple[tuple[object, ...], ...], list[dict[str, str | None]]] = defaultdict(list)
        preset_fixture_types: dict[str, set[str]] = defaultdict(set)
        preset_names_by_type: dict[str, set[str]] = defaultdict(set)
        fixture_type_preset_names: dict[tuple[str, str], set[str]] = defaultdict(set)

        preset_index = {preset.number: preset for preset in show.presets if preset.number}
        group_index = {group.number: group for group in show.groups if group.number}
        effect_index = {effect.number: effect for effect in show.effects if effect.number}

        for preset in show.presets:
            fixture_types = {
                patch_index.get(fixture_id, {}).get("fixture_type")
                for fixture_id in preset.fixture_ids
                if patch_index.get(fixture_id, {}).get("fixture_type")
            }
            if preset.preset_type:
                preset_names_by_type[preset.preset_type].add((preset.name or "").strip() or f"Preset {preset.number}")
            for fixture_type in fixture_types:
                if preset.preset_type:
                    fixture_type_preset_names[(fixture_type, preset.preset_type)].add((preset.name or "").strip() or f"Preset {preset.number}")
                preset_fixture_types[preset.number or preset.id].add(fixture_type)

            normalized_atoms = sorted(
                (
                    atom.fixture_id or 0,
                    atom.attribute or "",
                    atom.raw_value or "",
                    atom.value_type,
                    atom.reference_target or "",
                )
                for atom in preset.values
            )
            if normalized_atoms:
                preset_signature_map[tuple(normalized_atoms)].append(
                    {
                        "preset_number": preset.number,
                        "preset_name": preset.name,
                        "preset_type": preset.preset_type,
                    }
                )

            for atom in preset.values:
                if atom.fixture_id is not None and atom.attribute:
                    fixture_attribute_usage[atom.fixture_id][atom.attribute] += 1
                    feature_group = self._attribute_family(atom.attribute)
                    fixture_feature_usage[atom.fixture_id][feature_group] += 1

        for sequence in show.sequences:
            for cue_index, cue in enumerate(sequence.cues, start=1):
                cue_id = cue.id
                fixture_to_attrs: dict[int, set[str]] = defaultdict(set)
                fixture_to_hard_attrs: dict[int, set[str]] = defaultdict(set)
                fixture_family_modes: dict[int, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
                preset_targets: set[str] = set()
                group_targets: set[str] = set()
                effect_targets: set[str] = set()
                feature_groups: set[str] = set()
                hard_value_count = 0
                dimmer_value_count = 0
                has_hard = False
                has_preset = False
                zero_like_count = 0

                for atom in cue.values:
                    if atom.fixture_id is not None and atom.attribute:
                        fixture_to_attrs[atom.fixture_id].add(atom.attribute)
                        fixture_attribute_usage[atom.fixture_id][atom.attribute] += 1
                        feature_group = self._attribute_family(atom.attribute)
                        feature_groups.add(feature_group)
                        fixture_feature_usage[atom.fixture_id][feature_group] += 1
                        fixture_family_modes[atom.fixture_id][feature_group].add("touch")
                        fixture_type = patch_index.get(atom.fixture_id, {}).get("fixture_type") or "Unknown"
                        bucket = fixture_type_attribute_modes[(fixture_type, atom.attribute)]
                        bucket["fixtures"].add(str(atom.fixture_id))
                        bucket["cues"].add(cue_id)
                    if atom.value_type == "hard":
                        hard_class = self._hard_class(atom.attribute)
                        if hard_class == "hard":
                            has_hard = True
                            hard_value_count += 1
                        else:
                            dimmer_value_count += 1
                        if atom.fixture_id is not None:
                            fixture_hard_vs_ref[atom.fixture_id][hard_class] += 1
                            if atom.attribute:
                                fixture_to_hard_attrs[atom.fixture_id].add(atom.attribute)
                                family = self._attribute_family(atom.attribute)
                                fixture_family_modes[atom.fixture_id][family].add(hard_class)
                                fixture_family_modes_global[atom.fixture_id][family][hard_class] += 1
                                fixture_type = patch_index.get(atom.fixture_id, {}).get("fixture_type") or "Unknown"
                                if hard_class == "hard":
                                    fixture_type_attribute_modes[(fixture_type, atom.attribute)]["hard_atoms"] += 1
                            if hard_class == "hard":
                                repeated_key = (
                                    int(atom.fixture_id),
                                    atom.attribute or "",
                                    str(self._format_attribute_raw_value(atom.raw_value) or ""),
                                )
                                tracker = repeated_hard_tracker.setdefault(
                                    repeated_key,
                                    {
                                        "fixture_id": int(atom.fixture_id),
                                        "attribute": atom.attribute or "",
                                        "raw_value": self._format_attribute_raw_value(atom.raw_value),
                                        "cue_ids": set(),
                                        "cue_labels": [],
                                        "sequence_numbers": set(),
                                    },
                                )
                                tracker["cue_ids"].add(cue_id)
                                tracker["sequence_numbers"].add(sequence.number or "")
                                tracker["cue_labels"].append(f"{sequence.number}.{cue.cue_number} {cue.name or ''}".strip())
                        if self._is_zero_like(atom.raw_value):
                            zero_like_count += 1
                    elif atom.value_type == "preset_ref" and atom.reference_target:
                        has_preset = True
                        target = atom.reference_target.split(":", 1)[1]
                        preset_targets.add(target)
                        if atom.fixture_id is not None:
                            fixture_hard_vs_ref[atom.fixture_id]["preset"] += 1
                            if atom.attribute:
                                family = self._attribute_family(atom.attribute)
                                fixture_family_modes[atom.fixture_id][family].add("preset")
                                fixture_family_modes_global[atom.fixture_id][family]["preset"] += 1
                                fixture_type = patch_index.get(atom.fixture_id, {}).get("fixture_type") or "Unknown"
                                fixture_type_attribute_modes[(fixture_type, atom.attribute)]["preset_refs"] += 1
                    elif atom.value_type == "group_ref" and atom.reference_target:
                        group_targets.add(atom.reference_target.split(":", 1)[1])
                    elif atom.value_type == "effect_ref" and atom.reference_target:
                        effect_targets.add(atom.reference_target.split(":", 1)[1])

                for ref in reference_index.get(("cue", cue.id), []):
                    target = str(ref.get("target") or "")
                    kind = str(ref.get("kind") or "")
                    if target.startswith("preset:") or kind == "preset_ref":
                        has_preset = True
                        preset_targets.add(target.split(":", 1)[1] if ":" in target else target)
                    elif target.startswith("group:") or kind == "group_ref":
                        group_targets.add(target.split(":", 1)[1] if ":" in target else target)
                    elif target.startswith("effect:") or kind == "effect_ref":
                        effect_targets.add(target.split(":", 1)[1] if ":" in target else target)

                for preset_number in preset_targets:
                    preset = preset_index.get(preset_number)
                    if not preset:
                        continue
                    for atom in preset.values:
                        if atom.fixture_id is None or not atom.attribute:
                            continue
                        family = self._attribute_family(atom.attribute)
                        fixture_family_modes[atom.fixture_id][family].add("preset")
                        fixture_family_modes_global[atom.fixture_id][family]["preset"] += 1

                mixed_fixture_count = 0
                mixed_family_count = 0
                family_mode_summary: dict[str, dict[str, list[int]]] = {}
                for fixture_id, family_modes in fixture_family_modes.items():
                    fixture_is_mixed = False
                    for family, modes in family_modes.items():
                        mode_set = {mode for mode in modes if mode in {"hard", "preset"}}
                        if not mode_set:
                            continue
                        bucket = family_mode_summary.setdefault(
                            family,
                            {"hard_fixtures": [], "preset_fixtures": [], "mixed_fixtures": []},
                        )
                        if "hard" in mode_set and fixture_id not in bucket["hard_fixtures"]:
                            bucket["hard_fixtures"].append(fixture_id)
                        if "preset" in mode_set and fixture_id not in bucket["preset_fixtures"]:
                            bucket["preset_fixtures"].append(fixture_id)
                        if {"hard", "preset"}.issubset(mode_set):
                            fixture_is_mixed = True
                            mixed_family_count += 1
                            if fixture_id not in bucket["mixed_fixtures"]:
                                bucket["mixed_fixtures"].append(fixture_id)
                    if fixture_is_mixed:
                        mixed_fixture_count += 1

                signature_pairs = sorted(
                    f"{fixture_id}:{attribute}"
                    for fixture_id, attributes in fixture_to_attrs.items()
                    for attribute in attributes
                )

                for preset_number in preset_targets:
                    preset_usage_map[preset_number]["cues"].add(cue_id)
                    preset_usage_map[preset_number]["sequences"].add(sequence.id)
                    if cue.is_main_cue_list:
                        preset_usage_map[preset_number]["main_cues"].add(cue_id)
                for group_number in group_targets:
                    group_usage_map[group_number]["cues"].add(cue_id)
                    group_usage_map[group_number]["sequences"].add(sequence.id)
                for effect_number in effect_targets:
                    effect_usage_map[effect_number]["cues"].add(cue_id)
                    effect_usage_map[effect_number]["sequences"].add(sequence.id)

                cue_dependency_map.append(
                    {
                        "cue_id": cue_id,
                        "sequence_id": sequence.id,
                        "sequence_number": sequence.number,
                        "sequence_name": sequence.name,
                        "cue_number": cue.cue_number,
                        "cue_name": cue.name,
                        "cue_position": cue_index,
                        "is_main_cue_list": cue.is_main_cue_list,
                        "fixture_count": len(cue.fixture_ids),
                        "fixtures": cue.fixture_ids,
                        "fixture_details": self._fixture_summary(cue.fixture_ids, patch_index),
                        "attribute_count": len({attribute for attributes in fixture_to_attrs.values() for attribute in attributes}),
                        "attributes": sorted({attribute for attributes in fixture_to_attrs.values() for attribute in attributes}),
                        "feature_group_count": len(feature_groups),
                        "feature_groups": sorted(feature_groups),
                        "hard_value_count": hard_value_count,
                        "dimmer_value_count": dimmer_value_count,
                        "hard_fixture_count": sum(1 for attributes in fixture_to_hard_attrs.values() if any(not self._is_dimmer_family(attribute) for attribute in attributes)),
                        "dimmer_fixture_count": sum(1 for attributes in fixture_to_hard_attrs.values() if any(self._is_dimmer_family(attribute) for attribute in attributes)),
                        "preset_ref_count": len(preset_targets),
                        "preset_refs": sorted(preset_targets),
                        "group_ref_count": len(group_targets),
                        "group_refs": sorted(group_targets),
                        "effect_ref_count": len(effect_targets),
                        "effect_refs": sorted(effect_targets),
                        "zero_like_count": zero_like_count,
                        "mixed_fixture_count": mixed_fixture_count,
                        "mixed_family_count": mixed_family_count,
                        "control_mode": self._control_mode(has_hard, has_preset),
                        "fixture_attribute_map": {str(fid): sorted(attributes) for fid, attributes in fixture_to_attrs.items()},
                        "fixture_hard_attribute_map": {str(fid): sorted(attribute for attribute in attributes if not self._is_dimmer_family(attribute)) for fid, attributes in fixture_to_hard_attrs.items()},
                        "fixture_dimmer_attribute_map": {str(fid): sorted(attribute for attribute in attributes if self._is_dimmer_family(attribute)) for fid, attributes in fixture_to_hard_attrs.items()},
                        "fixture_family_mode_map": {
                            str(fid): {family: sorted(mode for mode in modes if mode in {"hard", "dimmer", "preset"}) for family, modes in family_map.items()}
                            for fid, family_map in fixture_family_modes.items()
                        },
                        "family_mode_summary": {
                            family: {
                                "hard_fixtures": sorted(set(data["hard_fixtures"])),
                                "preset_fixtures": sorted(set(data["preset_fixtures"])),
                                "mixed_fixtures": sorted(set(data["mixed_fixtures"])),
                            }
                            for family, data in family_mode_summary.items()
                        },
                        "signature_pairs": signature_pairs,
                        "source_file": cue.source_file,
                    }
                )

        duplicate_groups = {
            signature: presets
            for signature, presets in preset_signature_map.items()
            if len(presets) > 1
        }

        preset_heatmap: list[dict[str, object]] = []
        for preset in show.presets:
            usage = preset_usage_map.get(preset.number or "", {"cues": set(), "sequences": set(), "main_cues": set()})
            duplicates = []
            normalized_atoms = tuple(sorted(
                (
                    atom.fixture_id or 0,
                    atom.attribute or "",
                    atom.raw_value or "",
                    atom.value_type,
                    atom.reference_target or "",
                )
                for atom in preset.values
            ))
            if normalized_atoms in duplicate_groups:
                duplicates = [
                    item["preset_number"]
                    for item in duplicate_groups[normalized_atoms]
                    if item["preset_number"] != preset.number
                ]
            cue_count = len(usage["cues"])
            usage_status = "unused"
            if cue_count == 1:
                usage_status = "single_cue"
            elif cue_count > 0:
                usage_status = "active"
            preset_heatmap.append(
                {
                    "preset_number": preset.number,
                    "preset_type": preset.preset_type,
                    "preset_name": preset.name,
                    "cue_count": cue_count,
                    "sequence_count": len(usage["sequences"]),
                    "main_cue_count": len(usage["main_cues"]),
                    "fixture_count": len(preset.fixture_ids),
                    "fixture_types": sorted(preset_fixture_types.get(preset.number or preset.id, set())),
                    "value_count": len(preset.values),
                    "usage_status": usage_status,
                    "is_unused": cue_count == 0,
                    "is_single_cue": cue_count == 1,
                    "duplicate_candidates": sorted(set(duplicates)),
                    "duplicate_candidate_count": len(set(duplicates)),
                    "source_file": preset.source_file,
                }
            )
        preset_heatmap.sort(key=lambda row: (-int(row["cue_count"]), -int(row["sequence_count"]), row.get("preset_number") or ""))

        all_fixture_ids = set(show.fixture_usage.keys()) | set(patch_index.keys())
        fixture_coverage: list[dict[str, object]] = []
        for fixture_id in sorted(all_fixture_ids):
            usage = show.fixture_usage.get(fixture_id, {})
            patch = patch_index.get(fixture_id, {})
            attribute_counts = fixture_attribute_usage.get(fixture_id, Counter())
            feature_counts = fixture_feature_usage.get(fixture_id, Counter())
            preset_types = sorted({
                preset.preset_type
                for preset in show.presets
                if fixture_id in preset.fixture_ids and preset.preset_type
            })
            fixture_coverage.append(
                {
                    "fixture_id": fixture_id,
                    "fixture_name": patch.get("label") or patch.get("name"),
                    "fixture_type": patch.get("fixture_type"),
                    "fixture_patch": patch.get("patch"),
                    "sequence_count": usage.get("sequence_count", 0),
                    "cue_count": usage.get("cue_count", 0),
                    "preset_count": usage.get("preset_count", 0),
                    "group_count": usage.get("group_count", 0),
                    "effect_count": usage.get("effect_count", 0),
                    "hard_value_atoms": usage.get("hard_value_atoms", 0),
                    "dimmer_value_atoms": fixture_hard_vs_ref.get(fixture_id, Counter()).get("dimmer", 0),
                    "preset_ref_atoms": usage.get("preset_ref_atoms", 0),
                    "group_ref_atoms": usage.get("group_ref_atoms", 0),
                    "effect_ref_atoms": usage.get("effect_ref_atoms", 0),
                    "preset_types_available": preset_types,
                    "top_attributes": [name for name, _count in attribute_counts.most_common(10)],
                    "attribute_frequency": dict(attribute_counts.most_common()),
                    "feature_group_frequency": dict(feature_counts.most_common()),
                    "orphan_patch": fixture_id in patch_index and fixture_id not in show.fixture_usage,
                    "is_sparse": int(usage.get("cue_count", 0)) <= 1 and int(usage.get("preset_count", 0)) <= 1,
                    "control_mode": self._fixture_control_mode(fixture_hard_vs_ref.get(fixture_id, Counter())),
                }
            )

        consistency_issues: list[dict[str, object]] = []
        for (fixture_type, attribute), data in fixture_type_attribute_modes.items():
            hard_atoms = int(data["hard_atoms"])
            preset_refs = int(data["preset_refs"])
            if hard_atoms and preset_refs:
                consistency_issues.append(
                    {
                        "issue_type": "mixed_control_mode",
                        "severity": "high" if hard_atoms >= 10 and preset_refs >= 3 else "medium",
                        "subject": f"{fixture_type} / {attribute}",
                        "details": f"hard_atoms={hard_atoms}, preset_refs={preset_refs}, fixtures={len(data['fixtures'])}, cues={len(data['cues'])}",
                    }
                )
        for (fixture_type, preset_type), names in fixture_type_preset_names.items():
            normalized_names = {self._normalize_name(name) for name in names if name}
            if len(normalized_names) > 3:
                consistency_issues.append(
                    {
                        "issue_type": "preset_name_variation",
                        "severity": "medium",
                        "subject": f"{fixture_type} / preset type {preset_type}",
                        "details": f"{len(names)} preset names: {', '.join(sorted(list(names))[:8])}",
                    }
                )
        for preset_type, names in preset_names_by_type.items():
            normalized_names = {self._normalize_name(name) for name in names if name}
            if len(normalized_names) > 8:
                consistency_issues.append(
                    {
                        "issue_type": "pool_name_entropy",
                        "severity": "low",
                        "subject": f"Preset type {preset_type}",
                        "details": f"{len(names)} distinct names in pool",
                    }
                )
        consistency_issues.sort(key=lambda row: ({"high": 0, "medium": 1, "low": 2}.get(str(row.get("severity")), 9), row.get("subject") or ""))

        risk_hotspots: list[dict[str, object]] = []
        for row in cue_dependency_map:
            risk_score = 0
            reasons: list[str] = []
            hard_value_count = int(row["hard_value_count"])
            dimmer_value_count = int(row.get("dimmer_value_count") or 0)
            feature_group_count = int(row["feature_group_count"])
            preset_ref_count = int(row["preset_ref_count"])
            if hard_value_count >= 30:
                risk_score += 4
                reasons.append(f"many hard values ({hard_value_count})")
            elif hard_value_count >= 15:
                risk_score += 2
                reasons.append(f"elevated hard values ({hard_value_count})")
            if feature_group_count >= 5:
                risk_score += 3
                reasons.append(f"touches many feature groups ({feature_group_count})")
            elif feature_group_count >= 3:
                risk_score += 1
                reasons.append(f"touches multiple feature groups ({feature_group_count})")
            if row["control_mode"] == "mixed":
                risk_score += 2
                reasons.append("mixed hard and preset control")
            if preset_ref_count >= 4:
                risk_score += 1
                reasons.append(f"depends on several presets ({preset_ref_count})")
            if dimmer_value_count >= 8:
                reasons.append(f"dimmer hard values present ({dimmer_value_count})")
            if risk_score:
                risk_hotspots.append(
                    {
                        "category": "cue",
                        "subject": f"Seq {row.get('sequence_number')} Cue {row.get('cue_number')} {row.get('cue_name') or ''}".strip(),
                        "risk_score": risk_score,
                        "details": "; ".join(reasons),
                    }
                )
        for row in preset_heatmap[:]:
            if int(row["cue_count"]) >= 15:
                risk_hotspots.append(
                    {
                        "category": "preset",
                        "subject": f"Preset {row.get('preset_number')} {row.get('preset_name') or ''}".strip(),
                        "risk_score": 3 if int(row["cue_count"]) < 30 else 5,
                        "details": f"critical dependency: used by {row.get('cue_count')} cues in {row.get('sequence_count')} sequences",
                    }
                )
            if row.get("is_unused"):
                risk_hotspots.append(
                    {
                        "category": "preset",
                        "subject": f"Preset {row.get('preset_number')} {row.get('preset_name') or ''}".strip(),
                        "risk_score": 1,
                        "details": "dead preset: loaded in pool but not referenced by any cue",
                    }
                )
        for row in fixture_coverage:
            if row.get("orphan_patch"):
                risk_hotspots.append(
                    {
                        "category": "fixture",
                        "subject": f"Fixture {row.get('fixture_id')} {row.get('fixture_name') or ''}".strip(),
                        "risk_score": 1,
                        "details": "patched fixture appears unused in analyzed show data",
                    }
                )
            elif row.get("control_mode") == "mixed":
                risk_hotspots.append(
                    {
                        "category": "fixture",
                        "subject": f"Fixture {row.get('fixture_id')} {row.get('fixture_name') or ''}".strip(),
                        "risk_score": 2,
                        "details": "fixture receives both hard values and preset-driven control",
                    }
                )
        risk_hotspots.sort(key=lambda row: (-int(row["risk_score"]), row.get("subject") or ""))

        cue_quality: list[dict[str, object]] = []
        grouped_rows: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in cue_dependency_map:
            grouped_rows[str(row.get("sequence_id") or row.get("sequence_number") or "")].append(row)

        for sequence_rows in grouped_rows.values():
            sequence_rows.sort(key=lambda row: int(row.get("cue_position") or 0))
            for idx, row in enumerate(sequence_rows):
                prev_row = sequence_rows[idx - 1] if idx > 0 else None
                next_row = sequence_rows[idx + 1] if idx + 1 < len(sequence_rows) else None
                local_rows = sequence_rows[max(0, idx - 3): min(len(sequence_rows), idx + 4)]
                local_avg_hard = self._avg(local_rows, "hard_value_count")
                local_avg_dimmer = self._avg(local_rows, "dimmer_value_count")
                local_avg_preset = self._avg(local_rows, "preset_ref_count")
                local_avg_zero = self._avg(local_rows, "zero_like_count")
                local_avg_mixed = self._avg(local_rows, "mixed_fixture_count")
                local_avg_feature_groups = self._avg(local_rows, "feature_group_count")
                prev_similarity = self._jaccard(set(row.get("signature_pairs") or []), set((prev_row or {}).get("signature_pairs") or []))
                next_similarity = self._jaccard(set(row.get("signature_pairs") or []), set((next_row or {}).get("signature_pairs") or []))
                local_similarity = round((prev_similarity + next_similarity) / 2, 3)
                fade_value = self._safe_float(row.get("fade"))
                delay_value = self._safe_float(row.get("delay"))
                local_fades = [self._safe_float(item.get("fade")) for item in local_rows]
                local_delays = [self._safe_float(item.get("delay")) for item in local_rows]
                local_fades = [value for value in local_fades if value is not None]
                local_delays = [value for value in local_delays if value is not None]
                local_avg_fade = sum(local_fades) / len(local_fades) if local_fades else 0.0
                local_avg_delay = sum(local_delays) / len(local_delays) if local_delays else 0.0

                score = 0
                reasons: list[str] = []
                hard_count = int(row.get("hard_value_count") or 0)
                dimmer_count = int(row.get("dimmer_value_count") or 0)
                value_count = max(
                    int(row.get("hard_value_count") or 0)
                    + int(row.get("preset_ref_count") or 0)
                    + int(row.get("effect_ref_count") or 0),
                    1,
                )
                hard_ratio = hard_count / value_count
                if hard_ratio >= 0.75 and hard_count >= 8:
                    score += 20
                    reasons.append(f"very hard-heavy cue ({hard_count} hard values)")
                elif hard_ratio >= 0.45 and hard_count >= 4:
                    score += 12
                    reasons.append(f"hard-heavy cue ({hard_count} hard values)")

                mixed_fixture_count = int(row.get("mixed_fixture_count") or 0)
                mixed_family_count = int(row.get("mixed_family_count") or 0)
                if mixed_family_count >= 3:
                    score += 20
                    reasons.append(f"mixed programming in {mixed_family_count} fixture/family pairs")
                elif mixed_fixture_count >= 1:
                    score += 12
                    reasons.append(f"mixed fixture control on {mixed_fixture_count} fixtures")

                if local_similarity <= 0.18 and len(sequence_rows) >= 3:
                    score += 15
                    reasons.append(f"low similarity to neighbouring cues ({local_similarity:.2f})")
                elif local_similarity <= 0.35 and len(sequence_rows) >= 3:
                    score += 8
                    reasons.append(f"noticeable local outlier ({local_similarity:.2f})")

                if hard_count > max(local_avg_hard * 2.1, local_avg_hard + 8):
                    score += 12
                    reasons.append(f"hard values spike vs local block ({hard_count} vs avg {local_avg_hard:.1f})")
                if int(row.get("zero_like_count") or 0) > max(local_avg_zero * 2.0, 6):
                    score += 10
                    reasons.append(f"many zero/reset-like values ({row.get('zero_like_count')})")
                if int(row.get("feature_group_count") or 0) > max(local_avg_feature_groups * 1.8, 5):
                    score += 8
                    reasons.append(f"touches unusually many feature groups ({row.get('feature_group_count')})")
                if int(row.get("effect_ref_count") or 0) >= 3:
                    score += 8
                    reasons.append(f"heavy effect dependency ({row.get('effect_ref_count')} effects)")
                if fade_value is not None and fade_value > max(local_avg_fade * 2.5, 10.0):
                    score += 10
                    reasons.append(f"unusual cue fade {fade_value:.2f}s")
                if delay_value is not None and delay_value > max(local_avg_delay * 2.5, 5.0):
                    score += 10
                    reasons.append(f"unusual cue delay {delay_value:.2f}s")
                if int(row.get("preset_ref_count") or 0) > max(local_avg_preset * 2.2, 6) and hard_count:
                    score += 5
                    reasons.append("many preset refs combined with hard edits")
                if int(row.get("mixed_fixture_count") or 0) > max(local_avg_mixed * 2.0, 2):
                    score += 6
                    reasons.append("more mixed fixtures than neighbouring cues")
                if dimmer_count > max(local_avg_dimmer * 2.5, 10) and not hard_count:
                    reasons.append(f"dimmer-heavy cue ({dimmer_count} D values)")

                severity = "low"
                if score >= 45:
                    severity = "high"
                elif score >= 22:
                    severity = "medium"

                cue_quality.append(
                    {
                        "cue_id": row.get("cue_id"),
                        "sequence_id": row.get("sequence_id"),
                        "sequence_number": row.get("sequence_number"),
                        "sequence_name": row.get("sequence_name"),
                        "cue_number": row.get("cue_number"),
                        "cue_name": row.get("cue_name"),
                        "cue_position": row.get("cue_position"),
                        "is_main_cue_list": row.get("is_main_cue_list"),
                        "fixture_count": row.get("fixture_count"),
                        "attribute_count": row.get("attribute_count"),
                        "feature_group_count": row.get("feature_group_count"),
                        "hard_value_count": hard_count,
                        "dimmer_value_count": dimmer_count,
                        "preset_ref_count": row.get("preset_ref_count"),
                        "group_ref_count": row.get("group_ref_count"),
                        "effect_ref_count": row.get("effect_ref_count"),
                        "zero_like_count": row.get("zero_like_count"),
                        "mixed_fixture_count": mixed_fixture_count,
                        "mixed_family_count": mixed_family_count,
                        "control_mode": row.get("control_mode"),
                        "fade": row.get("fade"),
                        "delay": row.get("delay"),
                        "trigger": row.get("trigger"),
                        "trigger_time": row.get("trigger_time"),
                        "down_delay": row.get("down_delay"),
                        "prev_similarity": round(prev_similarity, 3),
                        "next_similarity": round(next_similarity, 3),
                        "local_similarity": local_similarity,
                        "local_avg_hard": round(local_avg_hard, 2),
                        "local_avg_dimmer": round(local_avg_dimmer, 2),
                        "local_avg_preset": round(local_avg_preset, 2),
                        "local_avg_zero": round(local_avg_zero, 2),
                        "local_avg_feature_groups": round(local_avg_feature_groups, 2),
                        "quality_risk_score": score,
                        "severity": severity,
                        "reason_count": len(reasons),
                        "reasons": reasons,
                        "reasons_text": "; ".join(reasons) if reasons else "stable cue profile",
                        "source_file": row.get("source_file"),
                    }
                )

        cue_quality.sort(
            key=lambda row: (
                {"high": 0, "medium": 1, "low": 2}.get(str(row.get("severity")), 9),
                -int(row.get("quality_risk_score") or 0),
                str(row.get("sequence_number") or ""),
                str(row.get("cue_number") or ""),
            )
        )

        worst_blocks: list[dict[str, object]] = []
        quality_by_sequence: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in cue_quality:
            quality_by_sequence[str(row.get("sequence_id") or row.get("sequence_number") or "")].append(row)
        for sequence_rows in quality_by_sequence.values():
            sequence_rows.sort(key=lambda row: int(row.get("cue_position") or 0))
            if len(sequence_rows) < 3:
                continue
            block_size = 5
            for start in range(0, max(1, len(sequence_rows) - block_size + 1)):
                window = sequence_rows[start:start + block_size]
                if len(window) < 3:
                    continue
                avg_score = sum(int(item.get("quality_risk_score") or 0) for item in window) / len(window)
                avg_hard = sum(int(item.get("hard_value_count") or 0) for item in window) / len(window)
                avg_mixed = sum(int(item.get("mixed_fixture_count") or 0) for item in window) / len(window)
                avg_similarity = sum(float(item.get("local_similarity") or 0) for item in window) / len(window)
                high_count = sum(1 for item in window if item.get("severity") == "high")
                worst_score = max(int(item.get("quality_risk_score") or 0) for item in window)
                first = window[0]
                last = window[-1]
                worst_blocks.append(
                    {
                        "sequence_id": first.get("sequence_id"),
                        "sequence_number": first.get("sequence_number"),
                        "sequence_name": first.get("sequence_name"),
                        "cue_range": f"{first.get('cue_number')} - {last.get('cue_number')}",
                        "cue_count": len(window),
                        "average_score": round(avg_score, 2),
                        "worst_cue_score": worst_score,
                        "high_count": high_count,
                        "average_hard_values": round(avg_hard, 2),
                        "average_mixed_fixtures": round(avg_mixed, 2),
                        "average_similarity": round(avg_similarity, 3),
                        "summary": f"high cues={high_count}, avg hard={avg_hard:.1f}, avg similarity={avg_similarity:.2f}",
                    }
                )
        worst_blocks.sort(
            key=lambda row: (
                -float(row.get("average_score") or 0),
                -int(row.get("worst_cue_score") or 0),
                str(row.get("sequence_number") or ""),
            )
        )

        fixture_inconsistency: list[dict[str, object]] = []
        for fixture_id, families in fixture_family_modes_global.items():
            patch = patch_index.get(fixture_id, {})
            touching_rows = [row for row in cue_dependency_map if str(fixture_id) in (row.get("fixture_family_mode_map") or {})]
            for family, counter in families.items():
                hard_count = int(counter.get("hard", 0))
                preset_count = int(counter.get("preset", 0))
                if not hard_count or not preset_count:
                    continue
                touching_cues = []
                mixed_cues = 0
                for row in touching_rows:
                    family_map = ((row.get("fixture_family_mode_map") or {}).get(str(fixture_id)) or {})
                    modes = set(family_map.get(family) or [])
                    if not modes:
                        continue
                    touching_cues.append(row)
                    if {"hard", "preset"}.issubset(modes):
                        mixed_cues += 1
                fixture_inconsistency.append(
                    {
                        "fixture_id": fixture_id,
                        "fixture_name": patch.get("label") or patch.get("name"),
                        "fixture_type": patch.get("fixture_type"),
                        "fixture_patch": patch.get("patch"),
                        "feature_group": family,
                        "hard_cue_count": sum(
                            1
                            for row in touching_cues
                            if "hard" in set((((row.get("fixture_family_mode_map") or {}).get(str(fixture_id)) or {}).get(family) or []))
                        ),
                        "preset_cue_count": sum(
                            1
                            for row in touching_cues
                            if "preset" in set((((row.get("fixture_family_mode_map") or {}).get(str(fixture_id)) or {}).get(family) or []))
                        ),
                        "mixed_cue_count": mixed_cues,
                        "sequence_count": len({row.get("sequence_number") for row in touching_cues}),
                        "details": f"family uses both hard and preset control across {len(touching_cues)} cues",
                    }
                )
        fixture_inconsistency.sort(
            key=lambda row: (
                -int(row.get("mixed_cue_count") or 0),
                -int(row.get("hard_cue_count") or 0),
                int(row.get("fixture_id") or 0),
            )
        )

        repeated_hard_values: list[dict[str, object]] = []
        for tracker in repeated_hard_tracker.values():
            cue_ids = tracker.get("cue_ids") or set()
            if len(cue_ids) < 3:
                continue
            fixture_id = int(tracker["fixture_id"])
            patch = patch_index.get(fixture_id, {})
            labels = list(dict.fromkeys(tracker.get("cue_labels") or []))
            repeated_hard_values.append(
                {
                    "fixture_id": fixture_id,
                    "fixture_name": patch.get("label") or patch.get("name"),
                    "fixture_type": patch.get("fixture_type"),
                    "fixture_patch": patch.get("patch"),
                    "attribute": tracker.get("attribute"),
                    "raw_value": tracker.get("raw_value"),
                    "cue_count": len(cue_ids),
                    "sequence_count": len(tracker.get("sequence_numbers") or []),
                    "cue_list_preview": " | ".join(labels[:8]) + (" ..." if len(labels) > 8 else ""),
                    "details": "repeated hard value candidate for preset cleanup",
                }
            )
        repeated_hard_values.sort(
            key=lambda row: (
                -int(row.get("cue_count") or 0),
                int(row.get("fixture_id") or 0),
                str(row.get("attribute") or ""),
            )
        )

        control_balance: list[dict[str, object]] = []
        for row in cue_dependency_map:
            fixture_attribute_map = row.get("fixture_hard_attribute_map") or {}
            fixture_dimmer_map = row.get("fixture_dimmer_attribute_map") or {}
            preset_refs = list(row.get("preset_refs") or [])
            referenced_presets = [preset_index.get(number) for number in preset_refs if preset_index.get(number)]
            preset_fixture_ids = sorted({
                fixture_id
                for preset in referenced_presets
                for fixture_id in preset.fixture_ids
            })
            hard_fixture_ids = sorted(int(key) for key in fixture_attribute_map.keys() if str(key).isdigit())
            all_fixture_ids = sorted(set(hard_fixture_ids) | set(preset_fixture_ids))
            for fixture_id in all_fixture_ids:
                patch = patch_index.get(fixture_id, {})
                hard_attrs = sorted((fixture_attribute_map.get(str(fixture_id)) or []))
                matching_presets = []
                matching_types = set()
                for preset in referenced_presets:
                    preset_atoms = [atom for atom in preset.values if atom.fixture_id == fixture_id]
                    if not preset_atoms:
                        continue
                    matching_presets.append(preset.number or "")
                    if preset.preset_type:
                        matching_types.add(preset.preset_type)
                mode = self._control_mode(bool(hard_attrs), bool(matching_presets))
                control_balance.append(
                    {
                        "sequence_number": row.get("sequence_number"),
                        "cue_number": row.get("cue_number"),
                        "cue_name": row.get("cue_name"),
                        "fixture_id": fixture_id,
                        "fixture_name": patch.get("label") or patch.get("name"),
                        "fixture_type": patch.get("fixture_type"),
                        "fixture_patch": patch.get("patch"),
                        "control_mode": mode,
                        "hard_attribute_count": len(hard_attrs),
                        "hard_attributes": hard_attrs,
                        "dimmer_attribute_count": len(fixture_dimmer_map.get(str(fixture_id)) or []),
                        "dimmer_attributes": sorted(fixture_dimmer_map.get(str(fixture_id)) or []),
                        "preset_ref_count": len(matching_presets),
                        "preset_refs": matching_presets,
                        "preset_types": sorted(matching_types),
                    }
                )
        control_balance.sort(
            key=lambda row: (
                {"mixed": 0, "hard_only": 1, "preset_only": 2, "none": 3}.get(str(row.get("control_mode")), 9),
                -int(row.get("hard_attribute_count") or 0),
                -int(row.get("preset_ref_count") or 0),
                str(row.get("sequence_number") or ""),
                str(row.get("cue_number") or ""),
                int(row.get("fixture_id") or 0),
            )
        )

        object_liveness: list[dict[str, object]] = []
        for preset in show.presets:
            usage = preset_usage_map.get(preset.number or "", {"cues": set(), "sequences": set()})
            object_liveness.append(
                {
                    "object_type": "preset",
                    "object_number": preset.number,
                    "object_name": preset.name,
                    "usage_count": len(usage["cues"]),
                    "sequence_count": len(usage["sequences"]),
                    "status": "dead" if not usage["cues"] else "live",
                }
            )
        for group in show.groups:
            usage = group_usage_map.get(group.number or "", {"cues": set(), "sequences": set()})
            object_liveness.append(
                {
                    "object_type": "group",
                    "object_number": group.number,
                    "object_name": group.name,
                    "usage_count": len(usage["cues"]),
                    "sequence_count": len(usage["sequences"]),
                    "status": "dead" if not usage["cues"] else "live",
                }
            )
        for effect in show.effects:
            usage = effect_usage_map.get(effect.number or "", {"cues": set(), "sequences": set()})
            object_liveness.append(
                {
                    "object_type": "effect",
                    "object_number": effect.number,
                    "object_name": effect.name,
                    "usage_count": len(usage["cues"]),
                    "sequence_count": len(usage["sequences"]),
                    "status": "dead" if not usage["cues"] else "live",
                }
            )

        preset_logic_audit = self._build_preset_logic_breaks(show, patch_index, reference_index)
        missing_preset_audit = self._build_missing_preset_opportunities(show, patch_index)

        return {
            "cue_dependency_map": cue_dependency_map,
            "cue_quality": cue_quality,
            "worst_blocks": worst_blocks,
            "fixture_inconsistency": fixture_inconsistency,
            "repeated_hard_values": repeated_hard_values,
            "preset_heatmap": preset_heatmap,
            "fixture_coverage": fixture_coverage,
            "consistency_issues": consistency_issues,
            "risk_hotspots": risk_hotspots,
            "control_balance": control_balance,
            "object_liveness": object_liveness,
            "preset_logic_breaks": preset_logic_audit.get("preset_logic_breaks", []),
            "preset_logic_break_summary": preset_logic_audit.get("preset_logic_break_summary", {}),
            "preset_logic_repeaters": preset_logic_audit.get("preset_logic_repeaters", []),
            "missing_preset_opportunities": missing_preset_audit.get("missing_preset_opportunities", []),
            "missing_preset_summary": missing_preset_audit.get("missing_preset_summary", {}),
            "missing_preset_clusters": missing_preset_audit.get("missing_preset_clusters", []),
        }

    def _write_audit_reports(self, show: ShowData, audit: dict[str, object], output_dir: Path) -> None:
        (output_dir / "audit_summary.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
        self._write_table(output_dir / "dependency_map.csv", list(audit.get("cue_dependency_map", [])))
        self._write_table(output_dir / "cue_quality.csv", list(audit.get("cue_quality", [])))
        self._write_table(output_dir / "worst_blocks.csv", list(audit.get("worst_blocks", [])))
        self._write_table(output_dir / "fixture_inconsistency.csv", list(audit.get("fixture_inconsistency", [])))
        self._write_table(output_dir / "repeated_hard_values.csv", list(audit.get("repeated_hard_values", [])))
        self._write_table(output_dir / "preset_heatmap.csv", list(audit.get("preset_heatmap", [])))
        self._write_table(output_dir / "fixture_coverage.csv", list(audit.get("fixture_coverage", [])))
        self._write_table(output_dir / "consistency_issues.csv", list(audit.get("consistency_issues", [])))
        self._write_table(output_dir / "risk_hotspots.csv", list(audit.get("risk_hotspots", [])))
        self._write_table(output_dir / "control_balance.csv", list(audit.get("control_balance", [])))
        self._write_table(output_dir / "object_liveness.csv", list(audit.get("object_liveness", [])))
        self._write_table(output_dir / "preset_logic_breaks.csv", list(audit.get("preset_logic_breaks", [])))
        self._write_table(output_dir / "preset_logic_repeaters.csv", list(audit.get("preset_logic_repeaters", [])))
        self._write_table(output_dir / "missing_preset_opportunities.csv", list(audit.get("missing_preset_opportunities", [])))
        self._write_table(output_dir / "missing_preset_clusters.csv", list(audit.get("missing_preset_clusters", [])))

        lines = [
            "# grandMA2 Audit Report",
            "",
            "## Dependency map",
            f"- Cues analyzed: {len(audit.get('cue_dependency_map', []))}",
            "",
            "## Preset heatmap",
        ]
        for row in list(audit.get("preset_heatmap", []))[:10]:
            lines.append(
                f"- Preset {row.get('preset_number')}: cues={row.get('cue_count')}, sequences={row.get('sequence_count')}, status={row.get('usage_status')}, duplicates={row.get('duplicate_candidate_count')}"
            )
        lines.extend(["", "## Consistency issues"])
        for row in list(audit.get("consistency_issues", []))[:10]:
            lines.append(f"- {row.get('issue_type')}: {row.get('subject')} | {row.get('details')}")
        lines.extend(["", "## Risk hotspots"])
        for row in list(audit.get("risk_hotspots", []))[:15]:
            lines.append(f"- {row.get('subject')} | score={row.get('risk_score')} | {row.get('details')}")
        lines.extend(["", "## Cue quality"])
        for row in list(audit.get("cue_quality", []))[:15]:
            lines.append(
                f"- Seq {row.get('sequence_number')} Cue {row.get('cue_number')} | score={row.get('quality_risk_score')} | {row.get('reasons_text')}"
            )
        lines.extend(["", "## Worst blocks"])
        for row in list(audit.get("worst_blocks", []))[:10]:
            lines.append(
                f"- Seq {row.get('sequence_number')} cues {row.get('cue_range')} | avg={row.get('average_score')} | {row.get('summary')}"
            )
        lines.extend(["", "## Fixture inconsistency"])
        for row in list(audit.get("fixture_inconsistency", []))[:10]:
            lines.append(
                f"- Fixture {row.get('fixture_id')} {row.get('feature_group')} | hard={row.get('hard_cue_count')} | preset={row.get('preset_cue_count')} | mixed={row.get('mixed_cue_count')}"
            )
        lines.extend(["", "## Hard vs preset balance"])
        for row in list(audit.get("control_balance", []))[:15]:
            lines.append(
                f"- Seq {row.get('sequence_number')} Cue {row.get('cue_number')} | Fixture {row.get('fixture_id')} | mode={row.get('control_mode')} | hard={row.get('hard_attribute_count')} | presets={row.get('preset_ref_count')}"
            )
        logic_summary = audit.get("preset_logic_break_summary", {})
        lines.extend(["", "## Preset logic breaks"])
        lines.append(f"- Total findings: {logic_summary.get('total', 0)}")
        lines.append(f"- Broken preset blocks: {logic_summary.get('broken_preset_block', 0)}")
        lines.append(f"- Local hard overrides: {logic_summary.get('local_hard_override', 0)}")
        lines.append(f"- Fragmented preset blocks: {logic_summary.get('fragmented_preset_block', 0)}")
        lines.append(f"- Repeated suspicious overrides: {logic_summary.get('repeated_suspicious_override', 0)}")
        for row in list(audit.get("preset_logic_breaks", []))[:12]:
            lines.append(
                f"- Seq {row.get('sequence_number') or '-'} Cue {row.get('cue_number') or '-'} | "
                f"{row.get('kind')} | family={row.get('attribute_family')} | preset={row.get('dominant_preset_number') or '-'} | "
                f"outliers={', '.join(map(str, row.get('fixture_ids_outliers') or [])) or '-'}"
            )
        missing_summary = audit.get("missing_preset_summary", {})
        lines.extend(["", "## Missing preset opportunities"])
        lines.append(f"- Total findings: {missing_summary.get('total', 0)}")
        lines.append(f"- Exact repeated blocks: {missing_summary.get('missing_preset_candidate_exact', 0)}")
        lines.append(f"- Near-identical repeated blocks: {missing_summary.get('missing_preset_candidate_near', 0)}")
        lines.append(f"- Fragmented repeated states: {missing_summary.get('fragmented_repeated_state', 0)}")
        lines.append(f"- Existing preset likely unused: {missing_summary.get('existing_preset_likely_unused', 0)}")
        for row in list(audit.get("missing_preset_opportunities", []))[:12]:
            lines.append(
                f"- {row.get('kind')} | family={row.get('attribute_family')} | cues={row.get('cue_range') or '-'} | "
                f"fixtures={', '.join(map(str, row.get('fixture_ids') or [])) or '-'} | occurrences={row.get('occurrence_count') or 0}"
            )
        (output_dir / "audit_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _attribute_family(self, attribute: str | None) -> str:
        normalized = (attribute or "").upper()
        if normalized.startswith("COLOR"):
            return "Color"
        if normalized.startswith(("POS", "POSITION", "PAN", "TILT")):
            return "Position"
        if normalized.startswith("GOBO"):
            return "Gobo"
        if normalized.startswith(("DIM", "SHUT", "STROBE")):
            return "Dimmer"
        if normalized.startswith(("FOCUS", "ZOOM", "IRIS", "BEAM", "PRISM", "FROST")):
            return "Beam"
        if normalized.startswith(("CTRL", "CONTROL", "LAMP")):
            return "Control"
        return "Other"

    def _is_dimmer_family(self, attribute: str | None) -> bool:
        return self._attribute_family(attribute) == "Dimmer"

    def _hard_class(self, attribute: str | None) -> str:
        return "dimmer" if self._is_dimmer_family(attribute) else "hard"

    def _control_mode(self, has_hard: bool, has_preset: bool) -> str:
        if has_hard and has_preset:
            return "mixed"
        if has_hard:
            return "hard_only"
        if has_preset:
            return "preset_only"
        return "none"

    def _fixture_control_mode(self, counter: Counter[str]) -> str:
        return self._control_mode(counter.get("hard", 0) > 0, counter.get("preset", 0) > 0)

    def _normalize_name(self, name: str) -> str:
        return " ".join((name or "").strip().lower().split())

    def _safe_float(self, value: object) -> float | None:
        if value in (None, ""):
            return None
        try:
            return float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            return None

    def _is_zero_like(self, value: object) -> bool:
        number = self._safe_float(value)
        if number is None:
            return False
        return abs(number) <= 0.0001

    def _jaccard(self, left: set[str], right: set[str]) -> float:
        if not left and not right:
            return 1.0
        if not left or not right:
            return 0.0
        union = left | right
        if not union:
            return 1.0
        return len(left & right) / len(union)

    def _avg(self, rows: list[dict[str, object]], key: str) -> float:
        if not rows:
            return 0.0
        values = [float(row.get(key) or 0) for row in rows]
        return sum(values) / len(values)

    def _family_tolerance(self, attribute: str | None, family: str | None = None) -> float:
        family_name = family or self._attribute_family(attribute)
        normalized = (attribute or "").upper()
        if normalized.startswith(("PAN", "TILT")):
            return 0.25
        if family_name == "Position":
            return 0.5
        if family_name == "Color":
            return 1.0
        if family_name == "Beam":
            return 0.75
        if family_name == "Gobo":
            return 0.1
        if family_name == "Dimmer":
            return 1.0
        return 0.5

    def _value_match_state(self, cue_value: object, preset_value: object, attribute: str | None, family: str | None = None) -> tuple[str, float | None]:
        left_num = self._safe_float(cue_value)
        right_num = self._safe_float(preset_value)
        if left_num is not None and right_num is not None:
            delta = abs(left_num - right_num)
            if delta <= 0.0001:
                return ("exact", 0.0)
            tolerance = self._family_tolerance(attribute, family)
            if delta <= tolerance:
                return ("near", delta)
            return ("far", delta)
        left_text = str(cue_value or "").strip().lower()
        right_text = str(preset_value or "").strip().lower()
        if not left_text and not right_text:
            return ("exact", 0.0)
        if left_text == right_text:
            return ("exact", 0.0)
        return ("far", None)

    def _build_preset_logic_breaks(
        self,
        show: ShowData,
        patch_index: dict[int, dict],
        reference_index: dict[tuple[str, str], list[dict[str, object]]],
    ) -> dict[str, object]:
        relevant_families = {"Dimmer", "Position", "Color", "Beam", "Gobo"}
        preset_blocks_by_type_family: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)

        for preset in show.presets:
            grouped: dict[tuple[str, str], dict[int, dict[str, object]]] = defaultdict(dict)
            for atom in preset.values:
                if atom.fixture_id is None or not atom.attribute:
                    continue
                family = self._attribute_family(atom.attribute)
                if family not in relevant_families:
                    continue
                fixture_type = patch_index.get(int(atom.fixture_id), {}).get("fixture_type") or "Unknown"
                grouped.setdefault((fixture_type, family), {}).setdefault(int(atom.fixture_id), {})[atom.attribute] = atom.raw_value
            for (fixture_type, family), fixture_map in grouped.items():
                if len(fixture_map) < 2:
                    continue
                preset_blocks_by_type_family[(fixture_type, family)].append(
                    {
                        "preset_id": preset.id,
                        "preset_number": preset.number or preset.id,
                        "preset_name": preset.name or f"Preset {preset.number or preset.id}",
                        "preset_type": preset.preset_type,
                        "fixture_type": fixture_type,
                        "attribute_family": family,
                        "fixture_map": fixture_map,
                        "attribute_count": len({attr for attrs in fixture_map.values() for attr in attrs.keys()}),
                    }
                )

        findings: list[dict[str, object]] = []

        for sequence in show.sequences:
            for cue in sequence.cues:
                cue_preset_refs: set[str] = set()
                for atom in cue.values:
                    if atom.value_type == "preset_ref" and atom.reference_target:
                        cue_preset_refs.add(atom.reference_target.split(":", 1)[1])
                for ref in reference_index.get(("cue", cue.id), []):
                    target = str(ref.get("target") or "")
                    if target.startswith("preset:"):
                        cue_preset_refs.add(target.split(":", 1)[1])

                blocks: dict[tuple[str, str], dict[int, dict[str, ValueAtom]]] = defaultdict(lambda: defaultdict(dict))
                for atom in cue.values:
                    if atom.value_type != "hard" or atom.fixture_id is None or not atom.attribute:
                        continue
                    family = self._attribute_family(atom.attribute)
                    if family not in relevant_families:
                        continue
                    fixture_type = patch_index.get(int(atom.fixture_id), {}).get("fixture_type") or "Unknown"
                    blocks[(fixture_type, family)][int(atom.fixture_id)][atom.attribute] = atom

                for (fixture_type, family), fixture_map in blocks.items():
                    fixture_ids = sorted(fixture_map.keys())
                    if len(fixture_ids) < 3:
                        continue
                    block_attr_count = sum(len(attrs) for attrs in fixture_map.values())
                    if block_attr_count < 3:
                        continue

                    best: dict[str, object] | None = None
                    for candidate in preset_blocks_by_type_family.get((fixture_type, family), []):
                        matched_fixture_ids: list[int] = []
                        outlier_fixture_ids: list[int] = []
                        fixture_scores: list[float] = []
                        total_compared = 0
                        total_matched = 0
                        exact_matches = 0
                        near_matches = 0
                        outlier_details: list[dict[str, object]] = []

                        for fixture_id in fixture_ids:
                            cue_attrs = fixture_map.get(fixture_id, {})
                            preset_attrs = candidate["fixture_map"].get(fixture_id, {})
                            compared = 0
                            matched = 0
                            fixture_diffs: list[dict[str, object]] = []

                            for attribute, atom in cue_attrs.items():
                                if attribute not in preset_attrs:
                                    continue
                                compared += 1
                                state, delta = self._value_match_state(atom.raw_value, preset_attrs.get(attribute), attribute, family)
                                if state in {"exact", "near"}:
                                    matched += 1
                                    if state == "exact":
                                        exact_matches += 1
                                    else:
                                        near_matches += 1
                                else:
                                    fixture_diffs.append(
                                        {
                                            "attribute": attribute,
                                            "hard_value": self._format_attribute_raw_value(atom.raw_value),
                                            "expected_value": self._format_attribute_raw_value(preset_attrs.get(attribute)),
                                            "delta": round(float(delta), 4) if delta is not None else None,
                                            "match_state": state,
                                        }
                                    )

                            if compared == 0:
                                outlier_fixture_ids.append(fixture_id)
                                outlier_details.append(
                                    {
                                        "fixture_id": fixture_id,
                                        "fixture_name": patch_index.get(fixture_id, {}).get("label") or patch_index.get(fixture_id, {}).get("name"),
                                        "override_type": "fixture_override",
                                        "hard_values": [
                                            {
                                                "attribute": attribute,
                                                "hard_value": self._format_attribute_raw_value(atom.raw_value),
                                                "expected_value": None,
                                                "delta": None,
                                                "match_state": "no_preset_fixture_data",
                                            }
                                            for attribute, atom in cue_attrs.items()
                                        ],
                                    }
                                )
                                continue

                            total_compared += compared
                            total_matched += matched
                            ratio = matched / compared if compared else 0.0
                            fixture_scores.append(ratio)
                            if ratio >= 0.75:
                                matched_fixture_ids.append(fixture_id)
                            else:
                                outlier_fixture_ids.append(fixture_id)
                                outlier_details.append(
                                    {
                                        "fixture_id": fixture_id,
                                        "fixture_name": patch_index.get(fixture_id, {}).get("label") or patch_index.get(fixture_id, {}).get("name"),
                                        "override_type": "attribute_override" if fixture_diffs else "fixture_override",
                                        "hard_values": fixture_diffs or [
                                            {
                                                "attribute": attribute,
                                                "hard_value": self._format_attribute_raw_value(atom.raw_value),
                                                "expected_value": self._format_attribute_raw_value(preset_attrs.get(attribute)),
                                                "delta": None,
                                                "match_state": "far",
                                            }
                                            for attribute, atom in cue_attrs.items()
                                        ],
                                    }
                                )

                        if not matched_fixture_ids or total_compared == 0:
                            continue

                        fixture_coverage_ratio = len(matched_fixture_ids) / max(len(fixture_ids), 1)
                        attribute_coverage_ratio = total_matched / max(total_compared, 1)
                        exact_ratio = exact_matches / max(total_compared, 1)
                        near_ratio = near_matches / max(total_compared, 1)
                        cue_reference_bonus = 0.10 if str(candidate["preset_number"]) in cue_preset_refs else 0.0
                        dominant_score = (
                            fixture_coverage_ratio * 0.35
                            + attribute_coverage_ratio * 0.25
                            + exact_ratio * 0.20
                            + near_ratio * 0.10
                            + cue_reference_bonus
                        )

                        candidate_result = {
                            "candidate": candidate,
                            "matched_fixture_ids": sorted(matched_fixture_ids),
                            "outlier_fixture_ids": sorted(set(outlier_fixture_ids)),
                            "outlier_details": outlier_details,
                            "fixture_coverage_ratio": round(fixture_coverage_ratio, 3),
                            "attribute_coverage_ratio": round(attribute_coverage_ratio, 3),
                            "exact_ratio": round(exact_ratio, 3),
                            "near_ratio": round(near_ratio, 3),
                            "dominant_score": round(dominant_score, 3),
                            "cue_reference_bonus": cue_reference_bonus,
                            "total_compared": total_compared,
                            "fragment_count": len(outlier_details),
                        }
                        if best is None or float(candidate_result["dominant_score"]) > float(best["dominant_score"]):
                            best = candidate_result

                    if not best:
                        continue
                    if float(best["fixture_coverage_ratio"]) < 0.6 or float(best["dominant_score"]) < 0.68:
                        continue
                    outlier_ids = list(best["outlier_fixture_ids"])
                    if not outlier_ids:
                        continue

                    block_size = len(fixture_ids)
                    override_ratio = len(outlier_ids) / max(block_size, 1)
                    block_size_score = min(block_size / 8, 1.0)
                    locality_score = 1.0 - min(override_ratio, 1.0)
                    preset_reference_score = 1.0 if best["cue_reference_bonus"] else 0.0
                    confidence = round(
                        min(
                            0.99,
                            float(best["fixture_coverage_ratio"]) * 0.35
                            + float(best["attribute_coverage_ratio"]) * 0.20
                            + block_size_score * 0.15
                            + locality_score * 0.10
                            + preset_reference_score * 0.10,
                        ),
                        3,
                    )

                    kind = ""
                    if float(best["fixture_coverage_ratio"]) >= 0.85 and override_ratio <= 0.20:
                        kind = "broken_preset_block"
                    elif best["cue_reference_bonus"] or float(best["attribute_coverage_ratio"]) >= 0.75:
                        kind = "local_hard_override"
                    elif float(best["fixture_coverage_ratio"]) >= 0.65 and len(outlier_ids) >= 2:
                        kind = "fragmented_preset_block"
                    if not kind:
                        continue

                    severity = "low"
                    if float(best["fixture_coverage_ratio"]) >= 0.85 and override_ratio <= 0.20 and confidence >= 0.80:
                        severity = "high"
                    elif confidence >= 0.62:
                        severity = "medium"

                    matched_ids = list(best["matched_fixture_ids"])
                    block_id = f"cue:{sequence.number}:{cue.cue_number}|fixture_type:{fixture_type}|family:{family}"
                    explanation = (
                        f"Většina bloku {fixture_type} / {family} v cue {sequence.number}.{cue.cue_number} "
                        f"odpovídá presetu {best['candidate']['preset_number']} {best['candidate']['preset_name']}, "
                        f"ale fixtures {', '.join(map(str, outlier_ids[:8]))}{' ...' if len(outlier_ids) > 8 else ''} vybočují hard hodnotami."
                    )
                    recommendation = (
                        f"Vrátit fixtures {', '.join(map(str, outlier_ids[:8]))}{' ...' if len(outlier_ids) > 8 else ''} "
                        f"na preset {best['candidate']['preset_number']} a ověřit, zda override nebyl záměrný."
                        if kind == "broken_preset_block"
                        else (
                            f"Cue {sequence.number}.{cue.cue_number} obsahuje lokální hard override v jinak presetovém bloku; "
                            f"zkontrolovat fixtures {', '.join(map(str, outlier_ids[:8]))}{' ...' if len(outlier_ids) > 8 else ''}."
                            if kind == "local_hard_override"
                            else (
                                f"Blok je rozpadlý do více hard variant; zvážit sjednocení na preset {best['candidate']['preset_number']} "
                                f"nebo vytvoření čistého presetového stavu."
                            )
                        )
                    )

                    findings.append(
                        {
                            "kind": kind,
                            "severity": severity,
                            "confidence": confidence,
                            "sequence_id": sequence.id,
                            "sequence_number": sequence.number,
                            "cue_id": cue.id,
                            "cue_number": cue.cue_number,
                            "cue_name": cue.name,
                            "cue_range": None,
                            "block_id": block_id,
                            "block_scope": "cue_fixture_type_family",
                            "fixture_type": fixture_type,
                            "group_number": None,
                            "attribute_family": family,
                            "attributes": sorted({attribute for attrs in fixture_map.values() for attribute in attrs.keys()}),
                            "dominant_logic_type": "preset",
                            "dominant_preset_number": best["candidate"]["preset_number"],
                            "dominant_preset_name": best["candidate"]["preset_name"],
                            "dominant_preset_type": best["candidate"]["preset_type"],
                            "fixture_ids_total": fixture_ids,
                            "fixture_ids_matching": matched_ids,
                            "fixture_ids_outliers": outlier_ids,
                            "match_ratio": best["fixture_coverage_ratio"],
                            "attribute_coverage_ratio": best["attribute_coverage_ratio"],
                            "override_ratio": round(override_ratio, 3),
                            "repeat_count_in_show": 1,
                            "outlier_details": best["outlier_details"],
                            "explanation": explanation,
                            "recommendation": recommendation,
                        }
                    )

        repeat_buckets: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
        for finding in findings:
            repeat_key = (
                finding.get("kind"),
                finding.get("fixture_type"),
                finding.get("attribute_family"),
                finding.get("dominant_preset_number"),
                tuple(finding.get("fixture_ids_outliers") or []),
            )
            repeat_buckets[repeat_key].append(finding)

        repeaters: list[dict[str, object]] = []
        for grouped in repeat_buckets.values():
            if len(grouped) < 3:
                continue
            first = grouped[0]
            confidence = round(min(0.95, 0.55 + len(grouped) * 0.05), 3)
            severity = "medium" if confidence >= 0.7 else "low"
            cue_refs = [f"{row.get('sequence_number')}.{row.get('cue_number')}" for row in grouped[:12]]
            repeaters.append(
                {
                    "kind": "repeated_suspicious_override",
                    "severity": severity,
                    "confidence": confidence,
                    "sequence_id": None,
                    "sequence_number": grouped[0].get("sequence_number"),
                    "cue_id": None,
                    "cue_number": None,
                    "cue_name": None,
                    "cue_range": " | ".join(cue_refs) + (" ..." if len(grouped) > 12 else ""),
                    "block_id": f"repeat:{first.get('fixture_type')}:{first.get('attribute_family')}:{first.get('dominant_preset_number')}",
                    "block_scope": "repeated_pattern",
                    "fixture_type": first.get("fixture_type"),
                    "group_number": None,
                    "attribute_family": first.get("attribute_family"),
                    "attributes": first.get("attributes"),
                    "dominant_logic_type": "preset",
                    "dominant_preset_number": first.get("dominant_preset_number"),
                    "dominant_preset_name": first.get("dominant_preset_name"),
                    "dominant_preset_type": first.get("dominant_preset_type"),
                    "fixture_ids_total": [],
                    "fixture_ids_matching": [],
                    "fixture_ids_outliers": first.get("fixture_ids_outliers"),
                    "match_ratio": first.get("match_ratio"),
                    "attribute_coverage_ratio": first.get("attribute_coverage_ratio"),
                    "override_ratio": first.get("override_ratio"),
                    "repeat_count_in_show": len(grouped),
                    "outlier_details": [],
                    "explanation": (
                        f"Stejný override pattern se opakuje v {len(grouped)} cues pro {first.get('fixture_type')} / {first.get('attribute_family')} "
                        f"vůči presetu {first.get('dominant_preset_number')}."
                    ),
                    "recommendation": "Prověřit, zda nejde o dlouhodobě rozbitý presetový vztah nebo systematický hard override.",
                }
            )

        all_findings = findings + repeaters
        all_findings.sort(
            key=lambda row: (
                {"high": 0, "medium": 1, "low": 2}.get(str(row.get("severity")), 9),
                -float(row.get("confidence") or 0.0),
                str(row.get("sequence_number") or ""),
                str(row.get("cue_number") or ""),
            )
        )
        summary = {
            "total": len(all_findings),
            "broken_preset_block": sum(1 for row in all_findings if row.get("kind") == "broken_preset_block"),
            "local_hard_override": sum(1 for row in all_findings if row.get("kind") == "local_hard_override"),
            "fragmented_preset_block": sum(1 for row in all_findings if row.get("kind") == "fragmented_preset_block"),
            "repeated_suspicious_override": sum(1 for row in all_findings if row.get("kind") == "repeated_suspicious_override"),
            "high": sum(1 for row in all_findings if row.get("severity") == "high"),
            "medium": sum(1 for row in all_findings if row.get("severity") == "medium"),
            "low": sum(1 for row in all_findings if row.get("severity") == "low"),
        }
        return {
            "preset_logic_breaks": all_findings,
            "preset_logic_break_summary": summary,
            "preset_logic_repeaters": repeaters,
        }

    def _block_value_similarity(
        self,
        left_map: dict[int, dict[str, object]],
        right_map: dict[int, dict[str, object]],
        family: str,
    ) -> dict[str, object]:
        fixture_ids = sorted(set(left_map) | set(right_map))
        total_compared = 0
        total_matched = 0
        exact_matches = 0
        near_matches = 0
        missing_fixture_ids: list[int] = []
        mismatched_fixture_ids: list[int] = []
        deltas: list[float] = []
        compared_fixture_ids: list[int] = []

        for fixture_id in fixture_ids:
            left_attrs = left_map.get(fixture_id, {})
            right_attrs = right_map.get(fixture_id, {})
            if not left_attrs or not right_attrs:
                missing_fixture_ids.append(fixture_id)
                continue
            compared_fixture_ids.append(fixture_id)
            compared_here = 0
            matched_here = 0
            mismatched_here = False
            for attribute in sorted(set(left_attrs) | set(right_attrs)):
                if attribute not in left_attrs or attribute not in right_attrs:
                    mismatched_here = True
                    continue
                compared_here += 1
                state, delta = self._value_match_state(left_attrs.get(attribute), right_attrs.get(attribute), attribute, family)
                if state in {"exact", "near"}:
                    matched_here += 1
                    total_matched += 1
                    if state == "exact":
                        exact_matches += 1
                    else:
                        near_matches += 1
                    if delta is not None:
                        deltas.append(float(delta))
                else:
                    mismatched_here = True
                    if delta is not None:
                        deltas.append(float(delta))
                total_compared += 1
            if compared_here == 0 or matched_here < compared_here:
                mismatched_here = True
            if mismatched_here:
                mismatched_fixture_ids.append(fixture_id)

        value_similarity = total_matched / total_compared if total_compared else 0.0
        fixture_overlap = len(compared_fixture_ids) / max(len(fixture_ids), 1)
        attribute_overlap = value_similarity
        total_similarity = fixture_overlap * 0.35 + value_similarity * 0.45 + attribute_overlap * 0.20
        return {
            "fixture_overlap": round(fixture_overlap, 3),
            "value_similarity": round(value_similarity, 3),
            "attribute_overlap": round(attribute_overlap, 3),
            "total_similarity": round(total_similarity, 3),
            "exact_ratio": round(exact_matches / total_compared, 3) if total_compared else 0.0,
            "near_ratio": round(near_matches / total_compared, 3) if total_compared else 0.0,
            "avg_delta": round(sum(deltas) / len(deltas), 4) if deltas else None,
            "mismatched_fixture_ids": sorted(set(mismatched_fixture_ids)),
            "missing_fixture_ids": sorted(set(missing_fixture_ids)),
        }

    def _build_missing_preset_opportunities(self, show: ShowData, patch_index: dict[int, dict]) -> dict[str, object]:
        relevant_families = {"Dimmer", "Position", "Color", "Beam", "Gobo"}
        preset_blocks_by_type_family: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)

        for preset in show.presets:
            grouped: dict[tuple[str, str], dict[int, dict[str, object]]] = defaultdict(dict)
            for atom in preset.values:
                if atom.fixture_id is None or not atom.attribute:
                    continue
                family = self._attribute_family(atom.attribute)
                if family not in relevant_families:
                    continue
                fixture_type = patch_index.get(int(atom.fixture_id), {}).get("fixture_type") or "Unknown"
                grouped.setdefault((fixture_type, family), {}).setdefault(int(atom.fixture_id), {})[atom.attribute] = atom.raw_value
            for (fixture_type, family), fixture_map in grouped.items():
                if len(fixture_map) < 3:
                    continue
                preset_blocks_by_type_family[(fixture_type, family)].append(
                    {
                        "preset_id": preset.id,
                        "preset_number": preset.number or preset.id,
                        "preset_name": preset.name or f"Preset {preset.number or preset.id}",
                        "preset_type": preset.preset_type,
                        "fixture_map": fixture_map,
                    }
                )

        raw_blocks: list[dict[str, object]] = []
        for sequence in show.sequences:
            for cue in sequence.cues:
                grouped: dict[tuple[str, str], dict[int, dict[str, object]]] = defaultdict(dict)
                for atom in cue.values:
                    if atom.value_type != "hard" or atom.fixture_id is None or not atom.attribute:
                        continue
                    family = self._attribute_family(atom.attribute)
                    if family not in relevant_families:
                        continue
                    fixture_type = patch_index.get(int(atom.fixture_id), {}).get("fixture_type") or "Unknown"
                    grouped.setdefault((fixture_type, family), {}).setdefault(int(atom.fixture_id), {})[atom.attribute] = atom.raw_value

                for (fixture_type, family), fixture_map in grouped.items():
                    fixture_ids = sorted(fixture_map)
                    attributes = sorted({attribute for attrs in fixture_map.values() for attribute in attrs})
                    if len(fixture_ids) < 3 or len(attributes) < 2:
                        continue
                    exact_signature = "|".join(
                        f"{fixture_id}:{','.join(f'{attribute}={self._format_attribute_raw_value(fixture_map[fixture_id].get(attribute))}' for attribute in attributes if attribute in fixture_map[fixture_id])}"
                        for fixture_id in fixture_ids
                    )
                    raw_blocks.append(
                        {
                            "sequence_id": sequence.id,
                            "sequence_number": str(sequence.number or ""),
                            "cue_id": cue.id,
                            "cue_number": str(cue.cue_number or ""),
                            "cue_name": cue.name or "",
                            "fixture_type": fixture_type,
                            "attribute_family": family,
                            "fixture_ids": fixture_ids,
                            "attributes": attributes,
                            "fixture_map": fixture_map,
                            "block_scope": "cue_fixture_type_family",
                            "exact_signature": exact_signature,
                        }
                    )

        bucketed: dict[tuple[str, str, tuple[int, ...], tuple[str, ...]], list[dict[str, object]]] = defaultdict(list)
        for block in raw_blocks:
            key = (
                str(block["fixture_type"]),
                str(block["attribute_family"]),
                tuple(block["fixture_ids"]),
                tuple(block["attributes"]),
            )
            bucketed[key].append(block)

        clusters: list[dict[str, object]] = []
        for (fixture_type, family, fixture_ids_key, attributes_key), blocks in bucketed.items():
            groups_by_exact: dict[str, list[dict[str, object]]] = defaultdict(list)
            for block in blocks:
                groups_by_exact[str(block["exact_signature"])].append(block)

            for exact_blocks in groups_by_exact.values():
                if len(exact_blocks) >= 3:
                    representative = exact_blocks[0]
                    clusters.append(
                        {
                            "kind_seed": "exact",
                            "fixture_type": fixture_type,
                            "attribute_family": family,
                            "fixture_ids": list(fixture_ids_key),
                            "attributes": list(attributes_key),
                            "occurrences": exact_blocks,
                            "representative": representative,
                            "match_strength": 1.0,
                            "fixture_subset_stability": 1.0,
                            "fragmented": False,
                            "cluster_members": len(exact_blocks),
                        }
                    )

            remaining = [block for block in blocks if not any(block in exact_blocks and len(exact_blocks) >= 3 for exact_blocks in groups_by_exact.values())]
            if len(remaining) < 3:
                continue
            base = remaining[0]
            similar = [base]
            strengths = [1.0]
            exact_count = 1
            for candidate in remaining[1:]:
                similarity = self._block_value_similarity(
                    base["fixture_map"],
                    candidate["fixture_map"],
                    str(base["attribute_family"]),
                )
                if float(similarity["total_similarity"]) >= 0.78:
                    similar.append(candidate)
                    strengths.append(float(similarity["total_similarity"]))
                    if float(similarity["total_similarity"]) >= 0.95:
                        exact_count += 1
            if len(similar) >= 3:
                clusters.append(
                    {
                        "kind_seed": "near",
                        "fixture_type": fixture_type,
                        "attribute_family": family,
                        "fixture_ids": list(fixture_ids_key),
                        "attributes": list(attributes_key),
                        "occurrences": similar,
                        "representative": base,
                        "match_strength": round(sum(strengths) / len(strengths), 3),
                        "fixture_subset_stability": 1.0,
                        "fragmented": exact_count < len(similar),
                        "cluster_members": len(similar),
                    }
                )

        findings: list[dict[str, object]] = []
        cluster_rows: list[dict[str, object]] = []
        seen_cluster_keys: set[tuple[object, ...]] = set()

        for index, cluster in enumerate(sorted(clusters, key=lambda row: (-int(row["cluster_members"]), -float(row["match_strength"])),), start=1):
            cluster_key = (
                cluster["kind_seed"],
                cluster["fixture_type"],
                cluster["attribute_family"],
                tuple(cluster["fixture_ids"]),
                tuple(sorted((item["cue_id"], item["sequence_id"]) for item in cluster["occurrences"])),
            )
            if cluster_key in seen_cluster_keys:
                continue
            seen_cluster_keys.add(cluster_key)

            representative = cluster["representative"]
            occurrence_count = int(cluster["cluster_members"])
            existing_preset_match: dict[str, object] | None = None
            best_preset_score = 0.0
            for preset_candidate in preset_blocks_by_type_family.get((str(cluster["fixture_type"]), str(cluster["attribute_family"])), []):
                similarity = self._block_value_similarity(
                    representative["fixture_map"],
                    preset_candidate["fixture_map"],
                    str(cluster["attribute_family"]),
                )
                if float(similarity["total_similarity"]) > best_preset_score:
                    best_preset_score = float(similarity["total_similarity"])
                    existing_preset_match = {
                        "preset_number": preset_candidate["preset_number"],
                        "preset_name": preset_candidate["preset_name"],
                        "preset_type": preset_candidate["preset_type"],
                        "score": round(best_preset_score, 3),
                    }

            repeat_score = min(occurrence_count / 5, 1.0)
            block_size_score = min(len(cluster["fixture_ids"]) / 8, 1.0)
            no_existing_preset_score = max(0.0, 1.0 - best_preset_score)
            confidence = round(
                min(
                    0.99,
                    repeat_score * 0.30
                    + float(cluster["match_strength"]) * 0.25
                    + float(cluster["fixture_subset_stability"]) * 0.20
                    + block_size_score * 0.15
                    + no_existing_preset_score * 0.10,
                ),
                3,
            )

            kind = ""
            if existing_preset_match and float(existing_preset_match["score"]) >= 0.80:
                kind = "existing_preset_likely_unused"
            elif cluster["fragmented"] and occurrence_count >= 3:
                kind = "fragmented_repeated_state"
            elif occurrence_count >= 4 and float(cluster["match_strength"]) >= 0.95:
                kind = "missing_preset_candidate_exact"
            elif occurrence_count >= 3 and float(cluster["match_strength"]) >= 0.78:
                kind = "missing_preset_candidate_near"
            if not kind:
                continue

            severity = "low"
            if kind == "existing_preset_likely_unused":
                severity = "medium" if confidence >= 0.68 else "low"
            elif occurrence_count >= 4 and confidence >= 0.80:
                severity = "high"
            elif confidence >= 0.62:
                severity = "medium"

            occurrences = list(cluster["occurrences"])
            cue_refs = [f"{row.get('sequence_number')}.{row.get('cue_number')}" for row in occurrences]
            cue_range = ", ".join(cue_refs[:10]) + (" ..." if len(cue_refs) > 10 else "")
            sample_pattern = {
                str(fixture_id): {attribute: self._format_attribute_raw_value(value) for attribute, value in sorted(attrs.items())}
                for fixture_id, attrs in sorted(representative["fixture_map"].items())
            }
            if kind == "existing_preset_likely_unused":
                explanation = (
                    f"Stejný nebo velmi podobný hard block se opakuje v {occurrence_count} cues pro "
                    f"{cluster['fixture_type']} / {cluster['attribute_family']}, ale už existuje podobný preset "
                    f"{existing_preset_match['preset_number']} {existing_preset_match['preset_name']}."
                )
                recommendation = (
                    f"Prověřit použití existujícího presetu {existing_preset_match['preset_number']} místo opakovaného hard patternu."
                )
            elif kind == "fragmented_repeated_state":
                explanation = (
                    f"Více velmi podobných hard variant se opakuje v {occurrence_count} cues pro "
                    f"{cluster['fixture_type']} / {cluster['attribute_family']} a působí jako neformalizovaný presetový stav."
                )
                recommendation = "Sjednotit opakující se hard varianty do jednoho presetu nebo čistého standardního looku."
            else:
                explanation = (
                    f"Tento hard-programmed {cluster['attribute_family']} block se opakuje v {occurrence_count} cues "
                    f"pro {cluster['fixture_type']} na stejné skupině fixture bez silné preset reference."
                )
                recommendation = (
                    f"Zvážit vytvoření nového {cluster['attribute_family']} presetu pro fixtures "
                    f"{', '.join(map(str, cluster['fixture_ids'][:10]))}{' ...' if len(cluster['fixture_ids']) > 10 else ''}."
                )

            finding = {
                "kind": kind,
                "severity": severity,
                "confidence": confidence,
                "cluster_id": f"{cluster['attribute_family']}|{cluster['fixture_type']}|{index}",
                "attribute_family": cluster["attribute_family"],
                "fixture_type": cluster["fixture_type"],
                "attributes": cluster["attributes"],
                "sequence_ids": sorted({row.get("sequence_id") for row in occurrences if row.get("sequence_id")}),
                "sequence_numbers": sorted({row.get("sequence_number") for row in occurrences if row.get("sequence_number")}),
                "cue_ids": [row.get("cue_id") for row in occurrences if row.get("cue_id")],
                "cue_numbers": [row.get("cue_number") for row in occurrences if row.get("cue_number")],
                "cue_range": cue_range,
                "fixture_ids": cluster["fixture_ids"],
                "fixture_subset_stability": cluster["fixture_subset_stability"],
                "occurrence_count": occurrence_count,
                "match_strength": cluster["match_strength"],
                "dominant_hard_pattern": sample_pattern,
                "existing_preset_match": existing_preset_match,
                "explanation": explanation,
                "recommendation": recommendation,
            }
            findings.append(finding)
            cluster_rows.append(
                {
                    "cluster_id": finding["cluster_id"],
                    "fixture_type": finding["fixture_type"],
                    "attribute_family": finding["attribute_family"],
                    "fixture_ids": finding["fixture_ids"],
                    "attributes": finding["attributes"],
                    "occurrence_count": finding["occurrence_count"],
                    "match_strength": finding["match_strength"],
                    "kind_seed": cluster["kind_seed"],
                    "fragmented": cluster["fragmented"],
                    "cue_range": finding["cue_range"],
                    "existing_preset_number": (existing_preset_match or {}).get("preset_number"),
                    "existing_preset_score": (existing_preset_match or {}).get("score"),
                }
            )

        findings.sort(
            key=lambda row: (
                {"high": 0, "medium": 1, "low": 2}.get(str(row.get("severity")), 9),
                -float(row.get("confidence") or 0.0),
                -int(row.get("occurrence_count") or 0),
                str(row.get("attribute_family") or ""),
            )
        )
        summary = {
            "total": len(findings),
            "missing_preset_candidate_exact": sum(1 for row in findings if row.get("kind") == "missing_preset_candidate_exact"),
            "missing_preset_candidate_near": sum(1 for row in findings if row.get("kind") == "missing_preset_candidate_near"),
            "fragmented_repeated_state": sum(1 for row in findings if row.get("kind") == "fragmented_repeated_state"),
            "existing_preset_likely_unused": sum(1 for row in findings if row.get("kind") == "existing_preset_likely_unused"),
            "high": sum(1 for row in findings if row.get("severity") == "high"),
            "medium": sum(1 for row in findings if row.get("severity") == "medium"),
            "low": sum(1 for row in findings if row.get("severity") == "low"),
        }
        return {
            "missing_preset_opportunities": findings,
            "missing_preset_summary": summary,
            "missing_preset_clusters": cluster_rows,
        }
