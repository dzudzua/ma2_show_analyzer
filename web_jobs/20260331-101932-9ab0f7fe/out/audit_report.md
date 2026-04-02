# grandMA2 Audit Report

## Dependency map
- Cues analyzed: 169

## Preset heatmap
- Preset 0.34: cues=23, sequences=1, status=active, duplicates=0
- Preset 0.45: cues=20, sequences=1, status=active, duplicates=0
- Preset 0.86: cues=7, sequences=5, status=active, duplicates=0
- Preset 0.49: cues=7, sequences=1, status=active, duplicates=0
- Preset 0.31: cues=6, sequences=1, status=active, duplicates=0
- Preset 0.58: cues=6, sequences=1, status=active, duplicates=0
- Preset 0.90: cues=6, sequences=1, status=active, duplicates=0
- Preset 0.41: cues=5, sequences=2, status=active, duplicates=0
- Preset 0.26: cues=5, sequences=1, status=active, duplicates=0
- Preset 0.56: cues=4, sequences=1, status=active, duplicates=0

## Consistency issues
- mixed_control_mode: 11 Robin Esprite Mode 2 / COLOR1 | hard_atoms=31, preset_refs=61, fixtures=8, cues=32
- mixed_control_mode: 11 Robin Esprite Mode 2 / COLOR2 | hard_atoms=31, preset_refs=61, fixtures=8, cues=32
- mixed_control_mode: 11 Robin Esprite Mode 2 / COLORRGB1 | hard_atoms=31, preset_refs=61, fixtures=8, cues=32
- mixed_control_mode: 11 Robin Esprite Mode 2 / COLORRGB2 | hard_atoms=31, preset_refs=61, fixtures=8, cues=32
- mixed_control_mode: 11 Robin Esprite Mode 2 / COLORRGB3 | hard_atoms=31, preset_refs=61, fixtures=8, cues=32
- mixed_control_mode: 11 Robin Esprite Mode 2 / CTO | hard_atoms=10, preset_refs=71, fixtures=8, cues=30
- mixed_control_mode: 11 Robin Esprite Mode 2 / GOBO2 | hard_atoms=10, preset_refs=78, fixtures=8, cues=30
- mixed_control_mode: 11 Robin Esprite Mode 2 / GOBO2_POS | hard_atoms=11, preset_refs=76, fixtures=8, cues=29
- mixed_control_mode: 11 Robin Esprite Mode 2 / INTENSITYMACROS | hard_atoms=12, preset_refs=67, fixtures=8, cues=30
- mixed_control_mode: 11 Robin Esprite Mode 2 / IRIS | hard_atoms=10, preset_refs=78, fixtures=8, cues=30

## Risk hotspots
- Seq 11 Cue 1 lidi | score=10 | many hard values (622); touches many feature groups (6); mixed hard and preset control; depends on several presets (6); dimmer hard values present (159)
- Seq 11 Cue 112 DIKY | score=10 | many hard values (645); touches many feature groups (6); mixed hard and preset control; depends on several presets (5); dimmer hard values present (186)
- Seq 11 Cue 113 lidi | score=10 | many hard values (605); touches many feature groups (6); mixed hard and preset control; depends on several presets (9); dimmer hard values present (176)
- Seq 11 Cue 114 8:15.150 | score=10 | many hard values (815); touches many feature groups (7); mixed hard and preset control; depends on several presets (10); dimmer hard values present (272)
- Seq 11 Cue 36 9:46.888 | score=10 | many hard values (75); touches many feature groups (7); mixed hard and preset control; depends on several presets (9); dimmer hard values present (250)
- Seq 11 Cue 103 blesk | score=9 | many hard values (48); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (100)
- Seq 11 Cue 106 DUHA | score=9 | many hard values (547); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (169)
- Seq 11 Cue 109 Blesk MIDI | score=9 | many hard values (640); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (88)
- Seq 11 Cue 27 beegees 6:37.6 | score=9 | many hard values (64); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (32)
- Seq 11 Cue 6 platforma dole | score=9 | many hard values (49); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (15)
- Seq 11 Cue 75 Projede Lavka az na konci | score=9 | many hard values (33); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (31)
- Seq 11 Cue 80 Alex gr STYCH od klaviru patrik osuka alexe | score=9 | many hard values (64); touches many feature groups (6); mixed hard and preset control
- Seq 11 Cue 81 disko gula dolu | score=9 | many hard values (64); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (13)
- Seq 11 Cue 84 Gobo sex | score=9 | many hard values (31); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (37)
- Seq 11 Cue 89 koks KOUR GARAZ | score=9 | many hard values (77); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (109)

