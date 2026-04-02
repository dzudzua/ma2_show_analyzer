from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable
import re
import xml.etree.ElementTree as ET

from .models import Cue, Effect, GenericObject, Group, PatchFixture, Preset, Sequence, ShowData, ValueAtom
from .utils import (
    RE_CUE,
    RE_EFFECT,
    RE_FIXTURE,
    RE_GROUP,
    RE_PRESET,
    RE_PRESET_COMPACT,
    RE_SEQUENCE,
    RE_TRIGGER,
    normalize_key,
    parse_xml_file,
    safe_text,
    strip_ns,
    text_blob_from_element,
    unique_preserve,
)


TIME_KEYS = {"fade", "fadetime", "fadefromx", "fadetox", "delay", "delaytime", "trigtime", "triggertime", "basicfade", "basicdelay"}
TRIGGER_KEYS = {"trigger", "triggermode", "cuetrigger", "cmdtrigger"}
NAME_KEYS = {"name", "label"}
NUMBER_KEYS = {"no", "number", "index", "nr"}
SEQUENCE_KEYS = {"sequence", "sequenceno", "seq", "seqno"}
CUE_KEYS = {"cue", "cueno", "cuenumber"}
PRESET_KEYS = {"preset", "presetno"}
GROUP_KEYS = {"group", "groupno"}
EFFECT_KEYS = {"effect", "effectno"}
FIXTURE_KEYS = {"fixture", "fixtureid", "fid", "fixid", "channel", "channelid", "channel_id", "chid", "chaid", "subfixture", "subfixtureid"}
VALUE_HINT_KEYS = {"value", "dmx", "absolute", "relative", "phys", "encoder"}
COMMAND_KEYS = {"cmd", "command", "macrocmd"}
PART_KEYS = {"part", "partno"}
PATCH_TYPE_KEYS = {"fixturetype", "fixturetypename", "fixturetype.name", "type", "fixtype", "classname"}
PATCH_MODE_KEYS = {"mode", "fixturemode"}
PATCH_PATCH_KEYS = {"patch", "patchaddress"}
PATCH_UNIVERSE_KEYS = {"universe", "dmxuniverse"}
PATCH_ADDRESS_KEYS = {"address", "dmxaddress"}


class ParseFolderError(RuntimeError):
    pass


