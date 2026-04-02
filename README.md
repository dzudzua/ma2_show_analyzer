# grandMA2 Show Analyzer

Kompletní offline systém pro analýzu `grandMA2` show z XML a CSV exportů.

Umí:
- načíst exporty `Sequence`, `Cue`, `Preset`, `Group`, `Effect` a patch data
- rozlišovat `hard values` vs `preset references`
- hledat reference na presety, efekty, groups a další objekty show
- vyhodnocovat timingy jako `fade`, `delay`, `trigger` a `trigger time`
- vytvářet vazby mezi objekty show
- počítat využití fixture ID a patch targetů
- generovat CSV, JSON a HTML reporty

Parser je navržený heuristicky, aby fungoval i nad rozdílnými variantami exportů z různých verzí grandMA2.

## Architektura

```text
ma2_show_analyzer/
├─ lua/
│  ├─ export_show_bundle.lua
│  └─ export_patch.lua
├─ src/
│  └─ ma2showanalyzer/
│     ├─ __main__.py
│     ├─ cli.py
│     ├─ models.py
│     ├─ parser.py
│     ├─ analyzer.py
│     ├─ reporters.py
│     ├─ reporting_html.py
│     ├─ reporting_io.py
│     ├─ webapp.py
│     ├─ web_jobs.py
│     └─ web_pages.py
├─ templates/
├─ img/
├─ run_analysis.py
├─ run_web_app.py
└─ README.md
```

## Datový model

Hlavní entity:
- `Sequence`
- `Cue`
- `Preset`
- `Group`
- `Effect`
- `PatchFixture`
- `ValueAtom`
- `Relationship`
- `ShowData`

### Cue

Cue obsahuje zejména:
- `sequence_number`
- `cue_number`
- `name`
- `fade`
- `delay`
- `trigger`
- `trigger_time`
- `down_delay`
- `command`
- `part`
- `fixture_ids`
- `references`
- `values`

### ValueAtom

Jednotlivý atom hodnoty ve value datech:
- `attribute`
- `raw_value`
- `value_type`
- `fixture_id`
- `channel_id`
- `patch_target_key`
- `reference_target`
- `flags`

## Tok dat

1. grandMA2 plugin vyexportuje XML a CSV soubory.
2. Parser projde adresář exportů a rozpozná typy objektů.
3. Analyzer postaví vztahy, usage statistiky a validační warningy.
4. Reporter vygeneruje CSV, JSON a HTML reporty.

## Lua plugin pro grandMA2

Hlavní plugin:
- `lua/export_show_bundle.lua`

Pomocný patch plugin:
- `lua/export_patch.lua`

### Co exportuje `export_show_bundle.lua`

- hlavní sequence nebo range pro primární analýzu
- všechny sequence v definovaném rozsahu
- groups
- effects
- patch jako transformované CSV
- preset pooly `0` až `14`

### Doporučený postup v MA2

1. Otevři `Plugin Pool`.
2. Vytvoř nový plugin.
3. Vlož obsah `lua/export_show_bundle.lua`.
4. Spusť plugin.
5. Zadej prefix, hlavní sequence, maximální rozsah poolů a cílový disk.

Plugin exportuje soubory do `importexport`.

## Instalace

```bash
cd ma2_show_analyzer
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instalace balíčku:

```bash
pip install -e .
```

## CLI použití

Základní analýza:

```bash
python -m ma2showanalyzer analyze \
  --input ./exports \
  --output ./out
```

Rekurzivní hledání:

```bash
python -m ma2showanalyzer analyze \
  --input ./exports \
  --output ./out \
  --recursive \
  --glob "*.xml"
