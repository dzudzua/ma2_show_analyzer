# grandMA2 Audit Report

## Dependency map
- Cues analyzed: 111

## Preset heatmap
- Preset 0.16: cues=4, sequences=1, status=active, duplicates=0
- Preset 0.18: cues=4, sequences=1, status=active, duplicates=0
- Preset 0.49: cues=4, sequences=1, status=active, duplicates=0
- Preset 0.5: cues=4, sequences=1, status=active, duplicates=0
- Preset 0.6: cues=4, sequences=1, status=active, duplicates=0
- Preset 0.17: cues=3, sequences=1, status=active, duplicates=0
- Preset 0.20: cues=3, sequences=1, status=active, duplicates=0
- Preset 0.4: cues=3, sequences=1, status=active, duplicates=0
- Preset 0.66: cues=3, sequences=1, status=active, duplicates=0
- Preset 0.1: cues=2, sequences=1, status=active, duplicates=0

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
