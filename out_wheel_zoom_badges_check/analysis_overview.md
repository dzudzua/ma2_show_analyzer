# grandMA2 Show Analysis

## Summary
- Main sequences: 2
- Main cue count: 208
- Presets loaded: 147
- Groups loaded: 7
- Effects loaded: 0
- Patch fixtures loaded: 81
- Used fixtures total: 113
- Used fixtures without patch mapping: 32
- Unified model export: `show_model_v2.json`
- Validation warnings: 245

## Top cues by hard values
- Cue 109 `Blesk MIDI`: H=302, D=30, fixtures=46, fade=-, trigger=-
- Cue 0 `Cue Zero`: H=278, D=66, fixtures=56, fade=-, trigger=-
- Cue 86 `lidi`: H=199, D=66, fixtures=56, fade=3, trigger=-
- Cue 106 `DUHA`: H=184, D=35, fixtures=40, fade=25, trigger=Timecode
- Cue 55 `Groteska boj o zradlo - Velikeho racka`: H=152, D=45, fixtures=50, fade=10, trigger=-
- Cue 1 `lidi`: H=142, D=26, fixtures=54, fade=1.5, trigger=-
- Cue 65 `final flash`: H=112, D=9, fixtures=46, fade=-, trigger=Timecode
- Cue 76 `J+F duet - S hudbou`: H=88, D=36, fixtures=33, fade=8, trigger=-
- Cue 85 `Dekovacka`: H=84, D=62, fixtures=56, fade=8, trigger=-
- Cue 89 `koks KOUR GARAZ`: H=77, D=49, fixtures=39, fade=-, trigger=Timecode

## Top fixtures by cue usage
- Fixture 5 `5`: type=-, patch=-, cues=134, H=348, D=156
- Fixture 3 `3`: type=-, patch=-, cues=129, H=272, D=133
- Fixture 2 `2`: type=-, patch=-, cues=128, H=275, D=136
- Fixture 4 `4`: type=-, patch=-, cues=128, H=238, D=98
- Fixture 7 `7`: type=-, patch=-, cues=126, H=283, D=132
- Fixture 6 `6`: type=-, patch=-, cues=123, H=272, D=130
- Fixture 8 `8`: type=-, patch=-, cues=122, H=230, D=98
- Fixture 1 `1`: type=-, patch=-, cues=84, H=342, D=144
- Fixture 16 `16`: type=-, patch=-, cues=80, H=356, D=56
- Fixture 15 `15`: type=-, patch=-, cues=77, H=348, D=52

## Hottest presets
- Preset 0.34 `350 plocha`: cues=21, sequences=1, fixtures=12, status=active
- Preset 0.34 `Pruvany rackove`: cues=21, sequences=1, fixtures=2, status=active
- Preset 0.45 `plocha spiider`: cues=18, sequences=1, fixtures=8, status=active
- Preset 4.10 `orange`: cues=18, sequences=1, fixtures=40, status=active
- Preset 0.49 `BAR`: cues=9, sequences=2, fixtures=12, status=active
- Preset 0.49 `Do zdi-Start`: cues=9, sequences=2, fixtures=2, status=active
- Preset 0.58 `Projzi scan`: cues=7, sequences=2, fixtures=12, status=active
- Preset 0.58 `Prave schodiste-Klouzacka`: cues=7, sequences=2, fixtures=1, status=active
- Preset 0.86 `blesk pre show`: cues=6, sequences=5, fixtures=4, status=active
- Preset 0.26 `strobo hor`: cues=5, sequences=2, fixtures=31, status=active

## Fixture coverage risks
- Fixture 1013 ``: type=-, cues=1, presets=0, orphan_patch=False
- Fixture 1014 ``: type=-, cues=1, presets=0, orphan_patch=False
- Fixture 1015 ``: type=-, cues=1, presets=0, orphan_patch=False
- Fixture 1016 ``: type=-, cues=1, presets=0, orphan_patch=False
- Fixture 1017 ``: type=-, cues=1, presets=0, orphan_patch=False
- Fixture 1018 ``: type=-, cues=1, presets=0, orphan_patch=False
- Fixture 1019 ``: type=-, cues=1, presets=0, orphan_patch=False
- Fixture 1020 ``: type=-, cues=1, presets=0, orphan_patch=False
- Fixture 1021 ``: type=-, cues=1, presets=0, orphan_patch=False
- Fixture 1022 ``: type=-, cues=1, presets=0, orphan_patch=False

