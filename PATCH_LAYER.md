# Patch Layer for GrAIndMA

This document describes the normalized patch foundation used by GrAIndMA when it ingests grandMA2 patch exports.

## Input Analysis

### Lua plugin behavior

The patch helper in [lua/export_patch.lua](/c:/Users/lukas/Downloads/ma2_show_analyzer/ma2_show_analyzer/lua/export_patch.lua) now exports two datasets:

- `"<prefix>_fixture_patch"` from `Export Fixture 1 Thru <maxFixture> ... /style=csv /transform /o`
- `"<prefix>_channel_patch"` from `Export Channel 1 Thru <maxChannel> ... /style=csv /transform /o`

It also lets the operator:

- choose the filename prefix
- define the maximum exported fixture range
- define the maximum exported channel range
- choose the target drive before export

### Export limits

The export is practical and robust, but not perfect:

- it depends on range-based export, so missing objects outside the entered max range are invisible
- grandMA2 transform output is not guaranteed to keep the same column names across versions
- empty slots are silently skipped by MA export, so the export is sparse by design
- fixture and channel pools use different identity domains, but their numeric IDs may overlap
- the transform export can produce CSV in some environments and XML-with-CSV stylesheet metadata in others, so the parser must accept both

### What can be reliably extracted

From both fixture and channel patch exports we can reliably derive:

- target identity: fixture or channel
- numeric target ID
- name / label
- fixture type name
- mode number
- patched DMX address
- normalized `universe.address`
- source file

From XML exports we can additionally extract:

- raw absolute MA patch address
- DMX footprint by counting exported channels inside `SubFixture`
- `react_to_grandmaster`
- display color
- position, rotation, and scaling

### Fixture export characteristics

In the provided [CH_F_fixture_patch.xml](/c:/Users/lukas/Downloads/ma2_show_analyzer/ma2_show_analyzer/exports/CH_F_fixture_patch.xml):

- 8 fixture targets were exported
- `fixture_id` range is `1..8`
- all fixtures are type `3 Robin Spiider Mode 3`
- each exported target has 25 channel nodes in its `SubFixture`

### Channel export characteristics

In the provided [CH_F_channel_patch.xml](/c:/Users/lukas/Downloads/ma2_show_analyzer/ma2_show_analyzer/exports/CH_F_channel_patch.xml):

- 12 channel targets were exported
- `channel_id` range is `1..12`
- exported targets are dimmers of type `2 Dimmer 00`
- each exported target has a single channel node in its `SubFixture`

### Expected differences between fixture and channel exports

- fixture rows identify objects by `fixture_id`
- channel rows identify objects by `channel_id`
- the same numeric value may exist in both pools at once
- footprint is usually much larger for fixtures than for channels
- fixture exports tend to represent intelligent fixtures, while channel exports often represent conventionals or dimmer-based devices

The sample data demonstrates an important real-world collision:

- fixture IDs `1..8` exist
- channel IDs `1..8` also exist

That means `1` cannot be treated as a globally unique patch identity.

## Unified Data Model

The canonical identity for patch targets is:

- `fixture:<id>`
- `channel:<id>`
- `subfixture:<fixture_id>:<subfixture_id>`

This identity is stored as `patch_target_key`.

### Normalized patch target fields

Each normalized patch record contains:

- `patch_target_key`: canonical unique key for GrAIndMA
- `patch_target_type`: `fixture`, `channel`, or `subfixture`
- `patch_target_id`: numeric ID within its domain
- `source_object_type`: original MA pool type that produced the row
- `source_object_id`: original object ID from that pool
- `fixture_id`: legacy compatibility field used by older analyzer paths
- `channel_id`
- `subfixture_id`
- `name`
- `label`
- `display_name`
- `fixture_type`
- `mode`
- `patch`
- `universe`
- `address`
- `raw_address`
- `footprint`
- `react_to_grandmaster`
- `color`
- `pos_x`, `pos_y`, `pos_z`
- `rot_x`, `rot_y`, `rot_z`
- `scale_x`, `scale_y`, `scale_z`
- `source_files`
- `flags`

### Why this model is safe for production use

- fixture and channel exports can be merged without overwriting each other
- one application-wide identity works across patch, cues, presets, groups, and effects
- sparse exports still yield stable records
- raw export metadata is preserved for debugging and future enrichment
- normalized fields stay compact enough for backend filtering and UI tables

## Parser and Merge Strategy

The parser in [parser.py](/c:/Users/lukas/Downloads/ma2_show_analyzer/ma2_show_analyzer/src/ma2showanalyzer/parser.py) now follows these rules:

1. Accept both patch CSV and patch XML exports.
2. Detect whether the row/node represents a fixture or a channel.
3. Build a canonical `patch_target_key`.
4. Normalize raw MA absolute addresses to `universe.address`.
5. Extract extra XML-only fields such as footprint and spatial metadata.
6. Merge records by canonical target identity, not by bare numeric ID.
7. Publish a consolidated registry for downstream GrAIndMA features.

## Output Datasets

The reporting layer writes patch-oriented backend datasets:

- `patch_registry.json`
- `patch_registry.csv`
- `patch_fixtures.json`
- `patch_fixtures.csv`
- `patch_summary.json`

`patch_registry.*` is the recommended primary backend source for GrAIndMA.

## Practical Recommendation for GrAIndMA

Inside the app, treat `patch_target_key` as the only authoritative ID for patch targets.

Use:

- `patch_registry.json` for backend/API loading
- `patch_registry.csv` for debug, ad-hoc inspection, and spreadsheet work
- `patch_summary.json` for dashboard counters
- `patch_fixtures.json` only as the raw parsed layer before final registry consolidation
