# grandMA2 Audit Report

## Dependency map
- Cues analyzed: 2

## Preset heatmap
- Preset 1.5: cues=1, sequences=1, status=single_cue, duplicates=0
- Preset 2.7: cues=1, sequences=1, status=single_cue, duplicates=0

## Consistency issues
- mixed_control_mode: Robe LEDWash 600 / Dimmer | hard_atoms=2, preset_refs=1, fixtures=2, cues=2

## Risk hotspots
- Seq 1 Cue 1 Blackout | score=2 | mixed hard and preset control

## Cue quality
- Seq 1 Cue 1 | score=24 | hard-heavy cue (4 hard values); mixed fixture control on 1 fixtures
- Seq 1 Cue 2 | score=0 | stable cue profile

## Worst blocks

## Fixture inconsistency
- Fixture 101 Dimmer | hard=2 | preset=1 | mixed=1

## Hard vs preset balance
- Seq 1 Cue 1 | Fixture 101 | mode=mixed | hard=1 | presets=1
- Seq 1 Cue 1 | Fixture 102 | mode=mixed | hard=1 | presets=1
- Seq 1 Cue 1 | Fixture 103 | mode=mixed | hard=1 | presets=1
- Seq 1 Cue 2 | Fixture 101 | mode=hard_only | hard=1 | presets=0
- Seq 1 Cue 2 | Fixture 102 | mode=hard_only | hard=1 | presets=0
- Seq 1 Cue 2 | Fixture 103 | mode=hard_only | hard=1 | presets=0