## Cue quality
- Seq 11 Cue 1 | score=91 | very hard-heavy cue (622 hard values); mixed programming in 24 fixture/family pairs; low similarity to neighbouring cues (0.01); hard values spike vs local block (622 vs avg 156.0); many zero/reset-like values (490); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 11 Cue 89 | score=91 | very hard-heavy cue (77 hard values); mixed programming in 9 fixture/family pairs; low similarity to neighbouring cues (0.02); hard values spike vs local block (77 vs avg 11.4); many zero/reset-like values (52); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 11 Cue 98 | score=83 | very hard-heavy cue (65 hard values); mixed programming in 8 fixture/family pairs; low similarity to neighbouring cues (0.07); hard values spike vs local block (65 vs avg 18.0); many zero/reset-like values (53); more mixed fixtures than neighbouring cues
- Seq 11 Cue 36 | score=75 | very hard-heavy cue (75 hard values); mixed programming in 6 fixture/family pairs; hard values spike vs local block (75 vs avg 13.6); many zero/reset-like values (254); touches unusually many feature groups (7); many preset refs combined with hard edits
- Seq 11 Cue 27 | score=73 | very hard-heavy cue (64 hard values); mixed programming in 8 fixture/family pairs; low similarity to neighbouring cues (0.01); hard values spike vs local block (64 vs avg 9.4); more mixed fixtures than neighbouring cues
- Seq 11 Cue 6 | score=73 | very hard-heavy cue (49 hard values); mixed programming in 12 fixture/family pairs; low similarity to neighbouring cues (0.03); hard values spike vs local block (49 vs avg 10.4); more mixed fixtures than neighbouring cues
- Seq 11 Cue 84 | score=69 | very hard-heavy cue (31 hard values); mixed programming in 6 fixture/family pairs; low similarity to neighbouring cues (0.07); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 11 Cue 103 | score=68 | very hard-heavy cue (48 hard values); mixed programming in 12 fixture/family pairs; hard values spike vs local block (48 vs avg 8.1); many zero/reset-like values (40); more mixed fixtures than neighbouring cues
- Seq 11 Cue 81 | score=65 | very hard-heavy cue (64 hard values); low similarity to neighbouring cues (0.02); hard values spike vs local block (64 vs avg 14.0); many zero/reset-like values (40); touches unusually many feature groups (6)
- Seq 11 Cue 9 | score=65 | very hard-heavy cue (19 hard values); mixed programming in 5 fixture/family pairs; low similarity to neighbouring cues (0.17); many zero/reset-like values (43)
- Seq 11 Cue 80 | score=58 | very hard-heavy cue (64 hard values); noticeable local outlier (0.31); hard values spike vs local block (64 vs avg 18.9); many zero/reset-like values (56); touches unusually many feature groups (6)
- Seq 11 Cue 106 | score=57 | very hard-heavy cue (547 hard values); low similarity to neighbouring cues (0.00); hard values spike vs local block (547 vs avg 171.0); many zero/reset-like values (249)
- Seq 11 Cue 65 | score=57 | very hard-heavy cue (112 hard values); low similarity to neighbouring cues (0.01); hard values spike vs local block (112 vs avg 22.6); many zero/reset-like values (170)
- Seq 11 Cue 76 | score=57 | very hard-heavy cue (64 hard values); low similarity to neighbouring cues (0.06); hard values spike vs local block (64 vs avg 23.7); many zero/reset-like values (33)
- Seq 11 Cue 85 | score=57 | very hard-heavy cue (73 hard values); low similarity to neighbouring cues (0.05); hard values spike vs local block (73 vs avg 15.3); many zero/reset-like values (51)

## Worst blocks
- Seq 11 cues 81 - 85 | avg=44.2 | high cues=3, avg hard=34.0, avg similarity=0.06
- Seq 11 cues 5 - 9 | avg=40.2 | high cues=2, avg hard=14.4, avg similarity=0.08
- Seq 11 cues 94 - 98 | avg=39.0 | high cues=2, avg hard=24.8, avg similarity=0.02
- Seq 11 cues 95 - 99 | avg=39.0 | high cues=2, avg hard=24.8, avg similarity=0.06
- Seq 11 cues 6 - 9.5 | avg=38.2 | high cues=2, avg hard=14.2, avg similarity=0.07
- Seq 11 cues 76 - 80 | avg=37.0 | high cues=2, avg hard=39.0, avg similarity=0.19
- Seq 11 cues 109 - 114 | avg=36.8 | high cues=1, avg hard=541.2, avg similarity=0.31
- Seq 11 cues 85 - 89 | avg=35.8 | high cues=2, avg hard=30.2, avg similarity=0.13
- Seq 11 cues 80.6 - 84 | avg=35.8 | high cues=2, avg hard=19.4, avg similarity=0.07
- Seq 11 cues 96 - 100 | avg=35.2 | high cues=2, avg hard=23.4, avg similarity=0.11

