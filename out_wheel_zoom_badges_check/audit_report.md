# grandMA2 Audit Report

## Dependency map
- Cues analyzed: 295

## Preset heatmap
- Preset 0.34: cues=21, sequences=1, status=active, duplicates=0
- Preset 0.34: cues=21, sequences=1, status=active, duplicates=0
- Preset 0.45: cues=18, sequences=1, status=active, duplicates=0
- Preset 4.10: cues=18, sequences=1, status=active, duplicates=0
- Preset 0.49: cues=9, sequences=2, status=active, duplicates=0
- Preset 0.49: cues=9, sequences=2, status=active, duplicates=0
- Preset 0.58: cues=7, sequences=2, status=active, duplicates=0
- Preset 0.58: cues=7, sequences=2, status=active, duplicates=0
- Preset 0.86: cues=6, sequences=5, status=active, duplicates=0
- Preset 0.26: cues=5, sequences=2, status=active, duplicates=0

## Consistency issues
- mixed_control_mode: 12 Robin LEDBeam 350 Mode 1 / COLORMIXER | hard_atoms=12, preset_refs=204, fixtures=12, cues=23
- mixed_control_mode: 12 Robin LEDBeam 350 Mode 1 / COLORRGB1 | hard_atoms=124, preset_refs=240, fixtures=12, cues=52
- mixed_control_mode: 12 Robin LEDBeam 350 Mode 1 / COLORRGB2 | hard_atoms=124, preset_refs=240, fixtures=12, cues=52
- mixed_control_mode: 12 Robin LEDBeam 350 Mode 1 / COLORRGB3 | hard_atoms=124, preset_refs=240, fixtures=12, cues=52
- mixed_control_mode: 12 Robin LEDBeam 350 Mode 1 / COLORRGB5 | hard_atoms=124, preset_refs=240, fixtures=12, cues=52
- mixed_control_mode: 12 Robin LEDBeam 350 Mode 1 / COLORTEMPERATURE | hard_atoms=12, preset_refs=204, fixtures=12, cues=23
- mixed_control_mode: 14 Hotbox RGBW 8 channel / COLORRGB1 | hard_atoms=21, preset_refs=12, fixtures=7, cues=11
- mixed_control_mode: 14 Hotbox RGBW 8 channel / COLORRGB2 | hard_atoms=21, preset_refs=12, fixtures=7, cues=11
- mixed_control_mode: 14 Hotbox RGBW 8 channel / COLORRGB3 | hard_atoms=21, preset_refs=12, fixtures=7, cues=11
- mixed_control_mode: 14 Hotbox RGBW 8 channel / COLORRGB5 | hard_atoms=21, preset_refs=12, fixtures=7, cues=11

## Risk hotspots
- Seq 10 Cue 1 lidi | score=10 | many hard values (142); touches many feature groups (6); mixed hard and preset control; depends on several presets (6); dimmer hard values present (26)
- Seq 10 Cue 36 9:46.888 | score=10 | many hard values (75); touches many feature groups (7); mixed hard and preset control; depends on several presets (9); dimmer hard values present (27)
- Seq 2 Cue 25 Vilda odchazi | score=10 | many hard values (66); touches many feature groups (6); mixed hard and preset control; depends on several presets (5)
- Seq 2 Cue 85 Dekovacka | score=10 | many hard values (84); touches many feature groups (6); mixed hard and preset control; depends on several presets (7); dimmer hard values present (62)
- Seq 10 Cue 103 blesk | score=9 | many hard values (48); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (24)
- Seq 10 Cue 106 DUHA | score=9 | many hard values (184); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (35)
- Seq 10 Cue 109 Blesk MIDI | score=9 | many hard values (302); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (30)
- Seq 10 Cue 27 beegees 6:37.6 | score=9 | many hard values (64); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (30)
- Seq 10 Cue 6 najezd strobo | score=9 | many hard values (49); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (15)
- Seq 10 Cue 75 Projede Lavka | score=9 | many hard values (33); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (28)
- Seq 10 Cue 81 disko gula dolu | score=9 | many hard values (64); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (13)
- Seq 10 Cue 89 koks KOUR GARAZ | score=9 | many hard values (77); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (49)
- Seq 10 Cue 98 Flo BLESK kdyz se vyfoti tereze | score=9 | many hard values (65); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (30)
- Seq 2 Cue 11 J. SOLO - 2:47 | score=9 | many hard values (38); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (10)
- Seq 2 Cue 18 Rackove rostazeny nohy 5:05 | score=9 | many hard values (63); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (14)

