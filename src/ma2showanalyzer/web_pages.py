from __future__ import annotations

import base64
import html
import json
import os
from pathlib import Path
from urllib.parse import quote

from .ai import load_cue_options, load_sequence_options
from .web_jobs import JobStore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMG_DIR = PROJECT_ROOT / "img"

STATUS_LABELS = {
    "completed": "Dokonceno",
    "processing": "Zpracovava se",
    "failed": "Selhalo",
    "uploaded": "Nahrano",
}

STAGE_LABELS = {
    "Upload received": "Upload prijat",
    "Uploads stored": "Soubory ulozeny",
    "Preparing analysis": "Priprava analyzy",
    "Parsing uploads": "Zpracovani uploadu",
    "Building reports": "Generovani reportu",
    "Completed": "Dokonceno",
    "Failed": "Selhalo",
}

REPORT_LABELS = {
    "dashboard.html": "Prehledovy dashboard",
    "patch.html": "Patch a fixture",
    "cue_list.html": "Seznam cue",
    "sequence_content.html": "Obsah sekvenci",
    "sequence_inspector.html": "Sequence inspector",
    "cue_quality.html": "Kvalita cue",
    "preset_logic_breaks.html": "Preset logic breaks",
    "missing_preset_opportunities.html": "Missing preset opportunities",
    "warnings.html": "Varovani",
    "explorer.html": "Průzkumnik vztahu",
    "topology_graphs.html": "Topology Graphs",
    "explorer_d3.html": "Průzkumnik D3",
    "explorer_sankey.html": "Průzkumnik Sankey",
    "explorer_radial.html": "Průzkumnik radialni",
    "analysis_overview.md": "Textovy souhrn analyzy",
    "summary.json": "Souhrn dat JSON",
    "risk_hotspots.csv": "Rizikova mista",
    "main_cue_analysis.csv": "Analyza hlavniho cue listu",
    "main_cue_analysis.json": "Analyza hlavniho cue listu JSON",
    "dashboard.html": "Přehledový dashboard",
    "sequence_content.html": "Obsah sekvencí",
    "warnings.html": "Varování",
    "explorer.html": "Průzkumník vztahů",
    "explorer_d3.html": "Průzkumník D3",
    "explorer_sankey.html": "Průzkumník Sankey",
    "explorer_radial.html": "Průzkumník radiální",
    "analysis_overview.md": "Textový souhrn analýzy",
    "risk_hotspots.csv": "Riziková místa",
    "main_cue_analysis.csv": "Analýza hlavního cue listu",
    "main_cue_analysis.json": "Analýza hlavního cue listu JSON",
}


def web_logo_src() -> str:
    logo_path = IMG_DIR / "logo_graindma.png"
    if not logo_path.exists():
        return "/static/logo_graindma.png"
    encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def html_page(title: str, body: str) -> str:
    logo_src = web_logo_src()
    return f"""<!doctype html>
<html lang="cs">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; background: #0f172a; color: #e5e7eb; }}
    header {{ padding: 24px; background: #111827; border-bottom: 1px solid #334155; }}
    .header-inner {{ max-width: 1200px; margin: 0 auto; display:flex; gap:18px; align-items:center; flex-wrap:wrap; }}
    .header-brand img {{ width:min(240px, 34vw); max-width:100%; height:auto; object-fit:contain; border-radius:0; padding:0; background:none; border:none; box-shadow:0 8px 24px rgba(0,0,0,.18); }}
    .brand-copy {{ min-width: 0; }}
    .wrap {{ padding: 24px; max-width: 1200px; margin: 0 auto; }}
    .card {{ background: #1f2937; border: 1px solid #334155; border-radius: 16px; padding: 18px; margin-bottom: 18px; box-shadow: 0 4px 20px rgba(0,0,0,.18); }}
    .muted {{ color: #94a3b8; font-size: 12px; }}
    .progress-shell {{ margin-top: 14px; background:#0b1220; border:1px solid #334155; border-radius:999px; height:16px; overflow:hidden; }}
    .progress-fill {{ height:100%; width:0%; background:linear-gradient(90deg,#38bdf8,#22c55e); transition: width .18s ease; }}
    .hidden {{ display:none !important; }}
    input[type=file], input[type=text], button, select {{ padding: 10px 12px; border-radius: 10px; border: 1px solid #334155; background: #0b1220; color: #e5e7eb; }}
    button {{ cursor: pointer; }}
    button:hover {{ background: #172033; }}
    a {{ color: #7dd3fc; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; margin-right: 6px; }}
    .pill-completed {{ background: #14532d; color: #bbf7d0; }}
    .pill-processing {{ background: #082f49; color: #bae6fd; }}
    .pill-failed {{ background: #7f1d1d; color: #fecaca; }}
    .pill-uploaded {{ background: #334155; color: #e5e7eb; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ text-align: left; border-bottom: 1px solid #334155; padding: 8px; vertical-align: top; }}
    .code {{ white-space: pre-wrap; word-break: break-word; font-family: Consolas, monospace; font-size: 12px; }}
    .row {{ display:flex; gap:12px; flex-wrap:wrap; align-items:center; }}
    .danger-btn {{ padding:8px 12px; border-radius:10px; border:1px solid #7f1d1d; background:#3f1010; color:#fecaca; cursor:pointer; }}
    .danger-btn:hover {{ background:#571313; }}
  </style>
</head>
<body>
<header>
  <div class="header-inner">
    <div class="header-brand">
      <img src="{logo_src}" alt="grandMA2 Show Analyzer logo">
    </div>
    <div class="brand-copy">
      <h1 style="margin:0 0 8px;">grandMA2 Show Analyzer</h1>
      <div class="muted">Lokalni webova verze pro nahrani exportu a automaticke generovani reportu.</div>
    </div>
  </div>
</header>
<div class="wrap">
{body}
</div>
</body>
</html>"""


