# grandMA2 Audit Report

## Dependency map
- Cues analyzed: 111

## Preset heatmap
- Preset 4.10: cues=18, sequences=1, status=active, duplicates=0
- Preset 0.16: cues=4, sequences=1, status=active, duplicates=0
- Preset 0.18: cues=4, sequences=1, status=active, duplicates=0
- Preset 0.49: cues=4, sequences=1, status=active, duplicates=0
- Preset 0.5: cues=4, sequences=1, status=active, duplicates=0
- Preset 0.6: cues=4, sequences=1, status=active, duplicates=0
- Preset 0.17: cues=3, sequences=1, status=active, duplicates=0
- Preset 0.20: cues=3, sequences=1, status=active, duplicates=0
- Preset 0.4: cues=3, sequences=1, status=active, duplicates=0
- Preset 0.66: cues=3, sequences=1, status=active, duplicates=0

## Consistency issues
- mixed_control_mode: 6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off / COLORRGB1 | hard_atoms=213, preset_refs=186, fixtures=40, cues=32
- mixed_control_mode: 6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off / COLORRGB2 | hard_atoms=213, preset_refs=186, fixtures=40, cues=32
- mixed_control_mode: 6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off / COLORRGB3 | hard_atoms=201, preset_refs=186, fixtures=40, cues=32
- mixed_control_mode: 7 Robin Spiider Mode 3 / COLORMIXER | hard_atoms=34, preset_refs=116, fixtures=10, cues=42
- mixed_control_mode: 7 Robin Spiider Mode 3 / COLORMIXMODE | hard_atoms=34, preset_refs=116, fixtures=10, cues=42
- mixed_control_mode: 7 Robin Spiider Mode 3 / COLORRGB1 | hard_atoms=100, preset_refs=117, fixtures=10, cues=52
- mixed_control_mode: 7 Robin Spiider Mode 3 / COLORRGB2 | hard_atoms=102, preset_refs=117, fixtures=10, cues=52
- mixed_control_mode: 7 Robin Spiider Mode 3 / COLORRGB3 | hard_atoms=100, preset_refs=117, fixtures=10, cues=52
- mixed_control_mode: 7 Robin Spiider Mode 3 / COLORRGB5 | hard_atoms=100, preset_refs=117, fixtures=10, cues=52
- mixed_control_mode: 7 Robin Spiider Mode 3 / CTC | hard_atoms=34, preset_refs=116, fixtures=10, cues=42

## Risk hotspots
- Seq 2 Cue 25 Vilda odchazi | score=10 | many hard values (72); touches many feature groups (6); mixed hard and preset control; depends on several presets (5)
- Seq 2 Cue 85 Dekovacka | score=10 | many hard values (146); touches many feature groups (6); mixed hard and preset control; depends on several presets (7)
- Seq 2 Cue 11 J. SOLO - 2:47 | score=9 | many hard values (48); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 18 Rackove rostazeny nohy 5:05 | score=9 | many hard values (77); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 20 Solo Zacatek Bert | score=9 | many hard values (34); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 30.5 Soud - zelena- - bici hudba | score=9 | many hard values (46); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 31 Soud - proces-Na-schody | score=9 | many hard values (49); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 32 Po procesu - s hudbou | score=9 | many hard values (41); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 36 Jen prava strana - Wilda na schodech | score=9 | many hard values (34); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 46 Velkej ptak | score=9 | many hard values (51); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 53 Zacatek trio EFF 16 | score=9 | many hard values (67); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 55 Groteska boj o zradlo - Velikeho racka | score=9 | many hard values (197); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 78 Svicka | score=9 | many hard values (47); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 80 Flo konec sola stred | score=9 | many hard values (55); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 86 lidi | score=9 | many hard values (265); touches many feature groups (6); mixed hard and preset control

