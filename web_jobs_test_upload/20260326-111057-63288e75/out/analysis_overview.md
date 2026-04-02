# grandMA2 Show Analysis

## Summary
- Main sequences: 1
- Main cue count: 91
- Presets loaded: 56
- Groups loaded: 6
- Effects loaded: 0
- Patch fixtures loaded: 50
- Used fixtures total: 58
- Used fixtures without patch mapping: 0
- Unified model export: `show_model_v2.json`
- Validation warnings: 122

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
- Fixture 2 `HelDGB8S 2`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.025, cues=70, hard atoms=35
- Fixture 3 `HelDGB8S 3`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.049, cues=68, hard atoms=29
- Fixture 4 `HelDGB8S 4`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.073, cues=67, hard atoms=25
- Fixture 5 `HelDGB8S 5`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.097, cues=63, hard atoms=38
- Fixture 6 `HelDGB8S 6`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.121, cues=63, hard atoms=25
- Fixture 7 `HelDGB8S 7`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.145, cues=63, hard atoms=23
- Fixture 8 `HelDGB8S 8`: type=6 Helios Tube 42: RGB RGB - 8 Pixels - Strobe Off, patch=1.169, cues=63, hard atoms=31
- Fixture 101 `RSpiide3 1`: type=7 Robin Spiider Mode 3, patch=4.034, cues=51, hard atoms=519
- Fixture 102 `RSpiide3 2`: type=7 Robin Spiider Mode 3, patch=4.001, cues=51, hard atoms=521
- Fixture 202 `SPIDER 33 2`: type=7 Robin Spiider Mode 3, patch=4.436, cues=50, hard atoms=389

## Hottest presets
- Preset 0.16 `Start Front`: cues=4, sequences=1, fixtures=4, status=active
- Preset 0.18 `F-DoHnizda`: cues=4, sequences=1, fixtures=2, status=active
- Preset 0.49 `Do zdi-Start`: cues=4, sequences=1, fixtures=2, status=active
- Preset 0.5 `front`: cues=4, sequences=1, fixtures=4, status=active
- Preset 0.6 `Zeme Pruvany`: cues=4, sequences=1, fixtures=2, status=active
- Preset 0.17 `Q6-9`: cues=3, sequences=1, fixtures=4, status=active
- Preset 0.20 `Soud`: cues=3, sequences=1, fixtures=10, status=active
- Preset 0.4 `tepla vsude`: cues=3, sequences=1, fixtures=10, status=active
- Preset 0.66 `Jirka-Schody`: cues=3, sequences=1, fixtures=1, status=active
- Preset 0.1 `Kontra Zaklad`: cues=2, sequences=1, fixtures=4, status=active

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
- Severity breakdown: high=100, medium=8, low=14
- Top kinds: missing_target_object=92, unused_preset=14, fixture_used_without_patch_data=8, fixture_used_without_type=8
- high: missing_target_object | cue:cue:2:9:Tram_Analyz_main_sequences.xml:10 | missing target preset:4.10
- high: missing_target_object | cue:cue:2:9:Tram_Analyz_main_sequences.xml:10 | missing target preset:4.10
- high: missing_target_object | cue:cue:2:9:Tram_Analyz_main_sequences.xml:10 | missing target preset:4.10
- high: missing_target_object | cue:cue:2:9:Tram_Analyz_main_sequences.xml:10 | missing target preset:4.10
- high: missing_target_object | cue:cue:2:14:Tram_Analyz_main_sequences.xml:16 | missing target preset:4.10
- high: missing_target_object | cue:cue:2:14:Tram_Analyz_main_sequences.xml:16 | missing target preset:4.10
- high: missing_target_object | cue:cue:2:14:Tram_Analyz_main_sequences.xml:16 | missing target preset:4.10
- high: missing_target_object | cue:cue:2:14:Tram_Analyz_main_sequences.xml:16 | missing target preset:4.10
- high: missing_target_object | cue:cue:2:15:Tram_Analyz_main_sequences.xml:17 | missing target preset:4.10
- high: missing_target_object | cue:cue:2:15:Tram_Analyz_main_sequences.xml:17 | missing target preset:4.10
- high: missing_target_object | cue:cue:2:15:Tram_Analyz_main_sequences.xml:17 | missing target preset:4.10
- high: missing_target_object | cue:cue:2:15:Tram_Analyz_main_sequences.xml:17 | missing target preset:4.10
- high: missing_target_object | cue:cue:2:16:Tram_Analyz_main_sequences.xml:18 | missing target preset:4.11
- high: missing_target_object | cue:cue:2:16:Tram_Analyz_main_sequences.xml:18 | missing target preset:4.11
- high: missing_target_object | cue:cue:2:16:Tram_Analyz_main_sequences.xml:18 | missing target preset:4.11