```

Windows wrapper:

```bat
run_analysis.bat
```

PowerShell wrapper:

```powershell
.\run_analysis.ps1
```

## Doporučený workflow pro hlavní cue list

Použij `lua/export_show_bundle.lua` a jako `Main Sequence or range` zadej číslo hlavního cue listu, například `1`.

Typické výstupy:
- `*_main_sequences.xml`
- `*_all_sequences.xml`
- `*_groups.xml`
- `*_effects.xml`
- `*_patch.csv`
- `*_preset_0.xml` až `*_preset_14.xml`

Pak spusť analýzu:

```powershell
$env:PYTHONPATH='src'
python -m ma2showanalyzer analyze --input exports --output out
```

## Lokální webová verze

Projekt umí běžet i jako lokální web aplikace:

1. spustíš server
2. v prohlížeči nahraješ XML, CSV nebo ZIP
3. server vytvoří nový job
4. automaticky vygeneruje reporty
5. výsledky otevřeš přes lokální web

### Spuštění

Windows wrapper:

```bat
run_web_app.bat
```

S parametry:

```bat
run_web_app.bat -Port 8765 -DataDir web_jobs
```

Přímo přes Python:

```bash
python run_web_app.py --host 127.0.0.1 --port 8765 --open-browser
```

Nebo přes CLI:

```bash
python -m ma2showanalyzer serve --host 127.0.0.1 --port 8765 --open-browser
```

### Co web podporuje

- upload více souborů najednou
- upload ZIP archivu
- per-job ukládání uploadů i výstupů
- přehled jobů
- odkazy na všechny hlavní reporty

### Struktura jobů

```text
web_jobs/
web_jobs/<job_id>/uploads
web_jobs/<job_id>/out
web_jobs/<job_id>/meta.json
```

## Patch vrstva

Patch vrstva a doporučený datový model jsou popsané v:

- `PATCH_LAYER.md`

Parser umí načítat:
- transformované patch CSV
- patch metadata z XML exportů
- fixture i channel orientované patch informace

## Hlavní výstupy

### JSON

- `summary.json`
- `relationships.json`
- `fixtures.json`
- `patch_registry.json`
- `patch_summary.json`
- `fixture_types.json`
- `normalized_references.json`
- `warnings.json`
- `show_model_v2.json`

### CSV

- `sequences.csv`
- `cues.csv`
- `presets.csv`
- `groups.csv`
- `effects.csv`
- `relationships.csv`
- `value_atoms.csv`
- `fixture_usage.csv`
- `patch_registry.csv`
- `patch_fixtures.csv`

### Speciální hlavní cue reporty

- `main_cue_analysis.csv`
- `main_cue_value_atoms.csv`
- `main_cue_analysis.json`
- `sequence_content.csv`

### HTML

- `dashboard.html`
- `cue_list.html`
- `warnings.html`
- `cue_quality.html`
- `patch.html`
- `sequence_content.html`
- `sequence_inspector.html`
- `preset_logic_breaks.html`
- `missing_preset_opportunities.html`
- `explorer.html`
- `explorer_d3.html`
- `explorer_radial.html`
- `explorer_sankey.html`
- `topology_graphs.html`

## Co je vidět v hlavním cue reportu

Po jednotlivých cues uvidíš:
- `trigger`
- `trigger_time`
- `fade`
- `delay`
- `down_delay`
- `command`
- použitá fixture ID
- reference na presety, efekty a groups
- hard hodnoty a jejich atributy

## Jak systém detekuje vazby

### Preset references

Hledají se v:
- XML atributech typu `link`, `ref`, `preset`, `source`, `presetno`
- textových hodnotách typu `Preset 4.12` nebo `4.12`
- value blocích cue a presetů

### Effect references

Hledají se v:
- atributech a textech obsahujících `Effect`
- hodnotách typu `Effect 12`

### Group references

Hledají se v:
- command textech
- atributech
- value blocích

### Fixture usage

Kombinuje:
- fixture IDs nalezená přímo ve value datech
- fixture IDs z groups
- fixture IDs v cue, preset a effect datech

### Hard values

Value atom je označen jako `hard`, když:
- obsahuje konkrétní hodnotu atributu
- a současně nejde o rozpoznanou referenci na preset, effect nebo group

## Limitace

1. grandMA2 XML není jednotné API a různé verze exportují odlišnou strukturu.
2. Některé reference jsou implicitní nebo uložené netriviálně, proto je parser heuristický.
3. U atypických show může být potřeba doplnit další patterny do `parser.py`.

## Další rozšíření

Možné budoucí směry:
- diff dvou show exportů
- orphan preset a dead group detekce
- heatmap fixture usage po sequence
- další validační pravidla
- automatické porovnání konzistence patch dat
- live watcher složky s auto-refresh reportů

