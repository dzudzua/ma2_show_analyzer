from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class ValueAtom:
    attribute: str | None = None
    raw_value: str | None = None
    value_type: str = "unknown"
    fixture_id: int | None = None
    channel_id: int | None = None
    subfixture_id: int | None = None
    patch_target_type: str | None = None
    patch_target_id: int | None = None
    patch_target_key: str | None = None
    reference_target: str | None = None
    raw_reference: str | None = None
    reference_display: str | None = None
    reference_confidence: float | None = None
    reference_scope: str | None = None
    flags: list[str] = field(default_factory=list)
    source_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Relationship:
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    relation_type: str
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Cue:
    id: str
    sequence_number: str | None = None
    cue_number: str | None = None
    name: str | None = None
    fade: str | None = None
    delay: str | None = None
    trigger: str | None = None
    trigger_time: str | None = None
    down_delay: str | None = None
    command: str | None = None
    part: str | None = None
    fixture_ids: list[int] = field(default_factory=list)
    channel_ids: list[int] = field(default_factory=list)
    patch_target_keys: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    values: list[ValueAtom] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    source_file: str | None = None
    is_main_cue_list: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["values"] = [v.to_dict() for v in self.values]
        return d


@dataclass
class Sequence:
    id: str
    number: str | None = None
    name: str | None = None
    source_file: str | None = None
    cues: list[Cue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    is_main_cue_list: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["cues"] = [c.to_dict() for c in self.cues]
        return d


@dataclass
class Preset:
    id: str
    preset_type: str | None = None
    number: str | None = None
    name: str | None = None
    fixture_ids: list[int] = field(default_factory=list)
    channel_ids: list[int] = field(default_factory=list)
    patch_target_keys: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    values: list[ValueAtom] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    source_file: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["values"] = [v.to_dict() for v in self.values]
        return d


@dataclass
class Group:
    id: str
    number: str | None = None
    name: str | None = None
    fixture_ids: list[int] = field(default_factory=list)
    channel_ids: list[int] = field(default_factory=list)
    patch_target_keys: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    source_file: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Effect:
    id: str
    number: str | None = None
    name: str | None = None
    fixture_ids: list[int] = field(default_factory=list)
    channel_ids: list[int] = field(default_factory=list)
    patch_target_keys: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    source_file: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PatchFixture:
    fixture_id: int
    channel_id: int | None = None
    subfixture_id: int | None = None
    ma_fixture_id: int | None = None
    ma_channel_id: int | None = None
    patch_target_type: str = "fixture"
    patch_target_id: int | None = None
    patch_target_key: str | None = None
    source_object_type: str | None = None
    source_object_id: int | None = None
    name: str | None = None
    label: str | None = None
    fixture_type: str | None = None
    mode: str | None = None
    patch: str | None = None
    universe: str | None = None
    address: str | None = None
    raw_address: str | None = None
    footprint: int | None = None
    react_to_grandmaster: bool | None = None
    color: str | None = None
    pos_x: str | None = None
    pos_y: str | None = None
    pos_z: str | None = None
    rot_x: str | None = None
    rot_y: str | None = None
    rot_z: str | None = None
    scale_x: str | None = None
    scale_y: str | None = None
    scale_z: str | None = None
    source_file: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GenericObject:
    id: str
    object_type: str
    number: str | None = None
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    source_file: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NormalizedReference:
    owner_type: str
    owner_id: str
    kind: str
    target: str | None = None
    display: str | None = None
    raw_reference: str | None = None
    confidence: float | None = None
    scope: str | None = None
    fixture_id: int | None = None
    channel_id: int | None = None
    subfixture_id: int | None = None
    patch_target_type: str | None = None
    patch_target_id: int | None = None
    patch_target_key: str | None = None
    attribute: str | None = None
    target_exists: bool | None = None
    source_path: str | None = None
    source_file: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FixtureRecord:
    fixture_id: int
    channel_id: int | None = None
    subfixture_id: int | None = None
    ma_fixture_id: int | None = None
    ma_channel_id: int | None = None
    patch_target_type: str = "fixture"
    patch_target_id: int | None = None
    patch_target_key: str | None = None
    source_object_type: str | None = None
    source_object_id: int | None = None
    name: str | None = None
    label: str | None = None
    display_name: str | None = None
    fixture_type: str | None = None
    mode: str | None = None
    patch: str | None = None
    universe: str | None = None
    address: str | None = None
    raw_address: str | None = None
    footprint: int | None = None
    react_to_grandmaster: bool | None = None
    color: str | None = None
    pos_x: str | None = None
    pos_y: str | None = None
    pos_z: str | None = None
    rot_x: str | None = None
    rot_y: str | None = None
    rot_z: str | None = None
    scale_x: str | None = None
    scale_y: str | None = None
    scale_z: str | None = None
    source_files: list[str] = field(default_factory=list)
    flags: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ShowData:
    sequences: list[Sequence] = field(default_factory=list)
    presets: list[Preset] = field(default_factory=list)
    groups: list[Group] = field(default_factory=list)
    effects: list[Effect] = field(default_factory=list)
    patch_fixtures: list[PatchFixture] = field(default_factory=list)
    generic_objects: list[GenericObject] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    fixture_usage: dict[int, dict[str, Any]] = field(default_factory=dict)
    patch_target_usage: dict[str, dict[str, Any]] = field(default_factory=dict)
    main_sequence_numbers: list[str] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequences": [s.to_dict() for s in self.sequences],
            "presets": [p.to_dict() for p in self.presets],
            "groups": [g.to_dict() for g in self.groups],
            "effects": [e.to_dict() for e in self.effects],
            "patch_fixtures": [p.to_dict() for p in self.patch_fixtures],
            "generic_objects": [g.to_dict() for g in self.generic_objects],
            "relationships": [r.to_dict() for r in self.relationships],
            "fixture_usage": self.fixture_usage,
            "patch_target_usage": self.patch_target_usage,
            "main_sequence_numbers": self.main_sequence_numbers,
            "warnings": self.warnings,
        }

    def build_fixture_registry(self) -> list[dict[str, Any]]:
        registry: dict[str, FixtureRecord] = {}

        def patch_target_key(patch_target_type: str | None, patch_target_id: int | None, subfixture_id: int | None = None) -> str:
            base_type = patch_target_type or "fixture"
            if patch_target_id is None:
                return "fixture:unknown"
            if subfixture_id is not None:
                return f"{base_type}:{patch_target_id}:{subfixture_id}"
            return f"{base_type}:{patch_target_id}"

        def ensure_record(
            fixture_id: int | None,
            *,
            channel_id: int | None = None,
            subfixture_id: int | None = None,
            ma_fixture_id: int | None = None,
            ma_channel_id: int | None = None,
            patch_target_type: str | None = None,
            patch_target_id: int | None = None,
            patch_target_key_value: str | None = None,
        ) -> FixtureRecord:
            resolved_target_type = patch_target_type or ("channel" if channel_id is not None and fixture_id is None else "fixture")
            resolved_target_id = patch_target_id if patch_target_id is not None else (channel_id if resolved_target_type == "channel" else fixture_id)
            key = patch_target_key_value or patch_target_key(resolved_target_type, resolved_target_id, subfixture_id)
            if key not in registry:
                registry[key] = FixtureRecord(
                    fixture_id=fixture_id if fixture_id is not None else (resolved_target_id or 0),
                    channel_id=channel_id,
                    subfixture_id=subfixture_id,
                    ma_fixture_id=ma_fixture_id,
                    ma_channel_id=ma_channel_id,
                    patch_target_type=resolved_target_type,
                    patch_target_id=resolved_target_id,
                    patch_target_key=key,
                )
            return registry[key]

        patched_keys: set[str] = set()

        for patch in self.patch_fixtures:
            record = ensure_record(
                patch.fixture_id,
                channel_id=patch.channel_id,
                subfixture_id=patch.subfixture_id,
                ma_fixture_id=patch.ma_fixture_id,
                ma_channel_id=patch.ma_channel_id,
                patch_target_type=patch.patch_target_type,
                patch_target_id=patch.patch_target_id,
                patch_target_key_value=patch.patch_target_key,
            )
            record.name = patch.name or record.name
            record.label = patch.label or record.label
            record.ma_fixture_id = patch.ma_fixture_id if patch.ma_fixture_id is not None else record.ma_fixture_id
            record.ma_channel_id = patch.ma_channel_id if patch.ma_channel_id is not None else record.ma_channel_id
            record.source_object_type = patch.source_object_type or record.source_object_type
            record.source_object_id = patch.source_object_id if patch.source_object_id is not None else record.source_object_id
            target_name = "Channel" if record.patch_target_type == "channel" else "Fixture"
            if record.patch_target_type == "subfixture":
                target_name = "Subfixture"
            base_id = record.patch_target_id if record.patch_target_id is not None else record.fixture_id
            record.display_name = patch.label or patch.name or record.display_name or f"{target_name} {base_id}"
            record.fixture_type = patch.fixture_type or record.fixture_type
            record.mode = patch.mode or record.mode
            record.patch = patch.patch or record.patch
            record.universe = patch.universe or record.universe
            record.address = patch.address or record.address
            record.raw_address = patch.raw_address or record.raw_address
            record.footprint = patch.footprint if patch.footprint is not None else record.footprint
            record.react_to_grandmaster = patch.react_to_grandmaster if patch.react_to_grandmaster is not None else record.react_to_grandmaster
            record.color = patch.color or record.color
            record.pos_x = patch.pos_x or record.pos_x
            record.pos_y = patch.pos_y or record.pos_y
            record.pos_z = patch.pos_z or record.pos_z
            record.rot_x = patch.rot_x or record.rot_x
            record.rot_y = patch.rot_y or record.rot_y
            record.rot_z = patch.rot_z or record.rot_z
            record.scale_x = patch.scale_x or record.scale_x
            record.scale_y = patch.scale_y or record.scale_y
            record.scale_z = patch.scale_z or record.scale_z
            if patch.source_file and patch.source_file not in record.source_files:
                record.source_files.append(patch.source_file)
            if record.patch_target_key:
                patched_keys.add(record.patch_target_key)

        used_in_cues: set[str] = set()
        used_in_presets: set[str] = set()
        referenced_in_atoms: set[str] = set()

        for sequence in self.sequences:
            for cue in sequence.cues:
                for target_key in cue.patch_target_keys:
                    fixture_id = None
                    channel_id = None
                    patch_target_type = "fixture"
                    patch_target_id = None
                    parts = target_key.split(":")
                    if len(parts) >= 2:
                        patch_target_type = parts[0] or "fixture"
                        if parts[1].isdigit():
                            patch_target_id = int(parts[1])
                    if patch_target_type == "channel":
                        channel_id = patch_target_id
                    else:
                        fixture_id = patch_target_id
                    record = ensure_record(
                        fixture_id,
                        channel_id=channel_id,
                        ma_fixture_id=fixture_id,
                        ma_channel_id=channel_id,
                        patch_target_type=patch_target_type,
                        patch_target_id=patch_target_id,
                        patch_target_key_value=target_key,
                    )
                    target_name = "Channel" if record.patch_target_type == "channel" else "Fixture"
                    record.display_name = record.display_name or f"{target_name} {record.patch_target_id or record.fixture_id}"
                    used_in_cues.add(target_key)
                for atom in cue.values:
                    target_key = atom.patch_target_key
                    if target_key or atom.fixture_id is not None or atom.channel_id is not None:
                        record = ensure_record(
                            atom.fixture_id,
                            channel_id=atom.channel_id,
                            subfixture_id=atom.subfixture_id,
                            ma_fixture_id=atom.fixture_id,
                            ma_channel_id=atom.channel_id,
                            patch_target_type=atom.patch_target_type,
                            patch_target_id=atom.patch_target_id,
                            patch_target_key_value=target_key,
                        )
                        target_name = "Channel" if record.patch_target_type == "channel" else "Fixture"
                        record.display_name = record.display_name or f"{target_name} {record.patch_target_id or record.fixture_id}"
                        referenced_in_atoms.add(record.patch_target_key or target_key or f"fixture:{record.fixture_id}")

        for preset in self.presets:
            for target_key in preset.patch_target_keys:
                fixture_id = None
                channel_id = None
                patch_target_type = "fixture"
                patch_target_id = None
                parts = target_key.split(":")
                if len(parts) >= 2:
                    patch_target_type = parts[0] or "fixture"
                    if parts[1].isdigit():
                        patch_target_id = int(parts[1])
                if patch_target_type == "channel":
                    channel_id = patch_target_id
                else:
                    fixture_id = patch_target_id
                record = ensure_record(
                    fixture_id,
                    channel_id=channel_id,
                    ma_fixture_id=fixture_id,
                    ma_channel_id=channel_id,
                    patch_target_type=patch_target_type,
                    patch_target_id=patch_target_id,
                    patch_target_key_value=target_key,
                )
                target_name = "Channel" if record.patch_target_type == "channel" else "Fixture"
                record.display_name = record.display_name or f"{target_name} {record.patch_target_id or record.fixture_id}"
                used_in_presets.add(target_key)
            for atom in preset.values:
                target_key = atom.patch_target_key
                if target_key or atom.fixture_id is not None or atom.channel_id is not None:
                    record = ensure_record(
                        atom.fixture_id,
                        channel_id=atom.channel_id,
                        subfixture_id=atom.subfixture_id,
                        ma_fixture_id=atom.fixture_id,
                        ma_channel_id=atom.channel_id,
                        patch_target_type=atom.patch_target_type,
                        patch_target_id=atom.patch_target_id,
                        patch_target_key_value=target_key,
                    )
                    target_name = "Channel" if record.patch_target_type == "channel" else "Fixture"
                    record.display_name = record.display_name or f"{target_name} {record.patch_target_id or record.fixture_id}"
                    used_in_presets.add(record.patch_target_key or target_key or f"fixture:{record.fixture_id}")

        for record_key, record in registry.items():
            record.flags = {
                "is_patched": record_key in patched_keys,
                "is_used_in_cues": record_key in used_in_cues,
                "is_used_in_presets": record_key in used_in_presets,
                "has_spatial_data": any(value not in (None, "") for value in (record.pos_x, record.pos_y, record.pos_z)),
                "has_patch_data": bool(record.patch or record.universe or record.address),
                "has_fixture_type": bool(record.fixture_type),
                "referenced_in_atoms": record_key in referenced_in_atoms,
                "is_channel": record.patch_target_type == "channel",
                "is_subfixture": record.patch_target_type == "subfixture",
                "is_fixture": record.patch_target_type == "fixture",
            }

        return [
            record.to_dict()
            for _, record in sorted(
                registry.items(),
                key=lambda item: (
                    str(item[1].patch_target_type or "fixture"),
                    int(item[1].patch_target_id or item[1].fixture_id or 0),
                    int(item[1].subfixture_id or 0),
                    item[0],
                ),
            )
        ]

    def build_reference_registry(self) -> list[dict[str, Any]]:
        refs: list[NormalizedReference] = []
        preset_numbers = {preset.number for preset in self.presets if preset.number}
        group_numbers = {group.number for group in self.groups if group.number}
        effect_numbers = {effect.number for effect in self.effects if effect.number}
        sequence_numbers = {sequence.number for sequence in self.sequences if sequence.number}

        def target_exists(target: str | None) -> bool | None:
            if not target or ":" not in target:
                return None
            target_type, target_id = target.split(":", 1)
            if target_type == "preset":
                return target_id in preset_numbers
            if target_type == "group":
                return target_id in group_numbers
            if target_type == "effect":
                return target_id in effect_numbers
            if target_type == "sequence":
                return target_id in sequence_numbers
            return None

        def display_from_target(target: str | None) -> str | None:
            if not target:
                return None
            if ":" not in target:
                return target
            target_type, target_id = target.split(":", 1)
            if target_type == "preset":
                return target_id
            return target
        def register(owner_type: str, owner_id: str, atom: ValueAtom, source_file: str | None) -> None:
            if atom.value_type == "hard":
                return
            target = atom.reference_target
            refs.append(
                NormalizedReference(
                    owner_type=owner_type,
                    owner_id=owner_id,
                    kind=atom.value_type,
                    target=target,
                    display=atom.reference_display or display_from_target(target),
                    raw_reference=atom.raw_reference or atom.raw_value,
                    confidence=atom.reference_confidence,
                    scope=atom.reference_scope,
                    fixture_id=atom.fixture_id,
                    channel_id=atom.channel_id,
                    subfixture_id=atom.subfixture_id,
                    patch_target_type=atom.patch_target_type,
                    patch_target_id=atom.patch_target_id,
                    patch_target_key=atom.patch_target_key,
                    attribute=atom.attribute,
                    target_exists=target_exists(target),
                    source_path=atom.source_path,
                    source_file=source_file,
                )
            )

        for sequence in self.sequences:
            for cue in sequence.cues:
                for atom in cue.values:
                    register("cue", cue.id, atom, cue.source_file)
                for ref in cue.references:
                    display = display_from_target(ref)
                    refs.append(
                        NormalizedReference(
                            owner_type="cue",
                            owner_id=cue.id,
                            kind=ref.split(":", 1)[0] + "_ref" if ":" in ref else "reference",
                            target=ref,
                            display=display,
                            raw_reference=ref,
                            confidence=1.0,
                            scope="explicit",
                            target_exists=target_exists(ref),
                            source_file=cue.source_file,
                        )
                    )

        for preset in self.presets:
            for atom in preset.values:
                register("preset", preset.id, atom, preset.source_file)
            for ref in preset.references:
                display = display_from_target(ref)
                refs.append(
                    NormalizedReference(
                        owner_type="preset",
                        owner_id=preset.id,
                        kind=ref.split(":", 1)[0] + "_ref" if ":" in ref else "reference",
                        target=ref,
                        display=display,
                        raw_reference=ref,
                        confidence=1.0,
                        scope="explicit",
                        target_exists=target_exists(ref),
                        source_file=preset.source_file,
                    )
                )
        return [ref.to_dict() for ref in refs]

    def build_object_index(self) -> dict[str, Any]:
        return {
            "sequence_numbers": sorted([sequence.number for sequence in self.sequences if sequence.number], key=str),
            "preset_numbers": sorted([preset.number for preset in self.presets if preset.number], key=str),
            "group_numbers": sorted([group.number for group in self.groups if group.number], key=str),
            "effect_numbers": sorted([effect.number for effect in self.effects if effect.number], key=str),
            "fixture_ids": sorted([
                fixture["fixture_id"]
                for fixture in self.build_fixture_registry()
                if fixture.get("patch_target_type") != "channel"
            ]),
            "channel_ids": sorted([fixture["channel_id"] for fixture in self.build_fixture_registry() if fixture.get("channel_id") is not None]),
            "patch_target_keys": sorted([fixture["patch_target_key"] for fixture in self.build_fixture_registry() if fixture.get("patch_target_key")]),
        }

    def build_warnings(self) -> list[dict[str, Any]]:
        warnings: list[dict[str, Any]] = list(self.warnings)
        fixture_registry = self.build_fixture_registry()
        references = self.build_reference_registry()
        seen: set[tuple[Any, ...]] = set()

        def freeze(value: Any) -> Any:
            if isinstance(value, dict):
                return tuple(sorted((str(key), freeze(item)) for key, item in value.items()))
            if isinstance(value, (list, tuple)):
                return tuple(freeze(item) for item in value)
            if isinstance(value, set):
                return tuple(sorted(freeze(item) for item in value))
            return value

        def warning_humanization(kind: str, subject: str, details: str, extra: dict[str, Any]) -> tuple[str, str, str | None]:
            patch_target_key = str(extra.get("patch_target_key") or subject or "").strip()
            patch_target_type = str(extra.get("patch_target_type") or "").strip()
            patch_label = str(extra.get("display_name") or details or subject or "").strip()
            patch_value = str(extra.get("patch") or "").strip()
            target = patch_label or patch_target_key or "objekt"

            if kind == "orphan_patch_fixture":
                return (
                    "Zapatchovaný target se v analyzovaných datech show nepoužívá.",
                    f"Target {target} je v patchi, ale v načtených cues ani presetech na něj nebyla nalezena žádná vazba.",
                    "Pokud má být používaný, zkontrolujte, že jste exportovali všechny sequence a presety. Pokud používaný být nemá, jde spíš o informativní upozornění.",
                )
            if kind == "fixture_used_without_patch_data":
                return (
                    "Používaný target nemá patch informace.",
                    f"Target {target} se v show používá, ale chybí mu adresa nebo jiné patch metadata.",
                    "Zkontrolujte patch export a to, jestli daný objekt opravdu existuje v exportovaných fixture/channel souborech.",
                )
            if kind == "patch_target_without_address":
                return (
                    "Target nemá přiřazenou patch adresu.",
                    f"Target {target} je v patch exportu, ale není u něj uvedená žádná DMX adresa.",
                    "Pokud má světlo svítit nebo být ovládané z konzole, přiřaďte mu patch adresu a export zopakujte.",
                )
            if kind == "fixture_used_without_type":
                return (
                    "Používaný target nemá určený typ zařízení.",
                    f"Target {target} se v show používá, ale analyzátor u něj nenašel fixture type.",
                    "Bez typu zařízení bude horší další analýza atributů, presetů a konzistence programování.",
                )
            if kind == "duplicate_patch_address":
                patch_desc = f" na adrese {patch_value}" if patch_value else ""
                return (
                    "Více targetů sdílí stejnou patch adresu.",
                    f"Analyzátor našel více targetů{patch_desc}, což často znamená kolizi v patchi nebo záměrné sdílení jedné DMX adresy.",
                    "Ověřte, jestli jde o záměr, nebo o omyl v patchi.",
                )
            if kind == "missing_target_object":
                target_ref = str(extra.get("target") or details or "").strip()
                return (
                    "Reference míří na objekt, který nebyl načten.",
                    f"Analyzátor našel odkaz na {target_ref}, ale odpovídající objekt v exportech nenašel.",
                    "Zkontrolujte, jestli nechybí některý export presetů, groups, effects nebo sequences.",
                )
            if kind == "unresolved_reference":
                attribute = str(extra.get("attribute") or "").strip()
                raw_reference = str(extra.get("raw_reference") or "").strip()
                what = f" atributu {attribute}" if attribute else ""
                return (
                    "Nepodařilo se rozpoznat odkaz ve value datech.",
                    f"Analyzátor nedokázal bezpečně určit, na co odkazuje hodnota{what}: {raw_reference or details}.",
                    "Může jít o neobvyklý formát exportu nebo o hodnotu, kterou parser zatím neumí spolehlivě klasifikovat.",
                )
            if kind == "inferred_reference":
                target_ref = str(extra.get("target") or details or "").strip()
                return (
                    "Reference byla odhadnuta, ne přečtena úplně jistě.",
                    f"Analyzátor odhadl, že hodnota míří na {target_ref}, ale jistota není stoprocentní.",
                    "Berte to jako měkčí upozornění. Výsledek může být správně, jen není potvrzený explicitní strukturou exportu.",
                )
            if kind == "empty_preset":
                return (
                    "Preset je prázdný.",
                    f"Preset {target} neobsahuje hodnoty, reference ani fixture vazby.",
                    "Může jít o nedokončený preset nebo o objekt, který je v poolu, ale reálně se nepoužívá.",
                )
            if kind == "unused_preset":
                return (
                    "Preset není nikde použitý.",
                    f"Preset {target} byl načten, ale analyzátor nenašel žádné použití v show.",
                    "Pokud je to pracovní nebo odložený preset, je to v pořádku. Jinak může jít o nevyužitý obsah v poolu.",
                )
            return (
                kind.replace("_", " ").capitalize(),
                details or subject or kind,
                None,
            )

        def add_warning(kind: str, severity: str, subject: str, details: str, **extra: Any) -> None:
            key = (kind, severity, subject, details, tuple(sorted((name, freeze(value)) for name, value in extra.items())))
            if key in seen:
                return
            seen.add(key)
            title, message, suggestion = warning_humanization(kind, subject, details, extra)
            warnings.append(
                {
                    "kind": kind,
                    "severity": severity,
                    "subject": subject,
                    "details": details,
                    "title": title,
                    "message": message,
                    "suggestion": suggestion,
                    **extra,
                }
            )

        for reference in references:
            target = reference.get("target")
            owner_type = reference.get("owner_type")
            owner_id = reference.get("owner_id")
            attribute = reference.get("attribute")
            raw_reference = reference.get("raw_reference")
            confidence = reference.get("confidence")
            scope = reference.get("scope")
            if not target:
                add_warning(
                    "unresolved_reference",
                    "high",
                    f"{owner_type}:{owner_id}",
                    f"attribute={attribute or '-'} raw={raw_reference or '-'}",
                    owner_type=owner_type,
                    owner_id=owner_id,
                    attribute=attribute,
                    raw_reference=raw_reference,
                )
                continue
            if confidence is not None and float(confidence) < 1.0:
                add_warning(
                    "inferred_reference",
                    "low",
                    f"{owner_type}:{owner_id}",
                    f"{target} via {scope or 'inferred'}",
                    owner_type=owner_type,
                    owner_id=owner_id,
                    target=target,
                    attribute=attribute,
                    confidence=confidence,
                    scope=scope,
                )
            if reference.get("target_exists") is False:
                add_warning(
                    "missing_target_object",
                    "high",
                    f"{owner_type}:{owner_id}",
                    f"missing target {target}",
                    owner_type=owner_type,
                    owner_id=owner_id,
                    target=target,
                    attribute=attribute,
                    raw_reference=raw_reference,
                )

        patch_buckets: dict[str, list[dict[str, Any]]] = {}
        for fixture in fixture_registry:
            fixture_id = fixture["fixture_id"]
            patch_target_key = fixture.get("patch_target_key") or f"fixture:{fixture_id}"
            flags = fixture.get("flags", {})
            display_name = fixture.get("display_name") or fixture.get("label") or fixture.get("name") or patch_target_key
            used = bool(flags.get("is_used_in_cues") or flags.get("is_used_in_presets"))
            if flags.get("is_patched") and not flags.get("has_patch_data"):
                add_warning(
                    "patch_target_without_address",
                    "medium" if used else "low",
                    patch_target_key,
                    display_name,
                    fixture_id=fixture_id,
                    patch_target_key=patch_target_key,
                    patch_target_type=fixture.get("patch_target_type"),
                    channel_id=fixture.get("channel_id"),
                    display_name=display_name,
                )
            if used and not flags.get("has_patch_data"):
                add_warning(
                    "fixture_used_without_patch_data",
                    "high",
                    patch_target_key,
                    display_name,
                    fixture_id=fixture_id,
                    patch_target_key=patch_target_key,
                    patch_target_type=fixture.get("patch_target_type"),
                    channel_id=fixture.get("channel_id"),
                    display_name=display_name,
                )
            if used and not flags.get("has_fixture_type"):
                add_warning(
                    "fixture_used_without_type",
                    "medium",
                    patch_target_key,
                    display_name,
                    fixture_id=fixture_id,
                    patch_target_key=patch_target_key,
                    patch_target_type=fixture.get("patch_target_type"),
                    channel_id=fixture.get("channel_id"),
                    display_name=display_name,
                )
            if flags.get("is_patched") and not used:
                if not flags.get("has_patch_data"):
                    continue
                add_warning(
                    "orphan_patch_fixture",
                    "low",
                    patch_target_key,
                    display_name,
                    fixture_id=fixture_id,
                    patch_target_key=patch_target_key,
                    patch_target_type=fixture.get("patch_target_type"),
                    channel_id=fixture.get("channel_id"),
                    display_name=display_name,
                )
            patch_value = str(fixture.get("patch") or "").strip()
            if patch_value:
                patch_buckets.setdefault(patch_value, []).append(fixture)

        for patch_value, fixtures in patch_buckets.items():
            if len(fixtures) < 2:
                continue
            fixture_ids = [fixture.get("fixture_id") for fixture in fixtures]
            patch_target_keys = [fixture.get("patch_target_key") for fixture in fixtures]
            add_warning(
                "duplicate_patch_address",
                "high",
                f"patch:{patch_value}",
                f"Targets {', '.join(str(key or fixture_id) for key, fixture_id in zip(patch_target_keys, fixture_ids))}",
                patch=patch_value,
                fixture_ids=fixture_ids,
                patch_target_keys=patch_target_keys,
            )

        used_preset_numbers: set[str] = set()
        for reference in references:
            target = str(reference.get("target") or "")
            if target.startswith("preset:"):
                used_preset_numbers.add(target.split(":", 1)[1])

        for preset in self.presets:
            preset_number = preset.number or preset.id
            display_name = preset.name or f"Preset {preset_number}"
            if not preset.values and not preset.references and not preset.fixture_ids:
                add_warning(
                    "empty_preset",
                    "medium",
                    f"preset:{preset_number}",
                    display_name,
                    preset_id=preset.id,
                    preset_number=preset.number,
                )
            if preset.number and preset.number not in used_preset_numbers:
                add_warning(
                    "unused_preset",
                    "low",
                    f"preset:{preset.number}",
                    display_name,
                    preset_id=preset.id,
                    preset_number=preset.number,
                )

        return warnings

    def to_model_v2(self) -> dict[str, Any]:
        fixtures = self.build_fixture_registry()
        fixture_types: dict[str, dict[str, Any]] = {}
        patch_summary = {
            "total_targets": len(fixtures),
            "fixture_targets": sum(1 for fixture in fixtures if fixture.get("patch_target_type") == "fixture"),
            "channel_targets": sum(1 for fixture in fixtures if fixture.get("patch_target_type") == "channel"),
            "subfixture_targets": sum(1 for fixture in fixtures if fixture.get("patch_target_type") == "subfixture"),
            "patched_targets": sum(1 for fixture in fixtures if fixture.get("flags", {}).get("is_patched")),
            "targets_with_usage": sum(
                1
                for fixture in fixtures
                if fixture.get("flags", {}).get("is_used_in_cues") or fixture.get("flags", {}).get("is_used_in_presets")
            ),
            "unpatched_used_targets": sum(
                1
                for fixture in fixtures
                if (fixture.get("flags", {}).get("is_used_in_cues") or fixture.get("flags", {}).get("is_used_in_presets"))
                and not fixture.get("flags", {}).get("has_patch_data")
            ),
        }
        for fixture in fixtures:
            fixture_type = fixture.get("fixture_type")
            if not fixture_type:
                continue
            bucket = fixture_types.setdefault(
                fixture_type,
                {
                    "fixture_type": fixture_type,
                    "modes": [],
                    "fixture_ids": [],
                    "channel_ids": [],
                    "patch_target_keys": [],
                    "target_types": [],
                    "count": 0,
                },
            )
            mode = fixture.get("mode")
            if mode and mode not in bucket["modes"]:
                bucket["modes"].append(mode)
            if fixture.get("patch_target_type") == "channel":
                if fixture.get("channel_id") is not None:
                    bucket["channel_ids"].append(fixture["channel_id"])
            else:
                bucket["fixture_ids"].append(fixture["fixture_id"])
            patch_target_key = fixture.get("patch_target_key")
            if patch_target_key and patch_target_key not in bucket["patch_target_keys"]:
                bucket["patch_target_keys"].append(patch_target_key)
            target_type = fixture.get("patch_target_type")
            if target_type and target_type not in bucket["target_types"]:
                bucket["target_types"].append(target_type)
            bucket["count"] += 1

        references = self.build_reference_registry()
        warnings = self.build_warnings()

        return {
            "model_version": 2,
            "show": {
                "main_sequence_numbers": self.main_sequence_numbers,
                "sequence_count": len(self.sequences),
                "preset_count": len(self.presets),
                "group_count": len(self.groups),
                "effect_count": len(self.effects),
                "patch_fixture_count": len(self.patch_fixtures),
            },
            "patch_summary": patch_summary,
            "fixtures": fixtures,
            "fixture_types": list(fixture_types.values()),
            "sequences": [sequence.to_dict() for sequence in self.sequences],
            "presets": [preset.to_dict() for preset in self.presets],
            "groups": [group.to_dict() for group in self.groups],
            "effects": [effect.to_dict() for effect in self.effects],
            "relationships": [relationship.to_dict() for relationship in self.relationships],
            "references": references,
            "object_index": self.build_object_index(),
            "source_index": {
                "sequence_sources": sorted({sequence.source_file for sequence in self.sequences if sequence.source_file}),
                "preset_sources": sorted({preset.source_file for preset in self.presets if preset.source_file}),
                "group_sources": sorted({group.source_file for group in self.groups if group.source_file}),
                "effect_sources": sorted({effect.source_file for effect in self.effects if effect.source_file}),
                "patch_sources": sorted({patch.source_file for patch in self.patch_fixtures if patch.source_file}),
                "generic_sources": sorted({obj.source_file for obj in self.generic_objects if obj.source_file}),
            },
            "warnings": warnings,
        }