## Cue quality
- Seq 10 Cue 1 | score=91 | very hard-heavy cue (142 hard values); mixed programming in 24 fixture/family pairs; low similarity to neighbouring cues (0.01); hard values spike vs local block (142 vs avg 28.6); many zero/reset-like values (82); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 10 Cue 89 | score=91 | very hard-heavy cue (77 hard values); mixed programming in 11 fixture/family pairs; low similarity to neighbouring cues (0.02); hard values spike vs local block (77 vs avg 11.4); many zero/reset-like values (52); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 2 Cue 46 | score=91 | very hard-heavy cue (44 hard values); mixed programming in 8 fixture/family pairs; low similarity to neighbouring cues (0.02); hard values spike vs local block (44 vs avg 10.4); many zero/reset-like values (9); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 10 Cue 27 | score=83 | very hard-heavy cue (64 hard values); mixed programming in 8 fixture/family pairs; low similarity to neighbouring cues (0.01); hard values spike vs local block (64 vs avg 9.4); many zero/reset-like values (52); more mixed fixtures than neighbouring cues
- Seq 10 Cue 98 | score=83 | very hard-heavy cue (65 hard values); mixed programming in 8 fixture/family pairs; low similarity to neighbouring cues (0.07); hard values spike vs local block (65 vs avg 18.3); many zero/reset-like values (53); more mixed fixtures than neighbouring cues
- Seq 2 Cue 55 | score=83 | very hard-heavy cue (152 hard values); mixed programming in 4 fixture/family pairs; low similarity to neighbouring cues (0.12); hard values spike vs local block (152 vs avg 30.9); many zero/reset-like values (17); more mixed fixtures than neighbouring cues
- Seq 2 Cue 9 | score=83 | very hard-heavy cue (42 hard values); mixed programming in 12 fixture/family pairs; low similarity to neighbouring cues (0.06); hard values spike vs local block (42 vs avg 19.4); many zero/reset-like values (20); more mixed fixtures than neighbouring cues
- Seq 2 Cue 25 | score=76 | very hard-heavy cue (66 hard values); mixed programming in 25 fixture/family pairs; noticeable local outlier (0.27); hard values spike vs local block (66 vs avg 19.6); many zero/reset-like values (22); more mixed fixtures than neighbouring cues
- Seq 10 Cue 36 | score=75 | very hard-heavy cue (75 hard values); mixed programming in 6 fixture/family pairs; hard values spike vs local block (75 vs avg 13.6); many zero/reset-like values (61); touches unusually many feature groups (7); many preset refs combined with hard edits
- Seq 10 Cue 6 | score=73 | very hard-heavy cue (49 hard values); mixed programming in 12 fixture/family pairs; low similarity to neighbouring cues (0.03); hard values spike vs local block (49 vs avg 10.3); more mixed fixtures than neighbouring cues
- Seq 2 Cue 36 | score=73 | very hard-heavy cue (26 hard values); mixed programming in 9 fixture/family pairs; low similarity to neighbouring cues (0.07); hard values spike vs local block (26 vs avg 10.3); more mixed fixtures than neighbouring cues
- Seq 2 Cue 44 | score=69 | very hard-heavy cue (17 hard values); mixed programming in 4 fixture/family pairs; low similarity to neighbouring cues (0.03); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 10 Cue 103 | score=68 | very hard-heavy cue (48 hard values); mixed programming in 12 fixture/family pairs; hard values spike vs local block (48 vs avg 8.1); many zero/reset-like values (22); more mixed fixtures than neighbouring cues
- Seq 2 Cue 18 | score=68 | very hard-heavy cue (63 hard values); mixed programming in 26 fixture/family pairs; hard values spike vs local block (63 vs avg 13.6); many zero/reset-like values (22); more mixed fixtures than neighbouring cues
- Seq 2 Cue 86 | score=67 | very hard-heavy cue (199 hard values); mixed programming in 22 fixture/family pairs; low similarity to neighbouring cues (0.03); hard values spike vs local block (199 vs avg 75.2)

## Worst blocks
- Seq 2 cues 7 - 11 | avg=47.8 | high cues=2, avg hard=24.8, avg similarity=0.15
- Seq 2 cues 6 - 10 | avg=44.8 | high cues=2, avg hard=19.2, avg similarity=0.12
- Seq 2 cues 5 - 9 | avg=43.8 | high cues=2, avg hard=18.2, avg similarity=0.08
- Seq 2 cues 8 - 12 | avg=43.8 | high cues=2, avg hard=18.8, avg similarity=0.14
- Seq 2 cues 44 - 46.6 | avg=43.4 | high cues=2, avg hard=14.2, avg similarity=0.02
- Seq 2 cues 24 - 28 | avg=42.4 | high cues=2, avg hard=26.0, avg similarity=0.16
- Seq 2 cues 23 - 27 | avg=42.2 | high cues=2, avg hard=25.0, avg similarity=0.14
- Seq 2 cues 51 - 55 | avg=40.2 | high cues=2, avg hard=43.2, avg similarity=0.16
- Seq 2 cues 52 - 56 | avg=40.2 | high cues=2, avg hard=43.2, avg similarity=0.16
- Seq 10 cues 5 - 9 | avg=40.2 | high cues=2, avg hard=14.4, avg similarity=0.02