class XMLShowParser:
    def __init__(self) -> None:
        self._generic_counter = 0

    def parse_folder(self, input_dir: Path, recursive: bool = False, glob: str = "*.xml") -> ShowData:
        show = ShowData()
        parse_errors: list[str] = []
        files = sorted(input_dir.rglob(glob) if recursive else input_dir.glob(glob))
        for path in files:
            if not path.is_file():
                continue
            try:
                self.parse_file(path, show)
            except Exception as exc:  # pragma: no cover - resilience by design
                show.generic_objects.append(
                    GenericObject(
                        id=f"parse-error:{path.name}",
                        object_type="parse_error",
                        name=path.name,
                        metadata={"error": str(exc)},
                        source_file=str(path),
                    )
                )
                parse_errors.append(f"{path.name}: {exc}")
        csv_files = sorted(input_dir.rglob("*.csv") if recursive else input_dir.glob("*.csv"))
        for path in csv_files:
            if not path.is_file():
                continue
            try:
                self.parse_patch_file(path, show)
            except Exception as exc:  # pragma: no cover - resilience by design
                show.generic_objects.append(
                    GenericObject(
                        id=f"patch-parse-error:{path.name}",
                        object_type="patch_parse_error",
                        name=path.name,
                        metadata={"error": str(exc)},
                        source_file=str(path),
                    )
                )
                parse_errors.append(f"{path.name}: {exc}")
        if parse_errors:
            joined_errors = "\n".join(f"- {item}" for item in parse_errors)
            raise ParseFolderError(f"One or more input files could not be parsed:\n{joined_errors}")
        from .analyzer import ShowAnalyzer
        show = ShowAnalyzer().analyze(show)
        return show

    def _merge_meta_maps(self, primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        for source in (primary or {}, secondary or {}):
            for key, value in source.items():
                if isinstance(value, list):
                    for item in value:
                        self._store_meta_value(merged, key, safe_text(item))
                else:
                    self._store_meta_value(merged, key, safe_text(value))
        return merged

    def _cue_identity(self, cue: Cue) -> tuple[str, str]:
        return (str(cue.cue_number or ""), str(cue.part or ""))

    def _score_cue(self, cue: Cue) -> int:
        scalar_score = sum(1 for value in (cue.name, cue.fade, cue.delay, cue.trigger, cue.trigger_time, cue.down_delay, cue.command, cue.part) if value not in (None, ""))
        return (
            scalar_score
            + len(cue.fixture_ids)
            + len(cue.channel_ids)
            + len(cue.patch_target_keys)
            + len(cue.references)
            + len(cue.values) * 2
            + len(cue.metadata)
        )

    def _merge_value_atoms(self, primary: list[ValueAtom], secondary: list[ValueAtom]) -> list[ValueAtom]:
        merged: list[ValueAtom] = []
        seen: set[tuple[Any, ...]] = set()
        for atom in [*(primary or []), *(secondary or [])]:
            key = (
                atom.attribute,
                atom.raw_value,
                atom.value_type,
                atom.fixture_id,
                atom.channel_id,
                atom.subfixture_id,
                atom.patch_target_key,
                atom.reference_target,
                tuple(atom.flags),
                atom.source_path,
            )
            if key in seen:
                continue
            seen.add(key)
            merged.append(atom)
        return merged

    def _merge_cues(self, existing: Cue, incoming: Cue) -> Cue:
        primary, secondary = (incoming, existing) if self._score_cue(incoming) >= self._score_cue(existing) else (existing, incoming)
        return Cue(
            id=primary.id,
            sequence_number=primary.sequence_number or secondary.sequence_number,
            cue_number=primary.cue_number or secondary.cue_number,
            name=primary.name or secondary.name,
            fade=primary.fade or secondary.fade,
            delay=primary.delay or secondary.delay,
            trigger=primary.trigger or secondary.trigger,
            trigger_time=primary.trigger_time or secondary.trigger_time,
            down_delay=primary.down_delay or secondary.down_delay,
            command=primary.command or secondary.command,
            part=primary.part or secondary.part,
            fixture_ids=unique_preserve([*(existing.fixture_ids or []), *(incoming.fixture_ids or [])]),
            channel_ids=unique_preserve([*(existing.channel_ids or []), *(incoming.channel_ids or [])]),
            patch_target_keys=unique_preserve([*(existing.patch_target_keys or []), *(incoming.patch_target_keys or [])]),
            references=unique_preserve([*(existing.references or []), *(incoming.references or [])]),
            values=self._merge_value_atoms(existing.values, incoming.values),
            metadata=self._merge_meta_maps(existing.metadata, incoming.metadata),
            source_file=primary.source_file or secondary.source_file,
            is_main_cue_list=existing.is_main_cue_list or incoming.is_main_cue_list,
        )

    def _merge_sequences(self, existing: Sequence, incoming: Sequence) -> Sequence:
        primary, secondary = (incoming, existing) if len(incoming.cues) >= len(existing.cues) else (existing, incoming)
        cue_map: dict[tuple[str, str], Cue] = {}
        cue_order: list[tuple[str, str]] = []
        for cue in [*(existing.cues or []), *(incoming.cues or [])]:
            key = self._cue_identity(cue)
            if key not in cue_map:
                cue_map[key] = cue
                cue_order.append(key)
            else:
                cue_map[key] = self._merge_cues(cue_map[key], cue)
        merged = Sequence(
            id=primary.id,
            number=primary.number or secondary.number,
            name=primary.name or secondary.name,
            source_file=primary.source_file or secondary.source_file,
            cues=[cue_map[key] for key in cue_order],
            metadata=self._merge_meta_maps(existing.metadata, incoming.metadata),
            is_main_cue_list=existing.is_main_cue_list or incoming.is_main_cue_list,
        )
        merged_sources = unique_preserve([source for source in [existing.source_file, incoming.source_file] if source])
        if len(merged_sources) > 1:
            merged.metadata["merged_sources"] = merged_sources
        return merged

    def parse_file(self, path: Path, show: ShowData) -> None:
        root = parse_xml_file(path)
        object_type = self._detect_object_type(root, path)

        if object_type == "sequence":
            self._parse_sequences(root, path, show)
        elif object_type == "preset":
            self._parse_presets(root, path, show)
        elif object_type == "group":
            self._parse_groups(root, path, show)
        elif object_type == "effect":
            self._parse_effects(root, path, show)
        elif self._looks_like_patch_xml(path, root):
            self._parse_patch_xml(root, path, show)
        else:
            self._parse_generic(root, path, show)

    def _is_main_sequence_file(self, path: Path) -> bool:
        return path.stem.lower().endswith("_main_sequences")

    def _looks_like_patch_xml(self, path: Path, root: ET.Element) -> bool:
        stem = path.stem.lower()
        if stem.endswith("_patch") or "patch" in stem or "fixture" in stem:
            return True
        return normalize_key(strip_ns(root.tag)) in {"fixture", "fixtureschedule", "fixturetype", "channel"}

    def _looks_like_patch_csv(self, path: Path, fieldnames: list[str]) -> bool:
        stem = path.stem.lower()
        normalized = {normalize_key(name) for name in fieldnames if name}
        if "patch" in stem and any(name in normalized for name in {"fixtureid", "fixture", "id", "fid", "channelid"}):
            return True
        return "fixturetype" in normalized or ("patch" in normalized and ("fixtureid" in normalized or "fixid" in normalized))

    def _extract_patch_row_ids(self, row: dict[str, str]) -> tuple[int | None, int | None, int | None]:
        fixture_id = None
        channel_id = None
        subfixture_id = None
        for key in ("fixture_id", "fixtureid", "fixid", "fid", "id"):
            value = safe_text(row.get(key))
            if value.isdigit():
                fixture_id = int(value)
                break
        for key in ("channelid", "channel_id", "chid", "chaid"):
            value = safe_text(row.get(key))
            if value.isdigit():
                channel_id = int(value)
                break
        for key in ("subfixtureid", "subfixture_id", "subfixture"):
            value = safe_text(row.get(key))
            if value.isdigit():
                subfixture_id = int(value)
                break
        return fixture_id, channel_id, subfixture_id

    def _resolve_patch_target(
        self,
        *,
        fixture_id: int | None = None,
        channel_id: int | None = None,
        subfixture_id: int | None = None,
    ) -> tuple[str, int | None, str | None]:
        if channel_id is not None:
            return "channel", channel_id, f"channel:{channel_id}"
        if fixture_id is not None and subfixture_id is not None:
            return "subfixture", fixture_id, f"subfixture:{fixture_id}:{subfixture_id}"
        if fixture_id is not None:
            return "fixture", fixture_id, f"fixture:{fixture_id}"
        if channel_id is not None:
            return "channel", channel_id, f"channel:{channel_id}"
        return "fixture", None, None

    def _register_patch_fixture(self, show: ShowData, patch: PatchFixture) -> None:
        patch_identity = (
            patch.patch_target_key,
            patch.patch_target_type,
            patch.patch_target_id,
            patch.subfixture_id,
            patch.source_object_type,
            patch.source_object_id,
        )
        for idx, existing in enumerate(show.patch_fixtures):
            existing_identity = (
                existing.patch_target_key,
                existing.patch_target_type,
                existing.patch_target_id,
                existing.subfixture_id,
                existing.source_object_type,
                existing.source_object_id,
            )
            if existing_identity != patch_identity:
                continue
            existing_score = sum(1 for value in existing.to_dict().values() if value not in (None, "", {}, []))
            new_score = sum(1 for value in patch.to_dict().values() if value not in (None, "", {}, []))
            if new_score >= existing_score:
                show.patch_fixtures[idx] = patch
            return
        show.patch_fixtures.append(patch)

    def _patch_fixture_from_meta(self, meta: dict[str, Any], path: Path) -> PatchFixture | None:
        fixture_id_text = self._first_match(meta, {"fixtureid", "fid", "fixture", "id"})
        channel_id_text = self._first_match(meta, {"channelid", "channel", "chid", "chaid"})
        subfixture_id_text = self._first_match(meta, {"subfixtureid", "subfixture"})
        if (not fixture_id_text or not fixture_id_text.isdigit()) and (not channel_id_text or not channel_id_text.isdigit()):
            return None
        fixture_id = int(fixture_id_text) if fixture_id_text and fixture_id_text.isdigit() else None
        channel_id = int(channel_id_text) if channel_id_text and channel_id_text.isdigit() else None
        subfixture_id = int(subfixture_id_text) if subfixture_id_text and subfixture_id_text.isdigit() else None
        patch_target_type, patch_target_id, patch_target_key = self._resolve_patch_target(
            fixture_id=fixture_id,
            channel_id=channel_id,
            subfixture_id=subfixture_id,
        )
        universe = self._first_match(meta, PATCH_UNIVERSE_KEYS)
        address = self._first_match(meta, PATCH_ADDRESS_KEYS)
        patch = self._first_match(meta, PATCH_PATCH_KEYS)
        if not patch and universe and address:
            patch = f"{universe}.{address}"
        return PatchFixture(
            fixture_id=fixture_id if fixture_id is not None else (patch_target_id or 0),
            channel_id=channel_id,
            subfixture_id=subfixture_id,
            ma_fixture_id=fixture_id,
            ma_channel_id=channel_id,
            patch_target_type=patch_target_type,
            patch_target_id=patch_target_id,
            patch_target_key=patch_target_key,
            source_object_type=patch_target_type,
            source_object_id=patch_target_id,
            name=self._first_match(meta, {"name", "fixturename"}),
            label=self._first_match(meta, {"label"}),
            fixture_type=self._first_match(meta, PATCH_TYPE_KEYS),
            mode=self._first_match(meta, PATCH_MODE_KEYS),
            patch=patch,
            universe=universe,
            address=address,
            raw_address=self._first_match(meta, {"rawaddress", "address"}),
            pos_x=self._first_match(meta, {"posx", "positionx", "locationx", "x"}),
            pos_y=self._first_match(meta, {"posy", "positiony", "locationy", "y"}),
            pos_z=self._first_match(meta, {"posz", "positionz", "locationz", "z"}),
            rot_x=self._first_match(meta, {"rotx", "rotationx"}),
            rot_y=self._first_match(meta, {"roty", "rotationy"}),
            rot_z=self._first_match(meta, {"rotz", "rotationz"}),
            scale_x=self._first_match(meta, {"scalex", "scalingx"}),
            scale_y=self._first_match(meta, {"scaley", "scalingy"}),
            scale_z=self._first_match(meta, {"scalez", "scalingz"}),
            source_file=str(path),
            metadata=meta,
        )

    def _address_to_patch(self, address_text: str | None) -> tuple[str | None, str | None, str | None]:
        if not address_text:
            return None, None, None
        if address_text.isdigit():
            absolute = int(address_text)
            if absolute <= 0:
                return None, None, address_text
            universe = ((absolute - 1) // 512) + 1
            address = ((absolute - 1) % 512) + 1
            return f"{universe}.{address:03d}", str(universe), str(address)
        if "." in address_text:
            universe, _, address = address_text.partition(".")
            return address_text, universe or None, address or None
        return address_text, None, None

    def parse_patch_file(self, path: Path, show: ShowData) -> None:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            sample = handle.read(4096)
            handle.seek(0)
            delimiter = ";"
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=";,")
                delimiter = dialect.delimiter
            except csv.Error:
                pass

            reader = csv.DictReader(handle, delimiter=delimiter)
            if not reader.fieldnames:
                return
            fieldnames = [safe_text(name) for name in reader.fieldnames]
            if not self._looks_like_patch_csv(path, fieldnames):
                return

            for raw_row in reader:
                row = {normalize_key(key): safe_text(value) for key, value in raw_row.items() if key is not None}
                fixture_id, channel_id, subfixture_id = self._extract_patch_row_ids(row)
                if fixture_id is None and channel_id is None:
                    continue
                patch_target_type, patch_target_id, patch_target_key = self._resolve_patch_target(
                    fixture_id=fixture_id,
                    channel_id=channel_id,
                    subfixture_id=subfixture_id,
                )
                universe = row.get("universe") or row.get("dmxuniverse")
                address = row.get("address") or row.get("dmxaddress")
                patch = row.get("patch") or row.get("patchaddress")
                if not patch and universe and address:
                    patch = f"{universe}.{address}"
                patch_fixture = PatchFixture(
                    fixture_id=fixture_id if fixture_id is not None else (patch_target_id or 0),
                    channel_id=channel_id,
                    subfixture_id=subfixture_id,
                    ma_fixture_id=fixture_id,
                    ma_channel_id=channel_id,
                    patch_target_type=patch_target_type,
                    patch_target_id=patch_target_id,
                    patch_target_key=patch_target_key,
                    source_object_type=patch_target_type,
                    source_object_id=patch_target_id,
                    name=row.get("name") or row.get("fixturename"),
                    label=row.get("label") or row.get("name"),
                    fixture_type=row.get("fixturetype") or row.get("type"),
                    mode=row.get("mode") or row.get("fixturemode"),
                    patch=patch,
                    universe=universe,
                    address=address,
                    raw_address=row.get("rawaddress") or row.get("address"),
                    source_file=str(path),
                    metadata=row,
                )
                self._register_patch_fixture(show, patch_fixture)

    def _parse_patch_xml(self, root: ET.Element, path: Path, show: ShowData) -> None:
        fixture_nodes = list(self._iter_candidates(root, {"fixture"}))
        if not fixture_nodes:
            fixture_nodes = [root]

        for node in fixture_nodes:
            meta = self._collect_meta(node)
            for key, value in node.attrib.items():
                meta[normalize_key(key)] = safe_text(value)

            fixture_id_text = safe_text(node.attrib.get("fixture_id") or node.attrib.get("fix_id"))
            channel_id_text = safe_text(node.attrib.get("channel_id") or node.attrib.get("channelid"))
            subfixture_id_text = safe_text(node.attrib.get("subfixture_id") or node.attrib.get("subfixtureid"))
            if not fixture_id_text.isdigit() and not channel_id_text.isdigit():
                patch_fixture = self._patch_fixture_from_meta(meta, path)
                if patch_fixture is not None:
                    self._register_patch_fixture(show, patch_fixture)
                continue
            fixture_id = int(fixture_id_text) if fixture_id_text.isdigit() else None
            channel_id = int(channel_id_text) if channel_id_text.isdigit() else None
            subfixture_id = int(subfixture_id_text) if subfixture_id_text.isdigit() else None
            patch_target_type, patch_target_id, patch_target_key = self._resolve_patch_target(
                fixture_id=fixture_id,
                channel_id=channel_id,
                subfixture_id=subfixture_id,
            )
            source_object_type = "channel" if channel_id is not None and fixture_id is None else "fixture"
            source_object_id = channel_id if source_object_type == "channel" else fixture_id

            patch_text = None
            universe = None
            address = None
            raw_address = None
            patch_node = next((child for child in node.iter() if normalize_key(strip_ns(child.tag)) == "patch"), None)
            if patch_node is not None:
                address_node = next((child for child in patch_node if normalize_key(strip_ns(child.tag)) == "address"), None)
                if address_node is not None:
                    raw_address = safe_text(address_node.text)
                    patch_text, universe, address = self._address_to_patch(raw_address)

            fixture_type = None
            fixture_type_node = next((child for child in node if normalize_key(strip_ns(child.tag)) == "fixturetype"), None)
            if fixture_type_node is not None:
                fixture_type = safe_text(fixture_type_node.attrib.get("name"))
                mode_text = safe_text(next((child.text for child in fixture_type_node if normalize_key(strip_ns(child.tag)) == "no"), ""))
            else:
                mode_text = None

            subfixture_node = next((child for child in node if normalize_key(strip_ns(child.tag)) == "subfixture"), None)
            footprint = None
            if subfixture_node is not None:
                footprint = sum(1 for child in subfixture_node if normalize_key(strip_ns(child.tag)) == "channel")

            absolute_position = next((child for child in node.iter() if normalize_key(strip_ns(child.tag)) == "absoluteposition"), None)
            location_node = None
            rotation_node = None
            scaling_node = None
            if absolute_position is not None:
                location_node = next((child for child in absolute_position if normalize_key(strip_ns(child.tag)) == "location"), None)
                rotation_node = next((child for child in absolute_position if normalize_key(strip_ns(child.tag)) == "rotation"), None)
                scaling_node = next((child for child in absolute_position if normalize_key(strip_ns(child.tag)) == "scaling"), None)

            react_to_grandmaster = None
            color = None
            if subfixture_node is not None:
                react_attr = safe_text(subfixture_node.attrib.get("react_to_grandmaster")).lower()
                if react_attr in {"true", "false"}:
                    react_to_grandmaster = react_attr == "true"
                color = safe_text(subfixture_node.attrib.get("color"))

            patch_fixture = PatchFixture(
                fixture_id=fixture_id if fixture_id is not None else (patch_target_id or 0),
                channel_id=channel_id,
                subfixture_id=subfixture_id,
                ma_fixture_id=fixture_id,
                ma_channel_id=channel_id,
                patch_target_type=patch_target_type,
                patch_target_id=patch_target_id,
                patch_target_key=patch_target_key,
                source_object_type=source_object_type,
                source_object_id=source_object_id,
                name=safe_text(node.attrib.get("name")) or self._first_match(meta, {"name", "label"}),
                label=safe_text(node.attrib.get("name")) or self._first_match(meta, {"label", "name"}),
                fixture_type=fixture_type or self._first_match(meta, PATCH_TYPE_KEYS),
                mode=mode_text or self._first_match(meta, PATCH_MODE_KEYS),
                patch=patch_text,
                universe=universe,
                address=address,
                raw_address=raw_address,
                footprint=footprint,
                react_to_grandmaster=react_to_grandmaster,
                color=color,
                pos_x=safe_text(location_node.attrib.get("x")) if location_node is not None else None,
                pos_y=safe_text(location_node.attrib.get("y")) if location_node is not None else None,
                pos_z=safe_text(location_node.attrib.get("z")) if location_node is not None else None,
                rot_x=safe_text(rotation_node.attrib.get("x")) if rotation_node is not None else None,
                rot_y=safe_text(rotation_node.attrib.get("y")) if rotation_node is not None else None,
                rot_z=safe_text(rotation_node.attrib.get("z")) if rotation_node is not None else None,
                scale_x=safe_text(scaling_node.attrib.get("x")) if scaling_node is not None else None,
                scale_y=safe_text(scaling_node.attrib.get("y")) if scaling_node is not None else None,
                scale_z=safe_text(scaling_node.attrib.get("z")) if scaling_node is not None else None,
                source_file=str(path),
                metadata=meta,
            )
            self._register_patch_fixture(show, patch_fixture)

    def _register_sequence(self, show: ShowData, sequence: Sequence) -> None:
        if sequence.is_main_cue_list and sequence.number:
            show.main_sequence_numbers = unique_preserve(show.main_sequence_numbers + [sequence.number])

        existing_index = None
        for idx, existing in enumerate(show.sequences):
            if existing.number == sequence.number and existing.number is not None:
                existing_index = idx
                break

        if existing_index is None:
            show.sequences.append(sequence)
            return

        existing = show.sequences[existing_index]
        if sequence.is_main_cue_list and not existing.is_main_cue_list:
            show.sequences[existing_index] = self._merge_sequences(existing, sequence)
            return
        if sequence.is_main_cue_list == existing.is_main_cue_list:
            show.sequences[existing_index] = self._merge_sequences(existing, sequence)

    def _detect_object_type(self, root: ET.Element, path: Path) -> str:
        root_tag = normalize_key(strip_ns(root.tag))
        tags = [normalize_key(strip_ns(elem.tag)) for elem in root.iter()]
        tag_counts = {
            "sequence": sum(1 for tag in tags if tag == "sequence"),
            "preset": sum(1 for tag in tags if tag == "preset"),
            "group": sum(1 for tag in tags if tag == "group"),
            "effect": sum(1 for tag in tags if tag == "effect"),
            "cue": sum(1 for tag in tags if tag == "cue"),
        }

        if root_tag in {"sequence", "sequ"}:
            return "sequence"
        if root_tag in {"preset", "group", "effect"}:
            return root_tag
        if tag_counts["sequence"] or tag_counts["cue"]:
            return "sequence"
        if tag_counts["preset"]:
            return "preset"
        if tag_counts["group"]:
            return "group"
        if tag_counts["effect"]:
            return "effect"

        hint = f"{path.stem} {root_tag} {text_blob_from_element(root)[:3000]}".lower()
        for candidate in ("sequence", "preset", "group", "effect"):
            if candidate in hint:
                return candidate
        return "generic"

    def _iter_candidates(self, root: ET.Element, wanted: set[str]) -> Iterable[ET.Element]:
        for elem in root.iter():
            key = normalize_key(strip_ns(elem.tag))
            if key == "sequ":
                key = "sequence"
            if key in wanted:
                yield elem

    def _store_meta_value(self, meta: dict[str, Any], key: str, value: str) -> None:
        if not value:
            return
        if key not in meta:
            meta[key] = value
            return
        existing = meta[key]
        if isinstance(existing, list):
            if value not in existing:
                existing.append(value)
            return
        if existing != value:
            meta[key] = [existing, value]

    def _collect_meta(self, elem: ET.Element) -> dict[str, Any]:
        meta: dict[str, Any] = {}
        for k, v in elem.attrib.items():
            self._store_meta_value(meta, normalize_key(k), safe_text(v))
        for child in elem:
            ckey = normalize_key(strip_ns(child.tag))
            text = safe_text(child.text)
            self._store_meta_value(meta, ckey, text)
            for k, v in child.attrib.items():
                self._store_meta_value(meta, f"{ckey}.{normalize_key(k)}", safe_text(v))
        return meta

    def _first_match(self, values: dict[str, Any], keys: set[str]) -> str | None:
        for k, v in values.items():
            if k not in keys or not v:
                continue
            if isinstance(v, list):
                for item in v:
                    if item:
                        return str(item)
                continue
            return str(v)
        return None

    def _is_nil_element(self, elem: ET.Element) -> bool:
        for key, value in elem.attrib.items():
            normalized_key = normalize_key(strip_ns(key))
            if normalized_key == "nil" and safe_text(value).lower() == "true":
                return True
        return False

    def _extract_named_numbered(self, elem: ET.Element, fallback_type: str) -> tuple[str | None, str | None, dict[str, Any]]:
        meta = self._collect_meta(elem)
        name = self._first_match(meta, NAME_KEYS)
        number = None
        blob = text_blob_from_element(elem)

        if fallback_type == "cue":
            number_node = next((child for child in elem if normalize_key(strip_ns(child.tag)) == "number"), None)
            if number_node is not None:
                cue_main = safe_text(number_node.attrib.get("number"))
                cue_sub = safe_text(number_node.attrib.get("sub_number"))
                if cue_main:
                    if cue_sub and cue_sub not in {"0", "000"}:
                        cue_sub_value = cue_sub.rstrip("0") or "0"
                        number = f"{cue_main}.{cue_sub_value}"
                    else:
                        number = cue_main

        if not number:
            if fallback_type == "sequence":
                number = self._first_match(meta, {"no", "number", "nr"})
                if not number:
                    raw_index = self._first_match(meta, {"index"})
                    if raw_index and raw_index.isdigit():
                        number = str(int(raw_index) + 1)
            else:
                number = self._first_match(meta, NUMBER_KEYS)
        if not number:
            if fallback_type == "sequence":
                m = RE_SEQUENCE.search(blob)
                if m:
                    number = m.group(1)
            elif fallback_type == "cue":
                m = RE_CUE.search(blob)
                if m:
                    number = m.group(1)
            elif fallback_type == "effect":
                m = RE_EFFECT.search(blob)
                if m:
                    number = m.group(1)
            elif fallback_type == "group":
                m = RE_GROUP.search(blob)
                if m:
                    number = m.group(1)
            elif fallback_type == "preset":
                m = RE_PRESET.search(blob)
                if m:
                    number = f"{m.group(1)}.{m.group(2)}"
        return name, number, meta

    def _extract_fixtures(self, elem: ET.Element) -> list[int]:
        found: list[int] = []
        for x in elem.iter():
            for k, v in x.attrib.items():
                nk = normalize_key(k)
                if nk in FIXTURE_KEYS and safe_text(v).isdigit():
                    found.append(int(safe_text(v)))
                else:
                    for m in RE_FIXTURE.finditer(f"{k}={v}"):
                        found.append(int(m.group(1)))
            if x.text:
                for m in RE_FIXTURE.finditer(x.text):
                    found.append(int(m.group(1)))
        return unique_preserve(found)

    def _extract_channel_ids(self, elem: ET.Element) -> list[int]:
        found: list[int] = []
        for x in elem.iter():
            for k, v in x.attrib.items():
                nk = normalize_key(k)
                if nk in {"channelid", "channel_id", "chid", "chaid"} and safe_text(v).isdigit():
                    found.append(int(safe_text(v)))
        return unique_preserve(found)

    def _extract_patch_target_keys(self, elem: ET.Element) -> list[str]:
        found: list[str] = []
        for x in elem.iter():
            fixture_id = None
            channel_id = None
            subfixture_id = None
            for k, v in x.attrib.items():
                nk = normalize_key(k)
                value = safe_text(v)
                if not value.isdigit():
                    continue
                if nk in {"fixture", "fixtureid", "fid", "fixid"}:
                    fixture_id = int(value)
                elif nk in {"channelid", "channel_id", "chid", "chaid"}:
                    channel_id = int(value)
                elif nk in {"subfixture", "subfixtureid"}:
                    subfixture_id = int(value)
            _, _, target_key = self._resolve_patch_target(
                fixture_id=fixture_id,
                channel_id=channel_id,
                subfixture_id=subfixture_id,
            )
            if target_key:
                found.append(target_key)
        return unique_preserve(found)

    def _extract_references(self, elem: ET.Element) -> list[str]:
        refs: list[str] = []
        blob = text_blob_from_element(elem)
        for m in RE_PRESET.finditer(blob):
            refs.append(f"preset:{m.group(1)}.{m.group(2)}")
        for m in RE_GROUP.finditer(blob):
            refs.append(f"group:{m.group(1)}")
        for m in RE_EFFECT.finditer(blob):
            refs.append(f"effect:{m.group(1)}")
        for m in RE_SEQUENCE.finditer(blob):
            refs.append(f"sequence:{m.group(1)}")
        return unique_preserve(refs)

    def _extract_value_atoms(self, elem: ET.Element) -> list[ValueAtom]:
        atoms: list[ValueAtom] = []

        def patch_target_from_node(node: ET.Element) -> tuple[int | None, int | None, int | None, str | None, int | None, str | None]:
            fixture_id = None
            channel_id = None
            subfixture_id = None
            for k, v in node.attrib.items():
                value = safe_text(v)
                if not value.isdigit():
                    continue
                key = normalize_key(k)
                if key in {"fixture", "fixtureid", "fid", "fixid"}:
                    fixture_id = int(value)
                elif key in {"channelid", "channel_id", "chid", "chaid"}:
                    channel_id = int(value)
                elif key in {"subfixture", "subfixtureid"}:
                    subfixture_id = int(value)
                elif key in FIXTURE_KEYS and fixture_id is None:
                    fixture_id = int(value)
            patch_target_type, patch_target_id, patch_target_key = self._resolve_patch_target(
                fixture_id=fixture_id,
                channel_id=channel_id,
                subfixture_id=subfixture_id,
            )
            return fixture_id, channel_id, subfixture_id, patch_target_type, patch_target_id, patch_target_key

        def attribute_from_node(node: ET.Element) -> str | None:
            for key in ("attribute_name", "attribute"):
                value = safe_text(node.attrib.get(key))
                if value:
                    return value
            if normalize_key(strip_ns(node.tag)) == "attribute":
                value = safe_text(node.attrib.get("name"))
                if value:
                    return value
            return None

        def explicit_reference_from_node(node: ET.Element) -> tuple[str, str | None]:
            for child in node:
                child_tag = normalize_key(strip_ns(child.tag))
                if child_tag == "preset":
                    numbers = [safe_text(grandchild.text) for grandchild in child if normalize_key(strip_ns(grandchild.tag)) == "no" and safe_text(grandchild.text)]
                    if len(numbers) >= 3 and numbers[1].isdigit() and numbers[2].isdigit():
                        preset_type = numbers[1]
                        preset_no = numbers[2]
                        return "preset_ref", f"preset:{int(preset_type)}.{int(preset_no)}"
                    if len(numbers) >= 2:
                        preset_type = numbers[0]
                        preset_no = next((num for num in reversed(numbers[1:]) if num not in {"", "0"}), numbers[-1])
                        if preset_type.isdigit() and preset_no.isdigit():
                            return "preset_ref", f"preset:{int(preset_type)}.{int(preset_no)}"
                if child_tag == "group":
                    number = safe_text(child.attrib.get("index") or child.attrib.get("number") or child.text)
                    if number.isdigit():
                        return "group_ref", f"group:{int(number)}"
                if child_tag == "effect":
                    number = safe_text(child.attrib.get("index") or child.attrib.get("number") or child.text)
                    if number.isdigit():
                        return "effect_ref", f"effect:{int(number)}"
            return "unknown", None

        def classify_reference(
            raw: str,
            blob: str,
            explicit_target: tuple[str, str | None] | None = None,
            *,
            allow_compact: bool = True,
        ) -> tuple[str, str | None]:
            if explicit_target and explicit_target[1]:
                return explicit_target
            preset_match = RE_PRESET.search(blob)
            effect_match = RE_EFFECT.search(blob)
            group_match = RE_GROUP.search(blob)
            if preset_match:
                return "preset_ref", f"preset:{preset_match.group(1)}.{preset_match.group(2)}"
            if effect_match:
                return "effect_ref", f"effect:{effect_match.group(1)}"
            if group_match:
                return "group_ref", f"group:{group_match.group(1)}"
            if allow_compact:
                compact = RE_PRESET_COMPACT.fullmatch(raw)
                if compact and len(compact.group(2)) >= 4:
                    preset_type = int(compact.group(1))
                    if 0 <= preset_type <= 14:
                        return "preset_ref", f"preset:{compact.group(1)}.{compact.group(2)}"
            return "hard", None

        def reference_metadata(value_type: str, target: str | None, raw: str, explicit_target: tuple[str, str | None] | None = None) -> tuple[str | None, float | None, str | None]:
            if value_type == "hard":
                return None, None, None
            display = target
            confidence = 1.0 if explicit_target and explicit_target[1] else 0.85
            scope = "explicit" if explicit_target and explicit_target[1] else "inferred"
            if target and target.startswith("preset:"):
                display = target.split(":", 1)[1]
            elif target and target.startswith(("group:", "effect:", "sequence:")):
                display = target
            elif not target:
                display = raw
                confidence = 0.0
                scope = "unresolved"
            return display, confidence, scope

        def walk(node: ET.Element, path_stack: list[str]) -> None:
            current_tag = strip_ns(node.tag)
            path_stack.append(current_tag)
            normalized_tag = normalize_key(current_tag)
            attr_name = attribute_from_node(node)
            blob = " | ".join([safe_text(node.text)] + [f"{k}={v}" for k, v in node.attrib.items()])
            fixture_id, channel_id, subfixture_id, patch_target_type, patch_target_id, patch_target_key = patch_target_from_node(node)

            if normalized_tag in {"cuedata", "presetvalue"}:
                context_nodes = list(node.iter())
                for child in context_nodes:
                    child_fixture_id, child_channel_id, child_subfixture_id, child_target_type, child_target_id, child_target_key = patch_target_from_node(child)
                    fixture_id = fixture_id or child_fixture_id
                    channel_id = channel_id or child_channel_id
                    subfixture_id = subfixture_id or child_subfixture_id
                    patch_target_type = patch_target_type or child_target_type
                    patch_target_id = patch_target_id or child_target_id
                    patch_target_key = patch_target_key or child_target_key
                    attr_name = attr_name or attribute_from_node(child)
                    blob += " | " + " | ".join(f"{k}={v}" for k, v in child.attrib.items())
                explicit_target = explicit_reference_from_node(node)

                raw_values: list[tuple[str, str]] = []
                attr_value = safe_text(node.attrib.get("Value") or node.attrib.get("value"))
                if attr_value:
                    raw_values.append(("value", attr_value))
                for child in node:
                    child_tag = normalize_key(strip_ns(child.tag))
                    child_text = safe_text(child.text)
                    if child_tag == "value" and child_text:
                        raw_values.append(("value", child_text))

                for key, raw in raw_values:
                    value_type, target = classify_reference(raw, blob, explicit_target=explicit_target, allow_compact=False)
                    display, confidence, scope = reference_metadata(value_type, target, raw, explicit_target)
                    flags: list[str] = []
                    if normalize_key(key) in TIME_KEYS:
                        flags.append("timing")
                    atoms.append(
                        ValueAtom(
                            attribute=attr_name or key,
                            raw_value=raw,
                            value_type=value_type,
                            fixture_id=fixture_id,
                            channel_id=channel_id,
                            subfixture_id=subfixture_id,
                            patch_target_type=patch_target_type,
                            patch_target_id=patch_target_id,
                            patch_target_key=patch_target_key,
                            reference_target=target,
                            raw_reference=raw if value_type != "hard" else None,
                            reference_display=display,
                            reference_confidence=confidence,
                            reference_scope=scope,
                            flags=flags,
                            source_path="/".join(path_stack),
                        )
                    )
                path_stack.pop()
                return

            explicit_value_fields = []
            for k, v in node.attrib.items():
                if normalize_key(k) in VALUE_HINT_KEYS or normalize_key(k) in TIME_KEYS:
                    explicit_value_fields.append((k, safe_text(v)))
            if safe_text(node.text):
                explicit_value_fields.append(("text", safe_text(node.text)))

            for key, raw in explicit_value_fields:
                raw = raw.strip()
                if not raw:
                    continue
                value_type, target = classify_reference(raw, blob)
                display, confidence, scope = reference_metadata(value_type, target, raw)
                flags: list[str] = []
                if not re.search(r"[A-Za-z0-9]", raw):
                    continue
                if normalize_key(key) in TIME_KEYS:
                    flags.append("timing")
                atoms.append(
                    ValueAtom(
                        attribute=attr_name or key,
                        raw_value=raw,
                        value_type=value_type,
                        fixture_id=fixture_id,
                        channel_id=channel_id,
                        subfixture_id=subfixture_id,
                        patch_target_type=patch_target_type,
                        patch_target_id=patch_target_id,
                        patch_target_key=patch_target_key,
                        reference_target=target,
                        raw_reference=raw if value_type != "hard" else None,
                        reference_display=display,
                        reference_confidence=confidence,
                        reference_scope=scope,
                        flags=flags,
                        source_path="/".join(path_stack),
                    )
                )

            for child in node:
                walk(child, path_stack)
            path_stack.pop()

        walk(elem, [])
        dedup: dict[tuple[str | None, str | None, str, int | None], ValueAtom] = {}
        for atom in atoms:
            key = (
                atom.attribute,
                atom.raw_value,
                atom.value_type,
                atom.fixture_id,
                atom.channel_id,
                atom.subfixture_id,
                atom.patch_target_key,
                atom.reference_target,
                tuple(atom.flags),
                atom.source_path,
            )
            dedup[key] = atom
        return list(dedup.values())

    def _parse_sequences(self, root: ET.Element, path: Path, show: ShowData) -> None:
        sequence_nodes = list(self._iter_candidates(root, {"sequence"}))
        if not sequence_nodes:
            sequence_nodes = [root]
        is_main_sequence_file = self._is_main_sequence_file(path)

        for idx, seq_node in enumerate(sequence_nodes, start=1):
            name, number, meta = self._extract_named_numbered(seq_node, "sequence")
            if not number:
                number = str(idx)
            sequence = Sequence(
                id=f"sequence:{number}:{path.name}:{idx}",
                number=number,
                name=name or f"Sequence {number}",
                source_file=str(path),
                metadata=meta,
                is_main_cue_list=is_main_sequence_file,
            )

            cue_nodes = list(self._iter_candidates(seq_node, {"cue"}))
            if not cue_nodes and normalize_key(strip_ns(seq_node.tag)) == "cue":
                cue_nodes = [seq_node]
            cue_nodes = [cue_node for cue_node in cue_nodes if not self._is_nil_element(cue_node)]

            for cidx, cue_node in enumerate(cue_nodes, start=1):
                cname, cnum, cmeta = self._extract_named_numbered(cue_node, "cue")
                blob = text_blob_from_element(cue_node)
                cue_no = cnum or str(cidx)
                cue_part = next((child for child in cue_node if normalize_key(strip_ns(child.tag)) == "cuepart"), None)
                fade = self._first_match(cmeta, {"fade", "fadetime", "cuepart.basicfade", "basicfade"})
                delay = self._first_match(cmeta, {"delay", "delaytime", "cuepart.basicdelay", "basicdelay"})
                down_delay = self._first_match(cmeta, {"cuepart.basicdowndelay", "basicdowndelay"})
                trigger = self._first_match(cmeta, TRIGGER_KEYS)
                trigger_time = self._first_match(cmeta, {"trigtime", "triggertime", "trigger.dataf"})
                if not trigger:
                    trig_match = RE_TRIGGER.search(blob)
                    if trig_match:
                        trigger = trig_match.group(1)
                trigger_node = next((child for child in cue_node if normalize_key(strip_ns(child.tag)) == "trigger"), None)
                if trigger_node is not None:
                    if not trigger:
                        trigger = safe_text(trigger_node.attrib.get("type"))
                    if not trigger_time:
                        trigger_time = safe_text(trigger_node.attrib.get("data_f"))
                if not trigger:
                    trigger = "Go"
                command = self._first_match(cmeta, COMMAND_KEYS)
                part = self._first_match(cmeta, PART_KEYS)
                values = self._extract_value_atoms(cue_node)
                fixture_ids = unique_preserve(self._extract_fixtures(cue_node) + [a.fixture_id for a in values if a.fixture_id])
                channel_ids = unique_preserve(self._extract_channel_ids(cue_node) + [a.channel_id for a in values if a.channel_id])
                patch_target_keys = unique_preserve(self._extract_patch_target_keys(cue_node) + [a.patch_target_key for a in values if a.patch_target_key])
                refs = unique_preserve(self._extract_references(cue_node) + [a.reference_target for a in values if a.reference_target])
                cue = Cue(
                    id=f"cue:{number}:{cue_no}:{path.name}:{cidx}",
                    sequence_number=number,
                    cue_number=cue_no,
                    name=(safe_text(cue_part.attrib.get("name")) if cue_part is not None else None) or cname or f"Cue {cue_no}",
                    fade=fade,
                    delay=delay,
                    trigger=trigger,
                    trigger_time=trigger_time,
                    down_delay=down_delay,
                    command=command,
                    part=part,
                    fixture_ids=fixture_ids,
                    channel_ids=channel_ids,
                    patch_target_keys=[key for key in patch_target_keys if key],
                    references=[r for r in refs if r],
                    values=values,
                    metadata=cmeta,
                    source_file=str(path),
                    is_main_cue_list=is_main_sequence_file,
                )
                sequence.cues.append(cue)
            self._register_sequence(show, sequence)

    def _parse_presets(self, root: ET.Element, path: Path, show: ShowData) -> None:
        preset_nodes = list(self._iter_candidates(root, {"preset"}))
        if not preset_nodes:
            preset_nodes = [root]
        preset_type_from_filename = None
        filename_match = re.search(r"_preset_(\d+)$", path.stem.lower())
        if filename_match:
            preset_type_from_filename = filename_match.group(1)

        for idx, preset_node in enumerate(preset_nodes, start=1):
            name, number, meta = self._extract_named_numbered(preset_node, "preset")
            blob = text_blob_from_element(preset_node)
            preset_type = preset_type_from_filename
            if preset_type and number and number.isdigit():
                # grandMA2 preset pool XML stores slot positions in 0-based `index`,
                # while the visible preset number in the UI is 1-based within the pool.
                number = f"{preset_type}.{int(number) + 1}"
            if number and "." in number:
                preset_type = number.split(".", 1)[0]
            else:
                m = RE_PRESET.search(blob)
                if m:
                    preset_type = m.group(1)
                    number = f"{m.group(1)}.{m.group(2)}"
            if not number:
                if preset_type:
                    number = f"{preset_type}.{idx}"
                else:
                    number = str(idx)
            values = self._extract_value_atoms(preset_node)
            fixture_ids = unique_preserve(self._extract_fixtures(preset_node) + [a.fixture_id for a in values if a.fixture_id])
            channel_ids = unique_preserve(self._extract_channel_ids(preset_node) + [a.channel_id for a in values if a.channel_id])
            patch_target_keys = unique_preserve(self._extract_patch_target_keys(preset_node) + [a.patch_target_key for a in values if a.patch_target_key])
            refs = unique_preserve(self._extract_references(preset_node) + [a.reference_target for a in values if a.reference_target])
            preset = Preset(
                id=f"preset:{number or idx}:{path.name}:{idx}",
                preset_type=preset_type,
                number=number or str(idx),
                name=name or f"Preset {number or idx}",
                fixture_ids=fixture_ids,
                channel_ids=channel_ids,
                patch_target_keys=[key for key in patch_target_keys if key],
                references=[r for r in refs if r],
                values=values,
                metadata=meta,
                source_file=str(path),
            )
            show.presets.append(preset)

    def _parse_groups(self, root: ET.Element, path: Path, show: ShowData) -> None:
        group_nodes = list(self._iter_candidates(root, {"group"}))
        if not group_nodes:
            group_nodes = [root]
        for idx, group_node in enumerate(group_nodes, start=1):
            name, number, meta = self._extract_named_numbered(group_node, "group")
            fixture_ids = self._extract_fixtures(group_node)
            channel_ids = self._extract_channel_ids(group_node)
            patch_target_keys = self._extract_patch_target_keys(group_node)
            if not fixture_ids:
                blob = text_blob_from_element(group_node)
                fixture_ids = [int(x) for x in re.findall(r"\b(?:fixtureid|channelid|subfixtureid)\s*[=:]\s*(\d+)\b", blob, re.IGNORECASE)]
            group = Group(
                id=f"group:{number or idx}:{path.name}:{idx}",
                number=number or str(idx),
                name=name or f"Group {number or idx}",
                fixture_ids=unique_preserve(fixture_ids),
                channel_ids=unique_preserve(channel_ids),
                patch_target_keys=[key for key in unique_preserve(patch_target_keys) if key],
                metadata=meta,
                source_file=str(path),
            )
            show.groups.append(group)

    def _parse_effects(self, root: ET.Element, path: Path, show: ShowData) -> None:
        effect_nodes = list(self._iter_candidates(root, {"effect"}))
        if not effect_nodes:
            effect_nodes = [root]
        for idx, effect_node in enumerate(effect_nodes, start=1):
            name, number, meta = self._extract_named_numbered(effect_node, "effect")
            refs = self._extract_references(effect_node)
            fixture_ids = self._extract_fixtures(effect_node)
            channel_ids = self._extract_channel_ids(effect_node)
            patch_target_keys = self._extract_patch_target_keys(effect_node)
            effect = Effect(
                id=f"effect:{number or idx}:{path.name}:{idx}",
                number=number or str(idx),
                name=name or f"Effect {number or idx}",
                references=refs,
                fixture_ids=fixture_ids,
                channel_ids=channel_ids,
                patch_target_keys=[key for key in unique_preserve(patch_target_keys) if key],
                metadata=meta,
                source_file=str(path),
            )
            show.effects.append(effect)

    def _parse_generic(self, root: ET.Element, path: Path, show: ShowData) -> None:
        self._generic_counter += 1
        meta = self._collect_meta(root)
        show.generic_objects.append(
            GenericObject(
                id=f"generic:{self._generic_counter}:{path.name}",
                object_type=strip_ns(root.tag),
                number=meta.get("number") or meta.get("no") or str(self._generic_counter),
                name=meta.get("name") or path.stem,
                metadata=meta,
                source_file=str(path),
            )
        )
