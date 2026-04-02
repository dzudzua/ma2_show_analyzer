# grandMA2 Show Analysis

## Summary
- Main sequences: 1
- Main cue count: 2
- Presets loaded: 2
- Groups loaded: 1
- Effects loaded: 1
- Patch fixtures loaded: 3
- Used fixtures total: 3
- Used fixtures without patch mapping: 0
- Unified model export: `show_model_v2.json`
- Validation warnings: 5

## Top cues by hard values
- Cue 1 `Blackout`: 4 hard values, 3 fixtures, fade=0, trigger=go
- Cue 2 `Build`: 3 hard values, 3 fixtures, fade=2, trigger=follow

## Top fixtures by cue usage
- Fixture 101 `Front Left Wash`: type=Robe LEDWash 600, patch=1.1, cues=2, hard atoms=0
- Fixture 102 `Front Center Wash`: type=Robe LEDWash 600, patch=1.17, cues=2, hard atoms=1
- Fixture 103 `DS Center Spot`: type=Martin MAC Viper, patch=1.33, cues=2, hard atoms=1

## Hottest presets
- Preset 1.5 `Warm Front`: cues=1, sequences=1, fixtures=2, status=single_cue
- Preset 2.7 `DS Center`: cues=1, sequences=1, fixtures=1, status=single_cue

## Fixture coverage risks

## Risk hotspots
- Seq 1 Cue 1 Blackout: score=2 | mixed hard and preset control

## Worst cues
- Seq 1 Cue 1 `Blackout`: score=0 | stable cue profile
- Seq 1 Cue 2 `Build`: score=0 | stable cue profile

## Validation warnings
- Severity breakdown: high=1, medium=0, low=4
- Top kinds: inferred_reference=4, missing_target_object=1
- low: inferred_reference | cue:cue:1:1:demo_main_sequences.xml:1 | preset:1.5 via inferred
- low: inferred_reference | cue:cue:1:1:demo_main_sequences.xml:1 | preset:2.7 via inferred
- high: missing_target_object | cue:cue:1:1:demo_main_sequences.xml:1 | missing target sequence:2
- low: inferred_reference | cue:cue:1:2:demo_main_sequences.xml:2 | effect:12 via inferred
- low: inferred_reference | cue:cue:1:2:demo_main_sequences.xml:2 | group:3 via inferred
