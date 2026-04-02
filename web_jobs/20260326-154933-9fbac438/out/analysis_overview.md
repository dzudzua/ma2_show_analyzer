# grandMA2 Show Analysis

## Summary
- Main sequences: 1
- Main cue count: 91
- Presets loaded: 83
- Groups loaded: 6
- Effects loaded: 0
- Patch fixtures loaded: 50
- Used fixtures total: 58
- Used fixtures without patch mapping: 0
- Unified model export: `show_model_v2.json`
- Validation warnings: 52

## Top cues by hard values
- Cue 0 `Cue Zero`: 344 hard values, 56 fixtures, fade=-, trigger=-
- Cue 86 `lidi`: 265 hard values, 56 fixtures, fade=3, trigger=-
- Cue 55 `Groteska boj o zradlo - Velikeho racka`: 197 hard values, 50 fixtures, fade=10, trigger=-
- Cue 85 `Dekovacka`: 146 hard values, 56 fixtures, fade=8, trigger=-
- Cue 76 `J+F duet - S hudbou`: 124 hard values, 33 fixtures, fade=8, trigger=-
- Cue 18 `Rackove rostazeny nohy 5:05`: 77 hard values, 10 fixtures, fade=8, trigger=-
- Cue 25 `Vilda odchazi`: 72 hard values, 27 fixtures, fade=15, trigger=-
- Cue 53 `Zacatek trio EFF 16`: 67 hard values, 53 fixtures, fade=18, trigger=-
- Cue 54 `TRIO do prostoru`: 65 hard values, 49 fixtures, fade=15, trigger=-
- Cue 9 `Racek astery 2:32`: 62 hard values, 28 fixtures, fade=1, trigger=-

## Top fixtures by cue usage
- Fixture 2 `HelDGB8S 2`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.025, cues=70, hard atoms=50
- Fixture 3 `HelDGB8S 3`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.049, cues=68, hard atoms=44
- Fixture 4 `HelDGB8S 4`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.073, cues=67, hard atoms=40
- Fixture 5 `HelDGB8S 5`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.097, cues=63, hard atoms=56
- Fixture 6 `HelDGB8S 6`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.121, cues=63, hard atoms=43
- Fixture 7 `HelDGB8S 7`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.145, cues=63, hard atoms=41
- Fixture 8 `HelDGB8S 8`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.169, cues=63, hard atoms=49
- Fixture 101 `RSpiide3 1`: type=7 Robin Spiider Mode 3, patch=4.034, cues=51, hard atoms=553
- Fixture 102 `RSpiide3 2`: type=7 Robin Spiider Mode 3, patch=4.001, cues=51, hard atoms=555
- Fixture 202 `SPIDER 33 2`: type=7 Robin Spiider Mode 3, patch=4.436, cues=50, hard atoms=421

## Hottest presets
- Preset 4.10 `orange`: cues=18, sequences=1, fixtures=40, status=active
- Preset 0.16 `Start Front`: cues=4, sequences=1, fixtures=4, status=active
- Preset 0.18 `F-DoHnizda`: cues=4, sequences=1, fixtures=2, status=active
- Preset 0.49 `Do zdi-Start`: cues=4, sequences=1, fixtures=2, status=active
- Preset 0.5 `front`: cues=4, sequences=1, fixtures=4, status=active
- Preset 0.6 `Zeme Pruvany`: cues=4, sequences=1, fixtures=2, status=active
- Preset 0.17 `Q6-9`: cues=3, sequences=1, fixtures=4, status=active
- Preset 0.20 `Soud`: cues=3, sequences=1, fixtures=10, status=active
- Preset 0.4 `tepla vsude`: cues=3, sequences=1, fixtures=10, status=active
- Preset 0.66 `Jirka-Schody`: cues=3, sequences=1, fixtures=1, status=active

## Fixture coverage risks
- Fixture 1008 ``: type=-, cues=1, presets=0, orphan_patch=False