## Fixture inconsistency
- Fixture 1 Color | hard=26 | preset=23 | mixed=5
- Fixture 5 Color | hard=26 | preset=23 | mixed=5
- Fixture 4 Color | hard=14 | preset=23 | mixed=5
- Fixture 2 Color | hard=13 | preset=23 | mixed=5
- Fixture 3 Color | hard=13 | preset=24 | mixed=5
- Fixture 6 Color | hard=13 | preset=23 | mixed=5
- Fixture 7 Color | hard=13 | preset=24 | mixed=5
- Fixture 8 Color | hard=13 | preset=23 | mixed=5
- Fixture 14 Color | hard=7 | preset=10 | mixed=5
- Fixture 21 Color | hard=7 | preset=9 | mixed=5

## Hard vs preset balance
- Seq 11 Cue 114 | Fixture 14 | mode=mixed | hard=37 | presets=1
- Seq 11 Cue 114 | Fixture 15 | mode=mixed | hard=37 | presets=1
- Seq 11 Cue 1 | Fixture 14 | mode=mixed | hard=28 | presets=1
- Seq 11 Cue 1 | Fixture 15 | mode=mixed | hard=28 | presets=1
- Seq 11 Cue 36 | Fixture 14 | mode=mixed | hard=28 | presets=1
- Seq 11 Cue 36 | Fixture 15 | mode=mixed | hard=28 | presets=1
- Seq 11 Cue 9 | Fixture 11 | mode=mixed | hard=18 | presets=1
- Seq 11 Cue 114 | Fixture 16 | mode=mixed | hard=12 | presets=1
- Seq 11 Cue 112 | Fixture 1 | mode=mixed | hard=8 | presets=2
- Seq 11 Cue 112 | Fixture 5 | mode=mixed | hard=8 | presets=2
- Seq 11 Cue 112 | Fixture 7 | mode=mixed | hard=8 | presets=2
- Seq 11 Cue 112 | Fixture 2 | mode=mixed | hard=8 | presets=1
- Seq 11 Cue 112 | Fixture 3 | mode=mixed | hard=8 | presets=1
- Seq 11 Cue 112 | Fixture 4 | mode=mixed | hard=8 | presets=1
- Seq 11 Cue 112 | Fixture 6 | mode=mixed | hard=8 | presets=1

## Preset logic breaks
- Total findings: 7
- Broken preset blocks: 1
- Local hard overrides: 6
- Fragmented preset blocks: 0
- Repeated suspicious overrides: 0
- Seq 11 Cue 113 | broken_preset_block | family=Dimmer | preset=0.39 | outliers=13
- Seq 11 Cue 114 | local_hard_override | family=Dimmer | preset=0.41 | outliers=27, 28, 111, 112
- Seq 11 Cue 36.5 | local_hard_override | family=Dimmer | preset=0.81 | outliers=16
- Seq 11 Cue 1 | local_hard_override | family=Position | preset=0.33 | outliers=13
- Seq 11 Cue 1 | local_hard_override | family=Beam | preset=0.33 | outliers=13
- Seq 11 Cue 36 | local_hard_override | family=Position | preset=0.33 | outliers=13
- Seq 11 Cue 36 | local_hard_override | family=Beam | preset=0.33 | outliers=13

## Missing preset opportunities
- Total findings: 5
- Exact repeated blocks: 3
- Near-identical repeated blocks: 1
- Fragmented repeated states: 0
- Existing preset likely unused: 1
- missing_preset_candidate_exact | family=Dimmer | cues=11.39, 11.41, 11.43, 11.45, 11.47, 11.49, 11.51, 11.53, 11.55, 11.57 ... | fixtures=1, 2, 3, 5, 6, 7 | occurrences=13
- missing_preset_candidate_exact | family=Color | cues=11.1, 11.36, 11.36.5, 11.113, 11.114 | fixtures=61, 62, 63, 64 | occurrences=5
- missing_preset_candidate_exact | family=Color | cues=11.40, 11.42, 11.44, 11.46, 11.48, 11.50, 11.52, 11.54, 11.56, 11.58 ... | fixtures=41, 42, 47, 48 | occurrences=12
- existing_preset_likely_unused | family=Color | cues=2.1, 11.27, 11.80, 11.89, 11.98, 11.114 | fixtures=1, 2, 3, 4, 5, 6, 7, 8 | occurrences=6
- missing_preset_candidate_near | family=Dimmer | cues=11.91, 11.103, 11.110 | fixtures=1, 2, 3, 4, 5, 6, 7, 8 | occurrences=3