## Fixture inconsistency
- Fixture 101 Color | hard=15 | preset=31 | mixed=8
- Fixture 102 Color | hard=14 | preset=34 | mixed=8
- Fixture 201 Color | hard=15 | preset=25 | mixed=7
- Fixture 101 Position | hard=17 | preset=32 | mixed=6
- Fixture 102 Position | hard=15 | preset=35 | mixed=6
- Fixture 202 Color | hard=13 | preset=28 | mixed=6
- Fixture 201 Position | hard=16 | preset=25 | mixed=5
- Fixture 202 Position | hard=16 | preset=28 | mixed=5
- Fixture 21 Color | hard=12 | preset=30 | mixed=5
- Fixture 22 Color | hard=12 | preset=30 | mixed=5

## Hard vs preset balance
- Seq 2 Cue 85 | Fixture 104 | mode=mixed | hard=15 | presets=1
- Seq 2 Cue 85 | Fixture 103 | mode=mixed | hard=14 | presets=1
- Seq 2 Cue 25 | Fixture 102 | mode=mixed | hard=12 | presets=3
- Seq 2 Cue 18 | Fixture 102 | mode=mixed | hard=12 | presets=2
- Seq 2 Cue 18 | Fixture 202 | mode=mixed | hard=12 | presets=2
- Seq 2 Cue 25 | Fixture 101 | mode=mixed | hard=12 | presets=2
- Seq 2 Cue 18 | Fixture 101 | mode=mixed | hard=12 | presets=1
- Seq 2 Cue 18 | Fixture 201 | mode=mixed | hard=12 | presets=1
- Seq 2 Cue 86 | Fixture 107 | mode=mixed | hard=11 | presets=1
- Seq 2 Cue 86 | Fixture 108 | mode=mixed | hard=11 | presets=1
- Seq 2 Cue 32 | Fixture 106 | mode=mixed | hard=9 | presets=1
- Seq 10 Cue 89 | Fixture 1 | mode=mixed | hard=8 | presets=2
- Seq 10 Cue 89 | Fixture 2 | mode=mixed | hard=8 | presets=2
- Seq 10 Cue 89 | Fixture 3 | mode=mixed | hard=8 | presets=2
- Seq 10 Cue 89 | Fixture 4 | mode=mixed | hard=8 | presets=2

## Preset logic breaks
- Total findings: 17
- Broken preset blocks: 4
- Local hard overrides: 13
- Fragmented preset blocks: 0
- Repeated suspicious overrides: 0
- Seq 2 Cue 25 | broken_preset_block | family=Color | preset=4.10 | outliers=101, 102
- Seq 10 Cue 1 | local_hard_override | family=Color | preset=0.52 | outliers=14, 15
- Seq 10 Cue 1 | local_hard_override | family=Position | preset=0.52 | outliers=13, 14, 15
- Seq 10 Cue 1 | local_hard_override | family=Beam | preset=0.52 | outliers=13, 14, 15
- Seq 2 Cue 35 | broken_preset_block | family=Dimmer | preset=0.78 | outliers=202
- Seq 10 Cue 89 | broken_preset_block | family=Color | preset=4.11 | outliers=16
- Seq 2 Cue 55 | broken_preset_block | family=Color | preset=4.11 | outliers=40, 101, 102, 201, 202
- Seq 10 Cue 109 | local_hard_override | family=Dimmer | preset=0.32 | outliers=111, 112
- Seq 10 Cue 65 | local_hard_override | family=Dimmer | preset=0.78 | outliers=111, 112
- Seq 2 Cue 16 | local_hard_override | family=Dimmer | preset=0.78 | outliers=1001, 1002, 1003, 1004
- Seq 10 Cue 2 | local_hard_override | family=Dimmer | preset=0.81 | outliers=16
- Seq 2 Cue 12 | local_hard_override | family=Dimmer | preset=0.30 | outliers=1004

## Missing preset opportunities
- Total findings: 4
- Exact repeated blocks: 2
- Near-identical repeated blocks: 1
- Fragmented repeated states: 0
- Existing preset likely unused: 1
- missing_preset_candidate_exact | family=Dimmer | cues=10.39, 10.41, 10.43, 10.45, 10.47, 10.49, 10.51, 10.53, 10.55, 10.57 ... | fixtures=1, 2, 3, 5, 6, 7 | occurrences=13
- missing_preset_candidate_exact | family=Color | cues=10.40, 10.42, 10.44, 10.46, 10.48, 10.50, 10.52, 10.54, 10.56, 10.58 ... | fixtures=41, 42, 47, 48 | occurrences=12
- existing_preset_likely_unused | family=Color | cues=1.1, 10.27, 10.80, 10.98 | fixtures=1, 2, 3, 4, 5, 6, 7, 8 | occurrences=4
- missing_preset_candidate_near | family=Color | cues=10.1, 10.36, 10.36.5 | fixtures=61, 62, 63, 64 | occurrences=3
