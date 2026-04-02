from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from .models import Cue, Effect, Group, Preset, Relationship, Sequence, ShowData, ValueAtom


class ShowAnalyzer:
    def analyze(self, show: ShowData) -> ShowData:
        relationships: list[Relationship] = []
        fixture_usage: dict[int, dict[str, object]] = defaultdict(lambda: {
            "sequence_count": 0,
            "cue_count": 0,
            "preset_count": 0,
            "group_count": 0,
            "effect_count": 0,
            "sequences": set(),
            "cues": set(),
            "presets": set(),
            "groups": set(),
            "effects": set(),
            "hard_value_atoms": 0,
            "dimmer_value_atoms": 0,
            "preset_ref_atoms": 0,
            "effect_ref_atoms": 0,
            "group_ref_atoms": 0,
        })
        patch_target_usage: dict[str, dict[str, object]] = defaultdict(lambda: {
            "sequence_count": 0,
            "cue_count": 0,
            "preset_count": 0,
            "group_count": 0,
            "effect_count": 0,
            "sequences": set(),
            "cues": set(),
            "presets": set(),
            "groups": set(),
            "effects": set(),
            "hard_value_atoms": 0,
            "dimmer_value_atoms": 0,
            "preset_ref_atoms": 0,
            "effect_ref_atoms": 0,
            "group_ref_atoms": 0,
            "patch_target_type": "fixture",
            "patch_target_id": None,
            "fixture_id": None,
            "channel_id": None,
            "subfixture_id": None,
        })

        preset_index = {p.number: p for p in show.presets if p.number}
        group_index = {g.number: g for g in show.groups if g.number}
        effect_index = {e.number: e for e in show.effects if e.number}
        sequence_index = {s.number: s for s in show.sequences if s.number}

        def is_dimmer_attribute(attribute: str | None) -> bool:
            normalized = str(attribute or "").upper()
            return normalized.startswith("DIM") or normalized.startswith("SHUT") or normalized.startswith("STROBE")

        def apply_patch_target_usage(
            target_key: str | None,
            *,
            owner_bucket: str | None = None,
            owner_id: str | None = None,
            increment: str | None = None,
            patch_target_type: str | None = None,
            patch_target_id: int | None = None,
            fixture_id: int | None = None,
            channel_id: int | None = None,
            subfixture_id: int | None = None,
        ) -> None:
            if not target_key:
                return
            rec = patch_target_usage[target_key]
            rec["patch_target_type"] = patch_target_type or rec.get("patch_target_type") or "fixture"
            rec["patch_target_id"] = patch_target_id if patch_target_id is not None else rec.get("patch_target_id")
            rec["fixture_id"] = fixture_id if fixture_id is not None else rec.get("fixture_id")
            rec["channel_id"] = channel_id if channel_id is not None else rec.get("channel_id")
            rec["subfixture_id"] = subfixture_id if subfixture_id is not None else rec.get("subfixture_id")
            if increment:
                rec[increment] += 1
            if owner_bucket and owner_id:
                rec[owner_bucket].add(owner_id)

        for sequence in show.sequences:
            seq_fixture_ids = set()
            seq_patch_target_keys = set()
            for cue in sequence.cues:
                seq_fixture_ids.update(cue.fixture_ids)
                seq_patch_target_keys.update(cue.patch_target_keys)
                self._consume_refs(
                    owner_type="cue",
                    owner_id=cue.id,
                    refs=cue.references,
                    relationships=relationships,
                    preset_index=preset_index,
                    group_index=group_index,
                    effect_index=effect_index,
                    sequence_index=sequence_index,
                )
                self._consume_atoms(cue.id, "cue", cue.values, relationships)
                for fixture_id in cue.fixture_ids:
                    rec = fixture_usage[fixture_id]
                    rec["cue_count"] += 1
                    rec["cues"].add(cue.id)
                for target_key in cue.patch_target_keys:
                    target_type, _, target_id = target_key.partition(":")
                    parsed_target_id = int(target_id.split(":", 1)[0]) if target_id and target_id.split(":", 1)[0].isdigit() else None
                    apply_patch_target_usage(
                        target_key,
                        owner_bucket="cues",
                        owner_id=cue.id,
                        increment="cue_count",
                        patch_target_type=target_type or "fixture",
                        patch_target_id=parsed_target_id,
                        fixture_id=parsed_target_id if (target_type or "fixture") != "channel" else None,
                        channel_id=parsed_target_id if target_type == "channel" else None,
                    )
                for atom in cue.values:
                    if atom.fixture_id is not None:
                        rec = fixture_usage[atom.fixture_id]
                        if atom.value_type == "hard":
                            if is_dimmer_attribute(atom.attribute):
                                rec["dimmer_value_atoms"] += 1
                            else:
                                rec["hard_value_atoms"] += 1
                        elif atom.value_type == "preset_ref":
                            rec["preset_ref_atoms"] += 1
                        elif atom.value_type == "effect_ref":
                            rec["effect_ref_atoms"] += 1
                        elif atom.value_type == "group_ref":
                            rec["group_ref_atoms"] += 1
                    apply_patch_target_usage(
                        atom.patch_target_key,
                        increment=(
                            f"{atom.value_type}_atoms"
                            if atom.value_type in {"preset_ref", "effect_ref", "group_ref"}
                            else ("dimmer_value_atoms" if atom.value_type == "hard" and is_dimmer_attribute(atom.attribute) else ("hard_value_atoms" if atom.value_type == "hard" else None))
                        ),
                        patch_target_type=atom.patch_target_type,
                        patch_target_id=atom.patch_target_id,
                        fixture_id=atom.fixture_id,
                        channel_id=atom.channel_id,
                        subfixture_id=atom.subfixture_id,
                    )
            for fixture_id in seq_fixture_ids:
                rec = fixture_usage[fixture_id]
                rec["sequence_count"] += 1
                rec["sequences"].add(sequence.id)
            for target_key in seq_patch_target_keys:
                apply_patch_target_usage(target_key, owner_bucket="sequences", owner_id=sequence.id, increment="sequence_count")

        for preset in show.presets:
            self._consume_refs(
                owner_type="preset",
                owner_id=preset.id,
                refs=preset.references,
                relationships=relationships,
                preset_index=preset_index,
                group_index=group_index,
                effect_index=effect_index,
                sequence_index=sequence_index,
            )
            self._consume_atoms(preset.id, "preset", preset.values, relationships)
            for fixture_id in preset.fixture_ids:
                rec = fixture_usage[fixture_id]
                rec["preset_count"] += 1
                rec["presets"].add(preset.id)
            for target_key in preset.patch_target_keys:
                target_type, _, target_id = target_key.partition(":")
                parsed_target_id = int(target_id.split(":", 1)[0]) if target_id and target_id.split(":", 1)[0].isdigit() else None
                apply_patch_target_usage(
                    target_key,
                    owner_bucket="presets",
                    owner_id=preset.id,
                    increment="preset_count",
                    patch_target_type=target_type or "fixture",
                    patch_target_id=parsed_target_id,
                    fixture_id=parsed_target_id if (target_type or "fixture") != "channel" else None,
                    channel_id=parsed_target_id if target_type == "channel" else None,
                )
            for atom in preset.values:
                if atom.fixture_id is not None:
                    rec = fixture_usage[atom.fixture_id]
                    if atom.value_type == "hard":
                        if is_dimmer_attribute(atom.attribute):
                            rec["dimmer_value_atoms"] += 1
                        else:
                            rec["hard_value_atoms"] += 1
                    elif atom.value_type == "preset_ref":
                        rec["preset_ref_atoms"] += 1
                    elif atom.value_type == "effect_ref":
                        rec["effect_ref_atoms"] += 1
                    elif atom.value_type == "group_ref":
                        rec["group_ref_atoms"] += 1
                apply_patch_target_usage(
                    atom.patch_target_key,
                    increment=(
                        f"{atom.value_type}_atoms"
                        if atom.value_type in {"preset_ref", "effect_ref", "group_ref"}
                        else ("dimmer_value_atoms" if atom.value_type == "hard" and is_dimmer_attribute(atom.attribute) else ("hard_value_atoms" if atom.value_type == "hard" else None))
                    ),
                    patch_target_type=atom.patch_target_type,
                    patch_target_id=atom.patch_target_id,
                    fixture_id=atom.fixture_id,
                    channel_id=atom.channel_id,
                    subfixture_id=atom.subfixture_id,
                )

        for group in show.groups:
            for fixture_id in group.fixture_ids:
                rec = fixture_usage[fixture_id]
                rec["group_count"] += 1
                rec["groups"].add(group.id)
            for target_key in group.patch_target_keys:
                target_type, _, target_id = target_key.partition(":")
                parsed_target_id = int(target_id.split(":", 1)[0]) if target_id and target_id.split(":", 1)[0].isdigit() else None
                apply_patch_target_usage(
                    target_key,
                    owner_bucket="groups",
                    owner_id=group.id,
                    increment="group_count",
                    patch_target_type=target_type or "fixture",
                    patch_target_id=parsed_target_id,
                    fixture_id=parsed_target_id if (target_type or "fixture") != "channel" else None,
                    channel_id=parsed_target_id if target_type == "channel" else None,
                )

        for effect in show.effects:
            self._consume_refs(
                owner_type="effect",
                owner_id=effect.id,
                refs=effect.references,
                relationships=relationships,
                preset_index=preset_index,
                group_index=group_index,
                effect_index=effect_index,
                sequence_index=sequence_index,
            )
            for fixture_id in effect.fixture_ids:
                rec = fixture_usage[fixture_id]
                rec["effect_count"] += 1
                rec["effects"].add(effect.id)
            for target_key in effect.patch_target_keys:
                target_type, _, target_id = target_key.partition(":")
                parsed_target_id = int(target_id.split(":", 1)[0]) if target_id and target_id.split(":", 1)[0].isdigit() else None
                apply_patch_target_usage(
                    target_key,
                    owner_bucket="effects",
                    owner_id=effect.id,
                    increment="effect_count",
                    patch_target_type=target_type or "fixture",
                    patch_target_id=parsed_target_id,
                    fixture_id=parsed_target_id if (target_type or "fixture") != "channel" else None,
                    channel_id=parsed_target_id if target_type == "channel" else None,
                )

        show.relationships = self._dedup_relationships(relationships)
        show.fixture_usage = {
            int(fid): {
                **{k: (sorted(v) if isinstance(v, set) else v) for k, v in usage.items()},
                "fixture_id": int(fid),
            }
            for fid, usage in fixture_usage.items()
        }
        show.patch_target_usage = {
            target_key: {
                **{k: (sorted(v) if isinstance(v, set) else v) for k, v in usage.items()},
                "patch_target_key": target_key,
            }
            for target_key, usage in patch_target_usage.items()
        }
        return show

    def _consume_atoms(self, owner_id: str, owner_type: str, atoms: Iterable[ValueAtom], relationships: list[Relationship]) -> None:
        for atom in atoms:
            if atom.reference_target:
                target_type, target_id = atom.reference_target.split(":", 1)
                relationships.append(
                    Relationship(
                        source_type=owner_type,
                        source_id=owner_id,
                        target_type=target_type,
                        target_id=target_id,
                        relation_type="value_reference",
                        evidence=f"atom:{atom.attribute}={atom.raw_value}",
                    )
                )

    def _consume_refs(
        self,
        owner_type: str,
        owner_id: str,
        refs: Iterable[str],
        relationships: list[Relationship],
        preset_index: dict[str, Preset],
        group_index: dict[str, Group],
        effect_index: dict[str, Effect],
        sequence_index: dict[str, Sequence],
    ) -> None:
        for ref in refs:
            if ":" not in ref:
                continue
            target_type, target_id = ref.split(":", 1)
            if target_type == "preset":
                exists = target_id in preset_index
            elif target_type == "group":
                exists = target_id in group_index
            elif target_type == "effect":
                exists = target_id in effect_index
            elif target_type == "sequence":
                exists = target_id in sequence_index
            else:
                exists = False
            relationships.append(
                Relationship(
                    source_type=owner_type,
                    source_id=owner_id,
                    target_type=target_type,
                    target_id=target_id,
                    relation_type="reference" if exists else "reference_unresolved",
                    evidence=ref,
                )
            )

    def _dedup_relationships(self, relationships: list[Relationship]) -> list[Relationship]:
        seen: set[tuple[str, str, str, str, str, str]] = set()
        out: list[Relationship] = []
        for rel in relationships:
            key = (rel.source_type, rel.source_id, rel.target_type, rel.target_id, rel.relation_type, rel.evidence)
            if key not in seen:
                seen.add(key)
                out.append(rel)
        return out