def status_badge(status: str) -> str:
    safe = html.escape(STATUS_LABELS.get(status, status or "Neznamy stav"))
    css = {
        "completed": "pill-completed",
        "processing": "pill-processing",
        "failed": "pill-failed",
        "uploaded": "pill-uploaded",
    }.get(status, "pill-uploaded")
    return f'<span class="pill {css}">{safe}</span>'


def localized_stage(stage: str) -> str:
    return STAGE_LABELS.get(stage, stage)


def localized_report_label(name: str) -> str:
    return REPORT_LABELS.get(name, name)


def localized_provider(provider: str) -> str:
    mapping = {
        "ollama": "Ollama",
        "openai": "OpenAI",
    }
    return mapping.get((provider or "").strip().lower(), provider or "neznamy")


def build_home_page(store: JobStore, message: str = "") -> str:
    jobs = store.list_jobs()
    rows = []
    for job in jobs[:30]:
        job_id = html.escape(str(job.get("job_id", "")))
        source_names = ", ".join(map(str, job.get("source_names", [])[:4]))
        if len(job.get("source_names", []) or []) > 4:
            source_names += " ..."
        stage_label = localized_stage(str(job.get("stage", "")))
        rows.append(
            f"<tr>"
            f"<td><a href=\"/jobs/{job_id}\">{job_id}</a></td>"
            f"<td>{status_badge(str(job.get('status', 'uploaded')))}</td>"
            f"<td>{html.escape(stage_label)} ({int(job.get('progress', 0) or 0)}%)</td>"
            f"<td>{html.escape(str(job.get('created_at', '')))}</td>"
            f"<td>{html.escape(source_names)}"
            f"<div style=\"margin-top:8px;\">"
            f"<form method=\"post\" action=\"/delete-job\" onsubmit=\"return confirm('Opravdu smazat job {job_id}?');\">"
            f"<input type=\"hidden\" name=\"job_id\" value=\"{job_id}\">"
            f"<button class=\"danger-btn\" type=\"submit\">Smazat job</button>"
            f"</form>"
            f"</div>"
            f"</td>"
            f"</tr>"
        )
    jobs_table = "\n".join(rows) if rows else '<tr><td colspan="5">Zatim zadne analyzy.</td></tr>'
    message_html = f'<div class="card">{html.escape(message)}</div>' if message else ""
    return html_page(
        "grandMA2 Show Analyzer",
        f"""
        {message_html}
        <div class="grid">
          <div class="card">
            <h2 style="margin-top:0;">Nova analyza</h2>
            <div class="muted">Nahrajte XML nebo CSV exporty, pripadne ZIP s exporty. Server vytvori novy job a rovnou vygeneruje vsechny reporty.</div>
            <form id="uploadForm" action="/analyze" method="post" enctype="multipart/form-data" style="margin-top:14px;">
                <div class="row" style="margin-bottom:12px;">
                  <input id="uploadFiles" type="file" name="files" multiple required style="flex:1;">
                </div>
                <div class="muted" style="margin-bottom:12px;">Podporovano: vice souboru najednou i ZIP archiv.</div>
              <button id="uploadSubmit" type="submit">Nahrat a spustit analyzu</button>
              <div id="uploadStatus" class="muted hidden" style="margin-top:10px;">Pripravuji upload...</div>
              <div id="uploadProgressWrap" class="progress-shell hidden">
                <div id="uploadProgressBar" class="progress-fill"></div>
              </div>
            </form>
          </div>
          <div class="card">
            <h2 style="margin-top:0;">Co server dela</h2>
            <div class="code">1. ulozi upload do samostatne slozky jobu
2. spusti parser a analyzu
3. vygeneruje dashboard, patch, seznam cue, varovani a vsechny pruzkumniky
4. zpristupni vysledek pres lokalni web</div>
          </div>
        </div>
          <div class="card">
            <h2 style="margin-top:0;">Posledni joby</h2>
            <table>
              <thead><tr><th>Job</th><th>Stav</th><th>Prubeh</th><th>Vytvoreno</th><th>Soubory</th></tr></thead>
              <tbody>{jobs_table}</tbody>
            </table>
          </div>
          <script>
            (function () {{
              const form = document.getElementById('uploadForm');
              const files = document.getElementById('uploadFiles');
              const submit = document.getElementById('uploadSubmit');
              const status = document.getElementById('uploadStatus');
              const wrap = document.getElementById('uploadProgressWrap');
              const bar = document.getElementById('uploadProgressBar');
              if (!form || !files || !submit || !status || !wrap || !bar || !window.XMLHttpRequest) {{
                return;
              }}
              form.addEventListener('submit', function (event) {{
                event.preventDefault();
                if (!files.files || !files.files.length) {{
                  status.textContent = 'Vyber aspon jeden soubor.';
                  status.classList.remove('hidden');
                  return;
                }}
                const data = new FormData(form);
                const xhr = new XMLHttpRequest();
                submit.disabled = true;
                files.disabled = true;
                wrap.classList.remove('hidden');
                status.classList.remove('hidden');
                status.textContent = 'Nahravam soubory...';
                bar.style.width = '0%';
                xhr.upload.addEventListener('progress', function (e) {{
                  if (!e.lengthComputable) {{
                    status.textContent = 'Nahravam soubory...';
                    return;
                  }}
                  const percent = Math.max(0, Math.min(100, Math.round((e.loaded / e.total) * 100)));
                  bar.style.width = percent + '%';
                  status.textContent = 'Nahravam soubory... ' + percent + '%';
                }});
                xhr.addEventListener('load', function () {{
                  if (xhr.status >= 200 && xhr.status < 400) {{
                    status.textContent = 'Upload dokonceny. Oteviram job...';
                    bar.style.width = '100%';
                    const target = xhr.responseURL || '/';
                    window.location.assign(target);
                    return;
                  }}
                  submit.disabled = false;
                  files.disabled = false;
                  status.textContent = 'Upload selhal. Zkus to prosim znovu.';
                }});
                xhr.addEventListener('error', function () {{
                  submit.disabled = false;
                  files.disabled = false;
                  status.textContent = 'Chyba spojeni pri uploadu.';
                }});
                xhr.open('POST', form.action, true);
                xhr.send(data);
              }});
            }})();
          </script>
          """,
    )