## Consistency issues
- mixed_control_mode: 6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off / COLORRGB1 | severity=high | hard_atoms=213, preset_refs=186, fixtures=40, cues=32
- mixed_control_mode: 6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off / COLORRGB2 | severity=high | hard_atoms=213, preset_refs=186, fixtures=40, cues=32
- mixed_control_mode: 6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off / COLORRGB3 | severity=high | hard_atoms=201, preset_refs=186, fixtures=40, cues=32
- mixed_control_mode: 7 Robin Spiider Mode 3 / COLORMIXER | severity=high | hard_atoms=34, preset_refs=116, fixtures=10, cues=42
- mixed_control_mode: 7 Robin Spiider Mode 3 / COLORMIXMODE | severity=high | hard_atoms=34, preset_refs=116, fixtures=10, cues=42
- mixed_control_mode: 7 Robin Spiider Mode 3 / COLORRGB1 | severity=high | hard_atoms=100, preset_refs=117, fixtures=10, cues=52
- mixed_control_mode: 7 Robin Spiider Mode 3 / COLORRGB2 | severity=high | hard_atoms=102, preset_refs=117, fixtures=10, cues=52
- mixed_control_mode: 7 Robin Spiider Mode 3 / COLORRGB3 | severity=high | hard_atoms=100, preset_refs=117, fixtures=10, cues=52
- mixed_control_mode: 7 Robin Spiider Mode 3 / COLORRGB5 | severity=high | hard_atoms=100, preset_refs=117, fixtures=10, cues=52
- mixed_control_mode: 7 Robin Spiider Mode 3 / CTC | severity=high | hard_atoms=34, preset_refs=116, fixtures=10, cues=42

## Risk hotspots
- Seq 2 Cue 25 Vilda odchazi: score=10 | many hard values (72); touches many feature groups (6); mixed hard and preset control; depends on several presets (5)
- Seq 2 Cue 85 Dekovacka: score=10 | many hard values (146); touches many feature groups (6); mixed hard and preset control; depends on several presets (7)
- Seq 2 Cue 11 J. SOLO - 2:47: score=9 | many hard values (48); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 18 Rackove rostazeny nohy 5:05: score=9 | many hard values (77); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 20 Solo Zacatek Bert: score=9 | many hard values (34); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 30.5 Soud - zelena- - bici hudba: score=9 | many hard values (46); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 31 Soud - proces-Na-schody: score=9 | many hard values (49); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 32 Po procesu - s hudbou: score=9 | many hard values (41); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 36 Jen prava strana - Wilda na schodech: score=9 | many hard values (34); touches many feature groups (6); mixed hard and preset control
- Seq 2 Cue 46 Velkej ptak: score=9 | many hard values (51); touches many feature groups (6); mixed hard and preset control

## Worst cues
- Seq 2 Cue 46 `Velkej ptak`: score=91 | very hard-heavy cue (51 hard values); mixed programming in 10 fixture/family pairs; low similarity to neighbouring cues (0.02); hard values spike vs local block (51 vs avg 15.4); many zero/reset-like values (9); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 2 Cue 55 `Groteska boj o zradlo - Velikeho racka`: score=83 | very hard-heavy cue (197 hard values); mixed programming in 4 fixture/family pairs; low similarity to neighbouring cues (0.12); hard values spike vs local block (197 vs avg 54.0); many zero/reset-like values (17); more mixed fixtures than neighbouring cues
- Seq 2 Cue 9 `Racek astery 2:32`: score=83 | very hard-heavy cue (62 hard values); mixed programming in 12 fixture/family pairs; low similarity to neighbouring cues (0.06); hard values spike vs local block (62 vs avg 25.9); many zero/reset-like values (20); more mixed fixtures than neighbouring cues
- Seq 2 Cue 25 `Vilda odchazi`: score=76 | very hard-heavy cue (72 hard values); mixed programming in 28 fixture/family pairs; noticeable local outlier (0.27); hard values spike vs local block (72 vs avg 24.3); many zero/reset-like values (22); more mixed fixtures than neighbouring cues
- Seq 2 Cue 11 `J. SOLO - 2:47`: score=70 | very hard-heavy cue (48 hard values); mixed programming in 3 fixture/family pairs; noticeable local outlier (0.23); hard values spike vs local block (48 vs avg 20.1); many zero/reset-like values (20)
- Seq 2 Cue 44 `Duet - velky nebe -HNED`: score=69 | very hard-heavy cue (24 hard values); mixed programming in 8 fixture/family pairs; low similarity to neighbouring cues (0.03); touches unusually many feature groups (6); more mixed fixtures than neighbouring cues
- Seq 2 Cue 18 `Rackove rostazeny nohy 5:05`: score=68 | very hard-heavy cue (77 hard values); mixed programming in 32 fixture/family pairs; hard values spike vs local block (77 vs avg 23.4); many zero/reset-like values (22); more mixed fixtures than neighbouring cues
- Seq 2 Cue 14 `Groteska W. hodi zradlo`: score=67 | very hard-heavy cue (26 hard values); mixed programming in 4 fixture/family pairs; low similarity to neighbouring cues (0.07); hard values spike vs local block (26 vs avg 9.4)
- Seq 2 Cue 86 `lidi`: score=67 | very hard-heavy cue (265 hard values); mixed programming in 26 fixture/family pairs; low similarity to neighbouring cues (0.03); hard values spike vs local block (265 vs avg 110.0)
- Seq 2 Cue 24 `Jonatanuv PAD`: score=66 | very hard-heavy cue (49 hard values); mixed programming in 12 fixture/family pairs; noticeable local outlier (0.26); hard values spike vs local block (49 vs avg 23.0); more mixed fixtures than neighbouring cues

