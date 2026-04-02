from __future__ import annotations

import json
from pathlib import Path

from .models import ShowData


def write_dashboard_html(writer: object, show: ShowData, audit: dict[str, object], output_dir: Path, template_path: Path | None) -> None:
    if template_path is None:
        template_path = Path(__file__).resolve().parents[2] / "templates" / "dashboard.html.j2"
    template = template_path.read_text(encoding="utf-8")
    summary = writer._rounded_summary(show)
    graph = writer._build_graph(show)
    flat_cues = [cue.to_dict() for sequence in show.sequences for cue in sequence.cues]
    stats = {
        "sequence_count": len(show.sequences),
        "main_sequence_count": len(show.main_sequence_numbers),
        "cue_count": len(flat_cues),
        "preset_count": len(show.presets),
        "group_count": len(show.groups),
        "effect_count": len(show.effects),
        "patch_fixture_count": len(show.patch_fixtures),
        "relationship_count": len(show.relationships),
        "unresolved_relationship_count": sum(1 for relation in show.relationships if relation.relation_type == "reference_unresolved"),
        "fixture_count": len(show.fixture_usage),
        "hard_value_atoms": sum(1 for sequence in show.sequences for cue in sequence.cues for atom in cue.values if atom.value_type == "hard")
        + sum(1 for preset in show.presets for atom in preset.values if atom.value_type == "hard"),
        "preset_ref_atoms": sum(1 for sequence in show.sequences for cue in sequence.cues for atom in cue.values if atom.value_type == "preset_ref")
        + sum(1 for preset in show.presets for atom in preset.values if atom.value_type == "preset_ref"),
        "effect_ref_atoms": sum(1 for sequence in show.sequences for cue in sequence.cues for atom in cue.values if atom.value_type == "effect_ref")
        + sum(1 for preset in show.presets for atom in preset.values if atom.value_type == "effect_ref"),
        "group_ref_atoms": sum(1 for sequence in show.sequences for cue in sequence.cues for atom in cue.values if atom.value_type == "group_ref")
        + sum(1 for preset in show.presets for atom in preset.values if atom.value_type == "group_ref"),
    }
    html = (
        template
        .replace("$DATA_JSON", json.dumps(summary, ensure_ascii=False))
        .replace("$STATS_JSON", json.dumps(stats, ensure_ascii=False))
        .replace("$GRAPH_JSON", json.dumps(graph, ensure_ascii=False))
        .replace("$AUDIT_JSON", json.dumps(audit, ensure_ascii=False))
    )
    (output_dir / "dashboard.html").write_text(writer._inline_branding_assets(html), encoding="utf-8")


def _write_template_data_html(writer: object, output_name: str, template_name: str, show: ShowData, output_dir: Path, *, include_graph: bool = False, audit: dict[str, object] | None = None) -> None:
    template_path = Path(__file__).resolve().parents[2] / "templates" / template_name
    template = template_path.read_text(encoding="utf-8")
    summary = writer._rounded_summary(show)
    html = template.replace("$DATA_JSON", json.dumps(summary, ensure_ascii=False))
    if include_graph:
        html = html.replace("$GRAPH_JSON", json.dumps(writer._build_graph(show), ensure_ascii=False))
    if audit is not None:
        html = html.replace("$AUDIT_JSON", json.dumps(audit, ensure_ascii=False))
    (output_dir / output_name).write_text(writer._inline_branding_assets(html), encoding="utf-8")


def write_explorer_html(writer: object, show: ShowData, output_dir: Path) -> None:
    _write_template_data_html(writer, "explorer.html", "explorer.html.j2", show, output_dir, include_graph=True)


def write_topology_graphs_html(writer: object, show: ShowData, output_dir: Path) -> None:
    _write_template_data_html(writer, "topology_graphs.html", "topology_graphs.html.j2", show, output_dir, include_graph=True)


def write_patch_html(writer: object, show: ShowData, output_dir: Path) -> None:
    _write_template_data_html(writer, "patch.html", "patch.html.j2", show, output_dir)


def write_cue_list_html(writer: object, show: ShowData, output_dir: Path) -> None:
    _write_template_data_html(writer, "cue_list.html", "cue_list.html.j2", show, output_dir)


def write_sequence_content_html(writer: object, show: ShowData, output_dir: Path) -> None:
    _write_template_data_html(writer, "sequence_content.html", "sequence_content.html.j2", show, output_dir, include_graph=True)


def write_sequence_inspector_html(writer: object, show: ShowData, output_dir: Path) -> None:
    _write_template_data_html(writer, "sequence_inspector.html", "sequence_inspector.html.j2", show, output_dir)


def write_preset_logic_breaks_html(writer: object, show: ShowData, audit: dict[str, object], output_dir: Path) -> None:
    _write_template_data_html(writer, "preset_logic_breaks.html", "preset_logic_breaks.html.j2", show, output_dir, audit=audit)


def write_missing_preset_opportunities_html(writer: object, show: ShowData, audit: dict[str, object], output_dir: Path) -> None:
    _write_template_data_html(writer, "missing_preset_opportunities.html", "missing_preset_opportunities.html.j2", show, output_dir, audit=audit)


def write_warnings_html(writer: object, show: ShowData, output_dir: Path) -> None:
    _write_template_data_html(writer, "warnings.html", "warnings.html.j2", show, output_dir)


def write_cue_quality_html(writer: object, show: ShowData, audit: dict[str, object], output_dir: Path) -> None:
    _write_template_data_html(writer, "cue_quality.html", "cue_quality.html.j2", show, output_dir, audit=audit)


def write_explorer_d3_html(writer: object, show: ShowData, output_dir: Path) -> None:
    _write_template_data_html(writer, "explorer_d3.html", "explorer_d3.html.j2", show, output_dir, include_graph=True)


def write_explorer_radial_html(writer: object, show: ShowData, output_dir: Path) -> None:
    _write_template_data_html(writer, "explorer_radial.html", "explorer_radial.html.j2", show, output_dir, include_graph=True)


def write_explorer_sankey_html(writer: object, show: ShowData, output_dir: Path) -> None:
    _write_template_data_html(writer, "explorer_sankey.html", "explorer_sankey.html.j2", show, output_dir)