def build_job_page(store: JobStore, job_id: str) -> str:
    meta = store.load_meta(job_id)
    if not meta:
        return html_page("Job nenalezen", f'<div class="card"><a href="/">Zpet</a><p>Job {html.escape(job_id)} nebyl nalezen.</p></div>')
    status = str(meta.get("status", "uploaded"))
    stage = str(meta.get("stage", ""))
    progress = max(0, min(100, int(meta.get("progress", 0) or 0)))
    auto_refresh = status in {"uploaded", "processing"}
    files = store.report_files(job_id)
    report_links = []
    preferred = [
        "dashboard.html",
        "patch.html",
        "cue_list.html",
        "sequence_content.html",
        "sequence_inspector.html",
        "cue_quality.html",
        "preset_logic_breaks.html",
        "missing_preset_opportunities.html",
        "warnings.html",
        "explorer.html",
        "topology_graphs.html",
        "explorer_d3.html",
        "explorer_sankey.html",
        "explorer_radial.html",
        "analysis_overview.md",
    ]
    file_map = {path.name: path for path in files}
    ordered_names = [name for name in preferred if name in file_map] + [name for name in sorted(file_map) if name not in preferred]
    for name in ordered_names:
        url = f"/jobs/{quote(job_id)}/reports/{quote(name)}"
        report_links.append(
            f'<li><a href="{url}" target="_blank">{html.escape(localized_report_label(name))}</a> '
            f'<span class="muted">({html.escape(name)})</span></li>'
        )
    error_text = ""
    error_path = store.error_path(job_id)
    if error_path.exists():
        error_text = error_path.read_text(encoding="utf-8")
    cue_options = load_cue_options(store.output_dir(job_id))
    sequence_options = load_sequence_options(store.output_dir(job_id))
    cue_options_markup = "".join(
        f'<option value="{html.escape(item["sequence_number"])}::{html.escape(item["cue_number"])}">{html.escape(item["label"])}</option>'
        for item in cue_options
    )
    sequence_options_markup = "".join(
        f'<option value="{html.escape(item["sequence_number"])}">{html.escape(item["label"])}</option>'
        for item in sequence_options
    )
    ai_provider = (os.getenv("MA2_AI_PROVIDER", "ollama") or "ollama").strip().lower()
    ai_enabled = ai_provider == "ollama" or bool(os.getenv("OPENAI_API_KEY", "").strip())
    markup = html_page(
        f"Job {job_id}",
        f"""
        <div class="card">
          <div class="row">
            <a href="/">← Zpet na nahravky</a>
            {status_badge(status)}
          </div>
          <h2 style="margin-bottom:8px;">Job {html.escape(job_id)}</h2>
          <div class="muted">Vytvoreno: {html.escape(str(meta.get("created_at", "")))}</div>
          <div class="muted">Aktualizovano: {html.escape(str(meta.get("updated_at", "")))}</div>
          <div class="muted">Soubory: {html.escape(", ".join(map(str, meta.get("source_names", []))))}</div>
          <div class="muted" style="margin-top:10px;">Faze: {html.escape(localized_stage(stage))} | Prubeh: {progress}%</div>
          <div style="margin-top:10px; background:#0b1220; border:1px solid #334155; border-radius:999px; height:14px; overflow:hidden;">
            <div style="height:100%; width:{progress}%; background:linear-gradient(90deg,#38bdf8,#22c55e);"></div>
          </div>
          {('<div class="muted" style="margin-top:8px;">Stranka se automaticky obnovuje, dokud job bezi.</div>' if auto_refresh else '')}
        </div>
        <div class="grid">
          <div class="card">
            <h3 style="margin-top:0;">Reporty</h3>
            <ul>
              {''.join(report_links) if report_links else '<li>Zatim nic negenerovano.</li>'}
            </ul>
          </div>
          <div class="card">
            <h3 style="margin-top:0;">Stav</h3>
            <div class="code">{html.escape(str(meta.get("error", "")) or "Bez chyby.")}</div>
          </div>
        </div>
        <div class="card">
          <h3 style="margin-top:0;">AI analyza cue</h3>
          <div class="muted">Vyberte cue z hlavniho cue listu a server pripravi prompt z reportu `main_cue_analysis`. Podporovana je lokalni Ollama i OpenAI kompatibilni endpoint.</div>
          <form id="aiCueForm" style="margin-top:14px;">
            <input type="hidden" name="job_id" value="{html.escape(job_id)}">
            <div class="row">
              <select id="aiCueSelect" name="cue_key" {'disabled' if not cue_options else ''} style="min-width:320px; flex:1;">
                {cue_options_markup or '<option value="">Zatim nejsou k dispozici data main cue.</option>'}
              </select>
              <button id="aiCueButton" type="submit" {'disabled' if not cue_options else ''}>Analyzovat cue</button>
            </div>
          </form>
          <div class="muted" style="margin-top:10px;">{html.escape(f'AI poskytovatel: {localized_provider(ai_provider)}. ' + ('AI je pripraveno.' if ai_enabled else 'AI zatim neni aktivni: chybi konfigurace provideru.'))}</div>
          <div id="aiCueStatus" class="muted" style="margin-top:10px;">{html.escape('Vyberte cue a spustte analyzu.' if cue_options else 'Nejprve pockejte na vygenerovani reportu hlavniho cue listu.')}</div>
          <pre id="aiCueResult" class="code" style="margin-top:14px; padding:14px; background:#0b1220; border:1px solid #334155; border-radius:12px; min-height:120px;">Vysledek AI analyzy se zobrazi tady.</pre>
        </div>
        <div class="grid">
          <div class="card">
            <h3 style="margin-top:0;">AI analyza cele sekvence</h3>
            <div class="muted">Shrne dramaturgii sekvence, programatorske vzory a navrhne uklid nebo refaktor cue listu.</div>
            <form id="aiSequenceForm" style="margin-top:14px;">
              <div class="row">
                <select id="aiSequenceSelect" name="sequence_number" {'disabled' if not sequence_options else ''} style="min-width:280px; flex:1;">
                  {sequence_options_markup or '<option value="">Zatim nejsou k dispozici sekvence.</option>'}
                </select>
                <button id="aiSequenceButton" type="submit" {'disabled' if not sequence_options else ''}>Analyzovat sekvenci</button>
              </div>
            </form>
            <div id="aiSequenceStatus" class="muted" style="margin-top:10px;">{html.escape('Vyberte sekvenci a spustte analyzu.' if sequence_options else 'Nejprve pockejte na vygenerovani reportu sekvenci.')}</div>
            <pre id="aiSequenceResult" class="code" style="margin-top:14px; padding:14px; background:#0b1220; border:1px solid #334155; border-radius:12px; min-height:160px;">Vysledek AI analyzy sekvence se zobrazi tady.</pre>
          </div>
          <div class="card">
            <h3 style="margin-top:0;">AI nejrizikovejsi cue</h3>
            <div class="muted">Vezme nejrizikovejsi cue z `risk_hotspots.csv`, vysvetli proc jsou rizikove a urci, co zkontrolovat jako prvni.</div>
            <form id="aiRiskForm" style="margin-top:14px;">
              <div class="row">
                <select id="aiRiskScope" name="sequence_number" style="min-width:280px; flex:1;">
                  <option value="">Cela show</option>
                  {sequence_options_markup}
                </select>
                <button id="aiRiskButton" type="submit">Analyzovat rizika</button>
              </div>
            </form>
            <div id="aiRiskStatus" class="muted" style="margin-top:10px;">Spustte analyzu rizik a AI oznaci nejproblemovejsi cue.</div>
            <pre id="aiRiskResult" class="code" style="margin-top:14px; padding:14px; background:#0b1220; border:1px solid #334155; border-radius:12px; min-height:160px;">AI rozbor rizikovych cue se zobrazi tady.</pre>
          </div>
        </div>
        {f'<div class="card"><h3 style="margin-top:0;">Traceback</h3><div class="code">{html.escape(error_text)}</div></div>' if error_text else ''}
        <script>
          (function () {{
            function localizeProviderName(name) {{
              const value = (name || '').toLowerCase();
              if (value === 'ollama') return 'Ollama';
              if (value === 'openai') return 'OpenAI';
              return name || 'neznamy';
            }}
            const form = document.getElementById('aiCueForm');
            const select = document.getElementById('aiCueSelect');
            const button = document.getElementById('aiCueButton');
            const statusNode = document.getElementById('aiCueStatus');
            const resultNode = document.getElementById('aiCueResult');
            if (!form || !select || !button || !statusNode || !resultNode || !window.fetch) {{
              return;
            }}
            form.addEventListener('submit', async function (event) {{
              event.preventDefault();
              if (!select.value) {{
                statusNode.textContent = 'Vyberte cue pro analyzu.';
                return;
              }}
              button.disabled = true;
              statusNode.textContent = 'Posilam data cue do AI...';
              resultNode.textContent = 'Analyza probiha...';
              try {{
                const response = await fetch('/ai-analyze-cue', {{
                  method: 'POST',
                  headers: {{ 'Content-Type': 'application/json' }},
                  body: JSON.stringify({{
                    job_id: {json.dumps(job_id)},
                    cue_key: select.value
                  }})
                }});
                const payload = await response.json();
                if (!response.ok || !payload.ok) {{
                  throw new Error(payload.error || 'AI analyza selhala.');
                }}
                statusNode.textContent = 'Analyza hotova. Poskytovatel: ' + localizeProviderName(payload.provider) + ', model: ' + (payload.model || 'neznamy') + (payload.cached ? ' (z cache)' : '');
                resultNode.textContent = payload.analysis || 'AI nevratila zadny text.';
              }} catch (error) {{
                statusNode.textContent = 'AI analyza se nepovedla.';
                resultNode.textContent = error && error.message ? error.message : 'Neznama chyba.';
              }} finally {{
                button.disabled = false;
              }}
            }});

            async function runAiRequest(config) {{
              const {{ buttonNode, statusNodeRef, resultNodeRef, endpoint, body, runningText, donePrefix, emptyMessage }} = config;
              buttonNode.disabled = true;
              statusNodeRef.textContent = runningText;
              resultNodeRef.textContent = 'Analyza probiha...';
              try {{
                const response = await fetch(endpoint, {{
                  method: 'POST',
                  headers: {{ 'Content-Type': 'application/json' }},
                  body: JSON.stringify(body)
                }});
                const payload = await response.json();
                if (!response.ok || !payload.ok) {{
                  throw new Error(payload.error || 'AI analyza selhala.');
                }}
                statusNodeRef.textContent = donePrefix + ' Poskytovatel: ' + localizeProviderName(payload.provider) + ', model: ' + (payload.model || 'neznamy') + (payload.cached ? ' (z cache)' : '');
                resultNodeRef.textContent = payload.analysis || emptyMessage;
              }} catch (error) {{
                statusNodeRef.textContent = 'AI analyza se nepovedla.';
                resultNodeRef.textContent = error && error.message ? error.message : 'Neznama chyba.';
              }} finally {{
                buttonNode.disabled = false;
              }}
            }}

            const sequenceForm = document.getElementById('aiSequenceForm');
            const sequenceSelect = document.getElementById('aiSequenceSelect');
            const sequenceButton = document.getElementById('aiSequenceButton');
            const sequenceStatus = document.getElementById('aiSequenceStatus');
            const sequenceResult = document.getElementById('aiSequenceResult');
            if (sequenceForm && sequenceSelect && sequenceButton && sequenceStatus && sequenceResult) {{
              sequenceForm.addEventListener('submit', function (event) {{
                event.preventDefault();
                if (!sequenceSelect.value) {{
                  sequenceStatus.textContent = 'Vyberte sekvenci pro analyzu.';
                  return;
                }}
                runAiRequest({{
                  buttonNode: sequenceButton,
                  statusNodeRef: sequenceStatus,
                  resultNodeRef: sequenceResult,
                  endpoint: '/ai-analyze-sequence',
                  body: {{ job_id: {json.dumps(job_id)}, sequence_number: sequenceSelect.value }},
                  runningText: 'Posilam data sekvence do AI...',
                  donePrefix: 'Analyza sekvence hotova.',
                  emptyMessage: 'AI nevratila zadny text.'
                }});
              }});
            }}

            const riskForm = document.getElementById('aiRiskForm');
            const riskScope = document.getElementById('aiRiskScope');
            const riskButton = document.getElementById('aiRiskButton');
            const riskStatus = document.getElementById('aiRiskStatus');
            const riskResult = document.getElementById('aiRiskResult');
            if (riskForm && riskScope && riskButton && riskStatus && riskResult) {{
              riskForm.addEventListener('submit', function (event) {{
                event.preventDefault();
                runAiRequest({{
                  buttonNode: riskButton,
                  statusNodeRef: riskStatus,
                  resultNodeRef: riskResult,
                  endpoint: '/ai-risk-cues',
                  body: {{ job_id: {json.dumps(job_id)}, sequence_number: riskScope.value }},
                  runningText: 'Posilam data rizikovych cue do AI...',
                  donePrefix: 'Analyza rizik hotova.',
                  emptyMessage: 'AI nevratila zadny text.'
                }});
              }});
            }}
          }})();
        </script>
        """,
    )
    if auto_refresh:
        return markup.replace("<head>", '<head>\n  <meta http-equiv="refresh" content="2">', 1)
    return markup