## Cue quality
- Seq 2 Cue 46 | score=91 | very hard-heavy cue (51 hard values); mixed programming in 10 fixture/family pairs; low similarity to neighbouring cues (0.02); hard values spike vs local block (51 vs avg 15.4); many zero/reset-like values (9); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 2 Cue 55 | score=83 | very hard-heavy cue (197 hard values); mixed programming in 4 fixture/family pairs; low similarity to neighbouring cues (0.12); hard values spike vs local block (197 vs avg 54.0); many zero/reset-like values (17); more mixed fixtures than neighbouring cues
- Seq 2 Cue 9 | score=83 | very hard-heavy cue (62 hard values); mixed programming in 12 fixture/family pairs; low similarity to neighbouring cues (0.06); hard values spike vs local block (62 vs avg 25.9); many zero/reset-like values (20); more mixed fixtures than neighbouring cues
- Seq 2 Cue 25 | score=76 | very hard-heavy cue (72 hard values); mixed programming in 28 fixture/family pairs; noticeable local outlier (0.27); hard values spike vs local block (72 vs avg 24.3); many zero/reset-like values (22); more mixed fixtures than neighbouring cues
- Seq 2 Cue 11 | score=70 | very hard-heavy cue (48 hard values); mixed programming in 3 fixture/family pairs; noticeable local outlier (0.23); hard values spike vs local block (48 vs avg 20.1); many zero/reset-like values (20)
- Seq 2 Cue 44 | score=69 | very hard-heavy cue (24 hard values); mixed programming in 8 fixture/family pairs; low similarity to neighbouring cues (0.03); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 2 Cue 18 | score=68 | very hard-heavy cue (77 hard values); mixed programming in 32 fixture/family pairs; hard values spike vs local block (77 vs avg 23.4); many zero/reset-like values (22); more mixed fixtures than neighbouring cues
- Seq 2 Cue 14 | score=67 | very hard-heavy cue (26 hard values); mixed programming in 4 fixture/family pairs; low similarity to neighbouring cues (0.07); hard values spike vs local block (26 vs avg 9.4)
- Seq 2 Cue 86 | score=67 | very hard-heavy cue (265 hard values); mixed programming in 26 fixture/family pairs; low similarity to neighbouring cues (0.03); hard values spike vs local block (265 vs avg 110.0)
- Seq 2 Cue 24 | score=66 | very hard-heavy cue (49 hard values); mixed programming in 12 fixture/family pairs; noticeable local outlier (0.26); hard values spike vs local block (49 vs avg 23.0); more mixed fixtures than neighbouring cues
- Seq 2 Cue 85 | score=66 | very hard-heavy cue (146 hard values); mixed programming in 33 fixture/family pairs; low similarity to neighbouring cues (0.04); many preset refs combined with hard edits; more mixed fixtures than neighbouring cues
- Seq 2 Cue 4 | score=65 | very hard-heavy cue (17 hard values); mixed programming in 4 fixture/family pairs; low similarity to neighbouring cues (0.05); many zero/reset-like values (7)
- Seq 2 Cue 76 | score=65 | very hard-heavy cue (124 hard values); low similarity to neighbouring cues (0.12); hard values spike vs local block (124 vs avg 33.1); many zero/reset-like values (54); touches unusually many feature groups (6)
- Seq 2 Cue 82 | score=65 | very hard-heavy cue (46 hard values); mixed programming in 6 fixture/family pairs; low similarity to neighbouring cues (0.17); many zero/reset-like values (43)
- Seq 2 Cue 80 | score=62 | very hard-heavy cue (55 hard values); mixed programming in 8 fixture/family pairs; noticeable local outlier (0.20); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues

## Worst blocks
- Seq 2 cues 7 - 11 | avg=51.0 | high cues=2, avg hard=32.4, avg similarity=0.15
- Seq 2 cues 8 - 12 | avg=51.0 | high cues=2, avg hard=27.0, avg similarity=0.14
- Seq 2 cues 51 - 55 | avg=50.6 | high cues=3, avg hard=77.8, avg similarity=0.16
- Seq 2 cues 23 - 27 | avg=49.4 | high cues=2, avg hard=31.2, avg similarity=0.14
- Seq 2 cues 35 - 39 | avg=48.8 | high cues=3, avg hard=20.2, avg similarity=0.11
- Seq 2 cues 80 - 85 | avg=48.6 | high cues=3, avg hard=51.6, avg similarity=0.08
- Seq 2 cues 24 - 28 | avg=48.0 | high cues=2, avg hard=32.2, avg similarity=0.16
- Seq 2 cues 36 - 40 | avg=47.8 | high cues=3, avg hard=19.4, avg similarity=0.09
- Seq 2 cues 44 - 46.6 | avg=47.4 | high cues=2, avg hard=18.8, avg similarity=0.02
- Seq 2 cues 76 - 80 | avg=47.4 | high cues=3, avg hard=56.0, avg similarity=0.13

## Fixture inconsistency
- Fixture 202 Dimmer | hard=40 | preset=23 | mixed=16
- Fixture 201 Dimmer | hard=39 | preset=20 | mixed=14
- Fixture 101 Dimmer | hard=33 | preset=25 | mixed=12
- Fixture 102 Dimmer | hard=32 | preset=28 | mixed=12
- Fixture 101 Color | hard=15 | preset=23 | mixed=8
- Fixture 102 Color | hard=14 | preset=26 | mixed=8
- Fixture 201 Color | hard=15 | preset=18 | mixed=7
- Fixture 108 Dimmer | hard=35 | preset=14 | mixed=6
- Fixture 106 Dimmer | hard=32 | preset=10 | mixed=6
- Fixture 107 Dimmer | hard=31 | preset=16 | mixed=6

## Hard vs preset balance
- Seq 2 Cue 85 | Fixture 101 | mode=mixed | hard=19 | presets=2
- Seq 2 Cue 85 | Fixture 102 | mode=mixed | hard=19 | presets=2
- Seq 2 Cue 85 | Fixture 201 | mode=mixed | hard=19 | presets=2
- Seq 2 Cue 85 | Fixture 202 | mode=mixed | hard=19 | presets=2
- Seq 2 Cue 86 | Fixture 101 | mode=mixed | hard=19 | presets=2
- Seq 2 Cue 86 | Fixture 102 | mode=mixed | hard=19 | presets=2
- Seq 2 Cue 86 | Fixture 201 | mode=mixed | hard=19 | presets=2
- Seq 2 Cue 86 | Fixture 202 | mode=mixed | hard=19 | presets=2
- Seq 2 Cue 25 | Fixture 102 | mode=mixed | hard=17 | presets=3
- Seq 2 Cue 85 | Fixture 107 | mode=mixed | hard=17 | presets=3
- Seq 2 Cue 85 | Fixture 108 | mode=mixed | hard=17 | presets=3
- Seq 2 Cue 14 | Fixture 108 | mode=mixed | hard=17 | presets=2
- Seq 2 Cue 18 | Fixture 102 | mode=mixed | hard=17 | presets=2
- Seq 2 Cue 18 | Fixture 202 | mode=mixed | hard=17 | presets=2
- Seq 2 Cue 2 | Fixture 101 | mode=mixed | hard=17 | presets=2