## Worst blocks
- Seq 2 cues 7 - 11: avg_score=51.0 | worst=83 | high cues=2, avg hard=32.4, avg similarity=0.15
- Seq 2 cues 8 - 12: avg_score=51.0 | worst=83 | high cues=2, avg hard=27.0, avg similarity=0.14
- Seq 2 cues 51 - 55: avg_score=50.6 | worst=83 | high cues=3, avg hard=77.8, avg similarity=0.16
- Seq 2 cues 23 - 27: avg_score=49.4 | worst=76 | high cues=2, avg hard=31.2, avg similarity=0.14
- Seq 2 cues 35 - 39: avg_score=48.8 | worst=61 | high cues=3, avg hard=20.2, avg similarity=0.11
- Seq 2 cues 80 - 85: avg_score=48.6 | worst=66 | high cues=3, avg hard=51.6, avg similarity=0.08
- Seq 2 cues 24 - 28: avg_score=48.0 | worst=76 | high cues=2, avg hard=32.2, avg similarity=0.16
- Seq 2 cues 36 - 40: avg_score=47.8 | worst=61 | high cues=3, avg hard=19.4, avg similarity=0.09

## Fixture inconsistency
- Fixture 202 `SPIDER 33 2` / Dimmer: hard=40, preset=23 | family uses both hard and preset control across 47 cues
- Fixture 201 `SPIDER 33 1` / Dimmer: hard=39, preset=20 | family uses both hard and preset control across 45 cues
- Fixture 101 `RSpiide3 1` / Dimmer: hard=33, preset=25 | family uses both hard and preset control across 46 cues
- Fixture 102 `RSpiide3 2` / Dimmer: hard=32, preset=28 | family uses both hard and preset control across 48 cues
- Fixture 101 `RSpiide3 1` / Color: hard=15, preset=23 | family uses both hard and preset control across 30 cues
- Fixture 102 `RSpiide3 2` / Color: hard=14, preset=26 | family uses both hard and preset control across 32 cues
- Fixture 201 `SPIDER 33 1` / Color: hard=15, preset=18 | family uses both hard and preset control across 26 cues
- Fixture 108 `RSpiide3 8` / Dimmer: hard=35, preset=14 | family uses both hard and preset control across 43 cues
- Fixture 106 `RSpiide3 6` / Dimmer: hard=32, preset=10 | family uses both hard and preset control across 36 cues
- Fixture 107 `RSpiide3 7` / Dimmer: hard=31, preset=16 | family uses both hard and preset control across 41 cues