## Consistency issues
- mixed_control_mode: 12 Robin LEDBeam 350 Mode 1 / COLORMIXER | severity=high | hard_atoms=12, preset_refs=204, fixtures=12, cues=23
- mixed_control_mode: 12 Robin LEDBeam 350 Mode 1 / COLORRGB1 | severity=high | hard_atoms=124, preset_refs=240, fixtures=12, cues=52
- mixed_control_mode: 12 Robin LEDBeam 350 Mode 1 / COLORRGB2 | severity=high | hard_atoms=124, preset_refs=240, fixtures=12, cues=52
- mixed_control_mode: 12 Robin LEDBeam 350 Mode 1 / COLORRGB3 | severity=high | hard_atoms=124, preset_refs=240, fixtures=12, cues=52
- mixed_control_mode: 12 Robin LEDBeam 350 Mode 1 / COLORRGB5 | severity=high | hard_atoms=124, preset_refs=240, fixtures=12, cues=52
- mixed_control_mode: 12 Robin LEDBeam 350 Mode 1 / COLORTEMPERATURE | severity=high | hard_atoms=12, preset_refs=204, fixtures=12, cues=23
- mixed_control_mode: 14 Hotbox RGBW 8 channel / COLORRGB1 | severity=high | hard_atoms=21, preset_refs=12, fixtures=7, cues=11
- mixed_control_mode: 14 Hotbox RGBW 8 channel / COLORRGB2 | severity=high | hard_atoms=21, preset_refs=12, fixtures=7, cues=11
- mixed_control_mode: 14 Hotbox RGBW 8 channel / COLORRGB3 | severity=high | hard_atoms=21, preset_refs=12, fixtures=7, cues=11
- mixed_control_mode: 14 Hotbox RGBW 8 channel / COLORRGB5 | severity=high | hard_atoms=21, preset_refs=12, fixtures=7, cues=11

## Risk hotspots
- Seq 10 Cue 1 lidi: score=10 | many hard values (142); touches many feature groups (6); mixed hard and preset control; depends on several presets (6); dimmer hard values present (26)
- Seq 10 Cue 36 9:46.888: score=10 | many hard values (75); touches many feature groups (7); mixed hard and preset control; depends on several presets (9); dimmer hard values present (27)
- Seq 2 Cue 25 Vilda odchazi: score=10 | many hard values (66); touches many feature groups (6); mixed hard and preset control; depends on several presets (5)
- Seq 2 Cue 85 Dekovacka: score=10 | many hard values (84); touches many feature groups (6); mixed hard and preset control; depends on several presets (7); dimmer hard values present (62)
- Seq 10 Cue 103 blesk: score=9 | many hard values (48); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (24)
- Seq 10 Cue 106 DUHA: score=9 | many hard values (184); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (35)
- Seq 10 Cue 109 Blesk MIDI: score=9 | many hard values (302); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (30)
- Seq 10 Cue 27 beegees 6:37.6: score=9 | many hard values (64); touches many feature groups (6); mixed hard and preset control; dimmer hard values present (30)
- Seq 10 Cue 6 najezd strobo: score=9 | many hard values (49); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (15)
- Seq 10 Cue 75 Projede Lavka: score=9 | many hard values (33); touches many feature groups (5); mixed hard and preset control; dimmer hard values present (28)