## Repeated hard values
- Fixture 202 DIM=0.00: cues=27 | 2.4 Hudba | 2.9 Racek astery 2:32 | 2.10 Klek zjeveni | 2.11 J. SOLO - 2:47 | 2.12 Dotancuje v pravo cca 4:50 | 2.19 Usinani 6:24 | 2.20 Solo Zacatek Bert | 2.21.5 Zpatky stred ...
- Fixture 201 DIM=0.00: cues=26 | 2.4 Hudba | 2.9 Racek astery 2:32 | 2.10 Klek zjeveni | 2.11 J. SOLO - 2:47 | 2.12 Dotancuje v pravo cca 4:50 | 2.19 Usinani 6:24 | 2.20 Solo Zacatek Bert | 2.21.5 Zpatky stred ...
- Fixture 101 DIM=0.00: cues=14 | 2.4 Hudba | 2.9 Racek astery 2:32 | 2.11 J. SOLO - 2:47 | 2.12 Dotancuje v pravo cca 4:50 | 2.19 Usinani 6:24 | 2.26 Jonathan svicka | 2.32 Po procesu - s hudbou | 2.34 Jon.Zustava sam ...
- Fixture 106 DIM=0.00: cues=14 | 2.3 Prichod tanecniku | 2.9 Racek astery 2:32 | 2.18 Rackove rostazeny nohy 5:05 | 2.25 Vilda odchazi | 2.30.5 Soud - zelena- - bici hudba | 2.31 Soud - proces-Na-schody | 2.34 Jon.Zustava sam | 2.42 W.spot pryc ...
- Fixture 107 DIM=0.00: cues=14 | 2.4 Hudba | 2.9 Racek astery 2:32 | 2.12 Dotancuje v pravo cca 4:50 | 2.14 Groteska W. hodi zradlo | 2.21 cela plocha | 2.29 Skupina posmesky | 2.33 Vilda Domluvi | 2.37 Jdou tunelem skoro hned driv ...
- Fixture 108 DIM=0.00: cues=14 | 2.4 Hudba | 2.9 Racek astery 2:32 | 2.12 Dotancuje v pravo cca 4:50 | 2.20 Solo Zacatek Bert | 2.25 Vilda odchazi | 2.29 Skupina posmesky | 2.32 Po procesu - s hudbou | 2.37 Jdou tunelem skoro hned driv ...
- Fixture 102 DIM=0.00: cues=13 | 2.9 Racek astery 2:32 | 2.11 J. SOLO - 2:47 | 2.12 Dotancuje v pravo cca 4:50 | 2.19 Usinani 6:24 | 2.24 Jonatanuv PAD | 2.26 Jonathan svicka | 2.32 Po procesu - s hudbou | 2.38 Vkladaji astery POZA se k lidem-zastavi se ...
- Fixture 105 DIM=0.00: cues=10 | 2.3 Prichod tanecniku | 2.9 Racek astery 2:32 | 2.18 Rackove rostazeny nohy 5:05 | 2.20 Solo Zacatek Bert | 2.30.5 Soud - zelena- - bici hudba | 2.36 Jen prava strana - Wilda na schodech | 2.41 Jdou k nemu do rohu - Pouze astery | 2.55 Groteska boj o zradlo - Velikeho racka ...
- Fixture 13 DIM=100.00: cues=9 | 1.1 Cue 1 | 2.41 Jdou k nemu do rohu - Pouze astery | 2.57 Patrik ON | 2.60 Patrik ON | 2.66 Pat | 2.69 Astery ON | 2.71 Astery ON | 2.73 Astery ON ...
- Fixture 31 DIM=0.00: cues=9 | 2.16 Boj o zradlo - Na Housle 2:12 | 2.31 Soud - proces-Na-schody | 2.32 Po procesu - s hudbou | 2.35 zustava sam LET- GESTO | 2.41 Jdou k nemu do rohu - Pouze astery | 2.42 W.spot pryc | 2.43 Zhasnuti astery..Odkuleni c.9 | 2.55 Groteska boj o zradlo - Velikeho racka ...

## Dead objects
- preset 0.3: Schody
- preset 0.9: Preset 0.9
- preset 0.11: Eff Front
- preset 0.13: q80-flo
- preset 0.24: Prava strana
- preset 0.34: Pruvany rackove
- preset 0.42: Asteta Main
- preset 0.53: Kalibrace-stredni zadni kostka
- preset 0.54: Kalibrace - stredy
- preset 0.55: Kalibrace kostky

## Validation warnings
- Severity breakdown: high=8, medium=8, low=36
- Top kinds: unused_preset=36, fixture_used_without_patch_data=8, fixture_used_without_type=8
- high: fixture_used_without_patch_data | fixture:1001 | Fixture 1001
- medium: fixture_used_without_type | fixture:1001 | Fixture 1001
- high: fixture_used_without_patch_data | fixture:1002 | Fixture 1002
- medium: fixture_used_without_type | fixture:1002 | Fixture 1002
- high: fixture_used_without_patch_data | fixture:1003 | Fixture 1003
- medium: fixture_used_without_type | fixture:1003 | Fixture 1003
- high: fixture_used_without_patch_data | fixture:1004 | Fixture 1004
- medium: fixture_used_without_type | fixture:1004 | Fixture 1004
- high: fixture_used_without_patch_data | fixture:1005 | Fixture 1005
- medium: fixture_used_without_type | fixture:1005 | Fixture 1005
- high: fixture_used_without_patch_data | fixture:1006 | Fixture 1006
- medium: fixture_used_without_type | fixture:1006 | Fixture 1006
- high: fixture_used_without_patch_data | fixture:1007 | Fixture 1007
- medium: fixture_used_without_type | fixture:1007 | Fixture 1007
- high: fixture_used_without_patch_data | fixture:1008 | Fixture 1008