## Worst cues
- Seq 10 Cue 1 `lidi`: score=91 | very hard-heavy cue (142 hard values); mixed programming in 24 fixture/family pairs; low similarity to neighbouring cues (0.01); hard values spike vs local block (142 vs avg 28.6); many zero/reset-like values (82); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 10 Cue 89 `koks KOUR GARAZ`: score=91 | very hard-heavy cue (77 hard values); mixed programming in 11 fixture/family pairs; low similarity to neighbouring cues (0.02); hard values spike vs local block (77 vs avg 11.4); many zero/reset-like values (52); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 2 Cue 46 `Velkej ptak`: score=91 | very hard-heavy cue (44 hard values); mixed programming in 8 fixture/family pairs; low similarity to neighbouring cues (0.02); hard values spike vs local block (44 vs avg 10.4); many zero/reset-like values (9); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 10 Cue 27 `beegees 6:37.6`: score=83 | very hard-heavy cue (64 hard values); mixed programming in 8 fixture/family pairs; low similarity to neighbouring cues (0.01); hard values spike vs local block (64 vs avg 9.4); many zero/reset-like values (52); more mixed fixtures than neighbouring cues
- Seq 10 Cue 98 `Flo BLESK kdyz se vyfoti tereze`: score=83 | very hard-heavy cue (65 hard values); mixed programming in 8 fixture/family pairs; low similarity to neighbouring cues (0.07); hard values spike vs local block (65 vs avg 18.3); many zero/reset-like values (53); more mixed fixtures than neighbouring cues
- Seq 2 Cue 55 `Groteska boj o zradlo - Velikeho racka`: score=83 | very hard-heavy cue (152 hard values); mixed programming in 4 fixture/family pairs; low similarity to neighbouring cues (0.12); hard values spike vs local block (152 vs avg 30.9); many zero/reset-like values (17); more mixed fixtures than neighbouring cues
- Seq 2 Cue 9 `Racek astery 2:32`: score=83 | very hard-heavy cue (42 hard values); mixed programming in 12 fixture/family pairs; low similarity to neighbouring cues (0.06); hard values spike vs local block (42 vs avg 19.4); many zero/reset-like values (20); more mixed fixtures than neighbouring cues
- Seq 2 Cue 25 `Vilda odchazi`: score=76 | very hard-heavy cue (66 hard values); mixed programming in 25 fixture/family pairs; noticeable local outlier (0.27); hard values spike vs local block (66 vs avg 19.6); many zero/reset-like values (22); more mixed fixtures than neighbouring cues
- Seq 10 Cue 36 `9:46.888`: score=75 | very hard-heavy cue (75 hard values); mixed programming in 6 fixture/family pairs; hard values spike vs local block (75 vs avg 13.6); many zero/reset-like values (61); touches unusually many feature groups (7); many preset refs combined with hard edits
- Seq 10 Cue 6 `najezd strobo`: score=73 | very hard-heavy cue (49 hard values); mixed programming in 12 fixture/family pairs; low similarity to neighbouring cues (0.03); hard values spike vs local block (49 vs avg 10.3); more mixed fixtures than neighbouring cues

## Worst blocks
- Seq 2 cues 7 - 11: avg_score=47.8 | worst=83 | high cues=2, avg hard=24.8, avg similarity=0.15
- Seq 2 cues 6 - 10: avg_score=44.8 | worst=83 | high cues=2, avg hard=19.2, avg similarity=0.12
- Seq 2 cues 5 - 9: avg_score=43.8 | worst=83 | high cues=2, avg hard=18.2, avg similarity=0.08
- Seq 2 cues 8 - 12: avg_score=43.8 | worst=83 | high cues=2, avg hard=18.8, avg similarity=0.14
- Seq 2 cues 44 - 46.6: avg_score=43.4 | worst=91 | high cues=2, avg hard=14.2, avg similarity=0.02
- Seq 2 cues 24 - 28: avg_score=42.4 | worst=76 | high cues=2, avg hard=26.0, avg similarity=0.16
- Seq 2 cues 23 - 27: avg_score=42.2 | worst=76 | high cues=2, avg hard=25.0, avg similarity=0.14
- Seq 2 cues 51 - 55: avg_score=40.2 | worst=83 | high cues=2, avg hard=43.2, avg similarity=0.16

## Fixture inconsistency
- Fixture 101 `` / Color: hard=15, preset=31 | family uses both hard and preset control across 38 cues
- Fixture 102 `` / Color: hard=14, preset=34 | family uses both hard and preset control across 40 cues
- Fixture 201 `` / Color: hard=15, preset=25 | family uses both hard and preset control across 33 cues
- Fixture 101 `` / Position: hard=17, preset=32 | family uses both hard and preset control across 43 cues
- Fixture 102 `` / Position: hard=15, preset=35 | family uses both hard and preset control across 44 cues
- Fixture 202 `` / Color: hard=13, preset=28 | family uses both hard and preset control across 35 cues
- Fixture 201 `` / Position: hard=16, preset=25 | family uses both hard and preset control across 36 cues
- Fixture 202 `` / Position: hard=16, preset=28 | family uses both hard and preset control across 39 cues
- Fixture 21 `` / Color: hard=12, preset=30 | family uses both hard and preset control across 37 cues
- Fixture 22 `` / Color: hard=12, preset=30 | family uses both hard and preset control across 37 cues

## Repeated hard values
- Fixture 1 COLORRGB31=0.00: cues=23 | 1.1 Cue 1 | 10.27 beegees 6:37.6 | 10.40 Flash | 10.42 Flash | 10.44 Flash | 10.46 Flash | 10.48 Flash | 10.50 Flash ...
- Fixture 1 COLORRGB32=0.00: cues=23 | 1.1 Cue 1 | 10.27 beegees 6:37.6 | 10.40 Flash | 10.42 Flash | 10.44 Flash | 10.46 Flash | 10.48 Flash | 10.50 Flash ...
- Fixture 1 COLORRGB33=0.00: cues=23 | 1.1 Cue 1 | 10.27 beegees 6:37.6 | 10.40 Flash | 10.42 Flash | 10.44 Flash | 10.46 Flash | 10.48 Flash | 10.50 Flash ...
- Fixture 1 COLORRGB35=0.00: cues=23 | 1.1 Cue 1 | 10.27 beegees 6:37.6 | 10.40 Flash | 10.42 Flash | 10.44 Flash | 10.46 Flash | 10.48 Flash | 10.50 Flash ...
- Fixture 5 COLORRGB31=0.00: cues=23 | 1.1 Cue 1 | 10.27 beegees 6:37.6 | 10.40 Flash | 10.42 Flash | 10.44 Flash | 10.46 Flash | 10.48 Flash | 10.50 Flash ...
- Fixture 5 COLORRGB32=0.00: cues=23 | 1.1 Cue 1 | 10.27 beegees 6:37.6 | 10.40 Flash | 10.42 Flash | 10.44 Flash | 10.46 Flash | 10.48 Flash | 10.50 Flash ...
- Fixture 5 COLORRGB33=0.00: cues=23 | 1.1 Cue 1 | 10.27 beegees 6:37.6 | 10.40 Flash | 10.42 Flash | 10.44 Flash | 10.46 Flash | 10.48 Flash | 10.50 Flash ...
- Fixture 5 COLORRGB35=0.00: cues=23 | 1.1 Cue 1 | 10.27 beegees 6:37.6 | 10.40 Flash | 10.42 Flash | 10.44 Flash | 10.46 Flash | 10.48 Flash | 10.50 Flash ...
- Fixture 41 COLORRGB5=100.00: cues=16 | 10.6 najezd strobo | 10.40 Flash | 10.42 Flash | 10.44 Flash | 10.46 Flash | 10.48 Flash | 10.50 Flash | 10.52 Flash ...
- Fixture 42 COLORRGB5=100.00: cues=16 | 10.6 najezd strobo | 10.40 Flash | 10.42 Flash | 10.44 Flash | 10.46 Flash | 10.48 Flash | 10.50 Flash | 10.52 Flash ...

## Dead objects
- preset 0.29: Preset 0.29
- preset 0.35: spii stred
- preset 0.38: animacnigobo
- preset 0.39: gobo
- preset 0.40: tetra vstup
- preset 0.46: spot fotka
- preset 0.48: lidi
- preset 0.53: Astery Start
- preset 0.59: Preset 0.59
- preset 0.69: Preset 0.69

## Validation warnings
- Severity breakdown: high=102, medium=99, low=44
- Top kinds: fixture_used_without_patch_data=99, fixture_used_without_type=99, unused_preset=44, duplicate_patch_address=2, missing_target_object=1
- high: missing_target_object | cue:cue:10:31:Studio54_main_sequences.xml:34 | missing target effect:29
- high: fixture_used_without_patch_data | fixture:1 | Channel 1
- medium: fixture_used_without_type | fixture:1 | Channel 1
- high: fixture_used_without_patch_data | fixture:2 | Channel 2
- medium: fixture_used_without_type | fixture:2 | Channel 2
- high: fixture_used_without_patch_data | fixture:3 | Channel 3
- medium: fixture_used_without_type | fixture:3 | Channel 3
- high: fixture_used_without_patch_data | fixture:4 | Channel 4
- medium: fixture_used_without_type | fixture:4 | Channel 4
- high: fixture_used_without_patch_data | fixture:5 | Channel 5
- medium: fixture_used_without_type | fixture:5 | Channel 5
- high: fixture_used_without_patch_data | fixture:6 | Channel 6
- medium: fixture_used_without_type | fixture:6 | Channel 6
- high: fixture_used_without_patch_data | fixture:7 | Channel 7
- medium: fixture_used_without_type | fixture:7 | Channel 7

## Fixtures used without patch metadata
- 998, 999, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023 ...
