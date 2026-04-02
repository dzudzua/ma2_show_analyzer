(function () {
  "use strict";

  const dataNode = document.getElementById("sequenceInspectorData");
  const DATA = dataNode ? JSON.parse(dataNode.textContent || "{}") : {};
  const WARNING_THRESHOLDS = {
    longFade: 8,
    longDelay: 3,
    manyFixtures: 12,
  };

  const COLUMN_DEFS = [
    { key: "cueNumber", label: "Cue Number", sortable: true, visible: true, className: "cell-tight" },
    { key: "cueName", label: "Cue Name", sortable: true, visible: true, className: "cell-wrap" },
    { key: "part", label: "Part", sortable: true, visible: true, className: "cell-tight" },
    { key: "trigger", label: "Trigger", sortable: true, visible: true, className: "cell-tight" },
    { key: "triggerTime", label: "Trigger Time", sortable: true, visible: true, className: "cell-tight" },
    { key: "fade", label: "Fade", sortable: true, visible: true, className: "cell-tight" },
    { key: "delay", label: "Delay", sortable: true, visible: true, className: "cell-tight" },
    { key: "command", label: "Command", sortable: true, visible: true, className: "cell-command" },
    { key: "presetRefs", label: "Preset References", sortable: true, visible: true, className: "cell-refs" },
    { key: "hardValuesCount", label: "Hard Values Count", sortable: true, visible: true, className: "cell-tight" },
    { key: "fixtureCount", label: "Fixture Count", sortable: true, visible: true, className: "cell-tight" },
    { key: "effectRefs", label: "Effect References", sortable: true, visible: true, className: "cell-refs" },
    { key: "warnings", label: "Warnings", sortable: true, visible: true, className: "cell-warning" },
    { key: "cueType", label: "Cue Type", sortable: true, visible: false, className: "cell-tight" },
    { key: "trackingState", label: "Tracking State", sortable: true, visible: false, className: "cell-tight" },
    { key: "block", label: "Block", sortable: true, visible: false, className: "cell-tight" },
    { key: "assert", label: "Assert", sortable: true, visible: false, className: "cell-tight" },
    { key: "mib", label: "MIB", sortable: true, visible: false, className: "cell-tight" },
    { key: "notes", label: "Notes", sortable: true, visible: false, className: "cell-wrap" },
  ];

  const refs = {
    sequenceSelect: document.getElementById("sequenceSelect"),
    searchInput: document.getElementById("searchInput"),
    triggerSelect: document.getElementById("triggerSelect"),
    onlyHard: document.getElementById("onlyHard"),
    onlyPreset: document.getElementById("onlyPreset"),
    onlyEffects: document.getElementById("onlyEffects"),
    onlyWarnings: document.getElementById("onlyWarnings"),
    onlyFade: document.getElementById("onlyFade"),
    onlyDelay: document.getElementById("onlyDelay"),
    resetFilters: document.getElementById("resetFilters"),
    tableHead: document.getElementById("tableHead"),
    tableBody: document.getElementById("tableBody"),
    loadingState: document.getElementById("loadingState"),
    emptyState: document.getElementById("emptyState"),
    statsRoot: document.getElementById("stats"),
    sequenceSummary: document.getElementById("sequenceSummary"),
    columnVisibility: document.getElementById("columnVisibility"),
    drawer: document.getElementById("detailDrawer"),
    resultMeta: document.getElementById("resultMeta"),
  };

  const presetIndex = Object.fromEntries((DATA.presets || []).map((preset) => [String(preset.number || ""), preset]));
  const fixtureIndex = Object.fromEntries((DATA.fixture_registry || DATA.patch_fixtures || []).map((fixture) => [String(fixture.fixture_id), fixture]));
  const referenceIndex = buildReferenceIndex(DATA.normalized_references || DATA.references || []);
  const sequenceRows = new Map();
  const sequences = normalizeSequences(DATA.sequences || []);
  const triggerOptions = buildTriggerOptions(sequences);

  const state = {
    sequenceNumber: initialSequenceNumber(sequences),
    sortKey: "cueNumber",
    sortDirection: "asc",
    activeCueId: "",
    selectedCueIds: new Set(),
    filters: {
      search: "",
      trigger: "all",
      onlyHard: false,
      onlyPreset: false,
      onlyEffects: false,
      onlyWarnings: false,
      onlyFade: false,
      onlyDelay: false,
    },
    visibleColumns: new Set(COLUMN_DEFS.filter((column) => column.visible).map((column) => column.key)),
  };

  function normalizeText(value) {
    return String(value || "").trim().toLowerCase();
  }

  function unique(values) {
    return [...new Set((values || []).filter(Boolean).map((value) => String(value)))];
  }

  function toNumber(value) {
    if (value === null || value === undefined || value === "") {
      return null;
    }
    const parsed = Number(String(value).replace(",", "."));
    return Number.isFinite(parsed) ? parsed : null;
  }

  function metaValue(meta, keys) {
    const safeMeta = meta || {};
    for (const key of keys) {
      if (safeMeta[key] !== undefined && safeMeta[key] !== null && safeMeta[key] !== "") {
        return safeMeta[key];
      }
    }
    return null;
  }

  function boolFromMeta(meta, keys) {
    const value = metaValue(meta, keys);
    if (value === null) {
      return false;
    }
    const normalized = String(value).trim().toLowerCase();
    return normalized === "true" || normalized === "1" || normalized === "yes";
  }

  function naturalCompare(left, right) {
    return String(left || "").localeCompare(String(right || ""), undefined, { numeric: true, sensitivity: "base" });
  }

  function compareNullableNumbers(left, right) {
    if (left === null && right === null) {
      return 0;
    }
    if (left === null) {
      return 1;
    }
    if (right === null) {
      return -1;
    }
    return left - right;
  }

  function formatNumber(value) {
    if (value === null || value === undefined || value === "") {
      return "-";
    }
    const parsed = toNumber(value);
    if (parsed === null) {
      return String(value);
    }
    return Number.isInteger(parsed) ? String(parsed) : parsed.toFixed(2).replace(/\.00$/, "");
  }

  function formatList(values, emptyLabel) {
    if (!(values || []).length) {
      return `<span class="muted">${emptyLabel}</span>`;
    }
    return values.map((value) => `<span class="tag">${escapeHtml(value)}</span>`).join("");
  }

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function buildReferenceIndex(references) {
    const index = new Map();
    for (const reference of references) {
      const key = `${reference.owner_type || ""}:${reference.owner_id || ""}`;
      if (!index.has(key)) {
        index.set(key, []);
      }
      index.get(key).push(reference);
    }
    return index;
  }

  function cueReferences(cue) {
    const key = `cue:${cue.id || ""}`;
    const references = referenceIndex.get(key) || [];
    const presetRefs = unique([
      ...(cue.values || [])
        .filter((atom) => atom.value_type === "preset_ref" && atom.reference_target)
        .map((atom) => String(atom.reference_target).replace(/^preset:/, "")),
      ...references
        .filter((reference) => reference.kind === "preset_ref" && reference.target)
        .map((reference) => String(reference.target).replace(/^preset:/, "")),
    ]).map(formatPresetReference);
    const effectRefs = unique([
      ...(cue.values || [])
        .filter((atom) => atom.value_type === "effect_ref" && atom.reference_target)
        .map((atom) => String(atom.reference_target).replace(/^effect:/, "")),
      ...references
        .filter((reference) => reference.kind === "effect_ref" && reference.target)
        .map((reference) => String(reference.target).replace(/^effect:/, "")),
    ]);
    return { presetRefs, effectRefs };
  }

  function formatPresetReference(value) {
    const preset = presetIndex[String(value)] || {};
    const presetName = String(preset.name || "").trim();
    return presetName ? `${value} ${presetName}` : String(value);
  }

  function analyzeCueWarnings(row) {
    const warnings = [];
    if (!normalizeText(row.cueName)) {
      warnings.push("missing cue name");
    }
    if (row.hardValuesCount > 0) {
      warnings.push("hard values used");
    }
    if (normalizeText(row.command)) {
      warnings.push("command present");
    }
    if (row.effectRefs.length > 0) {
      warnings.push("effects used");
    }
    if (row.fade !== null && row.fade > WARNING_THRESHOLDS.longFade) {
      warnings.push("long fade");
    }
    if (row.delay !== null && row.delay > WARNING_THRESHOLDS.longDelay) {
      warnings.push("long delay");
    }
    if (row.presetRefs.length === 0) {
      warnings.push("no preset references");
    }
    if (row.fixtureCount > WARNING_THRESHOLDS.manyFixtures) {
      warnings.push("too many fixtures changed");
    }
    return warnings;
  }

  function mapSequenceToCueRows(sequence) {
    return (sequence.cues || []).map((cue) => {
      const meta = cue.metadata || {};
      const refsForCue = cueReferences(cue);
      const hardAtoms = (cue.values || []).filter((atom) => atom.value_type === "hard");
      const fixtureIds = unique((cue.fixture_ids || []).map((fixtureId) => String(fixtureId)));
      const triggerTime = toNumber(metaValue(meta, [
        "cuepart.triggertime",
        "triggertime",
        "cue.triggertime",
        "cuepart.triggertimeinseconds",
      ]));
      const fade = toNumber(cue.fade ?? metaValue(meta, ["cuepart.basicfade", "basicfade", "fade"]));
      const delay = toNumber(cue.delay ?? metaValue(meta, ["cuepart.basicdelay", "cuepart.basicdowndelay", "basicdelay", "delay"]));
      const notes = unique([
        metaValue(meta, ["cuepart.name", "part.name"]),
        boolFromMeta(meta, ["cuepart.forceeffecttime"]) ? "force effect time" : "",
      ]);
      const row = {
        id: String(cue.id),
        cueNumber: String(cue.cue_number || ""),
        cueName: String(cue.name || ""),
        part: String(cue.part || metaValue(meta, ["cuepart.index", "part", "part.index"]) || ""),
        trigger: String(cue.trigger || metaValue(meta, ["trigger", "cue.trigger"]) || ""),
        triggerTime,
        fade,
        delay,
        command: cue.command ? String(cue.command) : "",
        presetRefs: refsForCue.presetRefs,
        effectRefs: refsForCue.effectRefs,
        hardValuesCount: hardAtoms.length,
        fixtureCount: fixtureIds.length,
        warnings: [],
        notes,
        cueType: String(metaValue(meta, ["cuetype", "cue.type"]) || ""),
        trackingState: String(metaValue(meta, ["trackingstate", "cue.trackingstate"]) || ""),
        block: boolFromMeta(meta, ["blockcue", "block", "cue.block"]),
        assert: boolFromMeta(meta, ["assertcue", "assert", "cue.assert"]),
        mib: boolFromMeta(meta, ["mibcue.number", "mib", "cue.mib"]),
        fixtureIds,
        fixtureLabels: fixtureIds.map((fixtureId) => {
          const fixture = fixtureIndex[fixtureId] || {};
          const label = fixture.label || fixture.name || `Fixture ${fixtureId}`;
          const patch = fixture.patch ? ` | ${fixture.patch}` : "";
          return `${fixtureId} ${label}${patch}`;
        }),
        changePreview: (cue.values || []).slice(0, 18).map((atom) => {
          const fixture = fixtureIndex[String(atom.fixture_id || "")] || {};
          return {
            attribute: String(atom.attribute || "?"),
            fixtureId: atom.fixture_id,
            fixtureLabel: fixture.label || fixture.name || (atom.fixture_id ? `Fixture ${atom.fixture_id}` : "Unbound fixture"),
            valueType: String(atom.value_type || "unknown"),
            rawValue: atom.raw_value,
            referenceTarget: atom.reference_target,
          };
        }),
      };
      row.warnings = analyzeCueWarnings(row);
      return row;
    });
  }

  function normalizeSequences(rawSequences) {
    return rawSequences
      .map((sequence) => ({
        id: String(sequence.id || ""),
        number: String(sequence.number || ""),
        name: String(sequence.name || ""),
        isMain: !!sequence.is_main_cue_list,
        cues: sequence.cues || [],
        sourceFile: sequence.source_file || "",
      }))
      .sort((left, right) => {
        if (left.isMain !== right.isMain) {
          return left.isMain ? -1 : 1;
        }
        return naturalCompare(left.number, right.number);
      });
  }

  function initialSequenceNumber(sequenceList) {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get("sequence");
    if (fromQuery && sequenceList.some((sequence) => sequence.number === fromQuery)) {
      return fromQuery;
    }
    const firstMain = sequenceList.find((sequence) => sequence.isMain && sequence.cues.length);
    return (firstMain || sequenceList.find((sequence) => sequence.cues.length) || sequenceList[0] || {}).number || "";
  }

  function sequenceForState() {
    return sequences.find((sequence) => sequence.number === state.sequenceNumber) || null;
  }

  function rowsForSequence(sequence) {
    if (!sequence) {
      return [];
    }
    if (!sequenceRows.has(sequence.number)) {
      sequenceRows.set(sequence.number, mapSequenceToCueRows(sequence));
    }
    return sequenceRows.get(sequence.number) || [];
  }

  function buildTriggerOptions(sequenceList) {
    const values = new Set();
    for (const sequence of sequenceList) {
      for (const cue of sequence.cues || []) {
        const trigger = String(cue.trigger || metaValue(cue.metadata || {}, ["trigger", "cue.trigger"]) || "").trim();
        if (trigger) {
          values.add(trigger);
        }
      }
    }
    return ["all", ...[...values].sort((left, right) => naturalCompare(left, right))];
  }

  function visibleRows(sequence) {
    const rows = rowsForSequence(sequence);
    const search = normalizeText(state.filters.search);
    const filtered = rows.filter((row) => {
      if (state.filters.trigger !== "all" && normalizeText(row.trigger) !== normalizeText(state.filters.trigger)) {
        return false;
      }
      if (state.filters.onlyHard && row.hardValuesCount === 0) {
        return false;
      }
      if (state.filters.onlyPreset && row.presetRefs.length === 0) {
        return false;
      }
      if (state.filters.onlyEffects && row.effectRefs.length === 0) {
        return false;
      }
      if (state.filters.onlyWarnings && row.warnings.length === 0) {
        return false;
      }
      if (state.filters.onlyFade && !(row.fade !== null && row.fade > 0)) {
        return false;
      }
      if (state.filters.onlyDelay && !(row.delay !== null && row.delay > 0)) {
        return false;
      }
      if (!search) {
        return true;
      }
      const haystack = [
        row.cueNumber,
        row.cueName,
        row.command,
        row.trigger,
        row.part,
        row.warnings.join(" "),
      ].map(normalizeText).join(" ");
      return haystack.includes(search);
    });
    const direction = state.sortDirection === "asc" ? 1 : -1;
    return filtered.sort((left, right) => {
      const key = state.sortKey;
      if (key === "cueNumber") {
        return direction * naturalCompare(left.cueNumber, right.cueNumber);
      }
      if (["triggerTime", "fade", "delay", "hardValuesCount", "fixtureCount"].includes(key)) {
        return direction * compareNullableNumbers(left[key], right[key]);
      }
      if (["presetRefs", "effectRefs", "warnings", "notes"].includes(key)) {
        return direction * naturalCompare((left[key] || []).join(" | "), (right[key] || []).join(" | "));
      }
      if (["block", "assert", "mib"].includes(key)) {
        return direction * compareNullableNumbers(left[key] ? 1 : 0, right[key] ? 1 : 0);
      }
      return direction * naturalCompare(left[key], right[key]);
    });
  }

  function updateUrl() {
    const params = new URLSearchParams(window.location.search);
    if (state.sequenceNumber) {
      params.set("sequence", state.sequenceNumber);
    }
    if (state.activeCueId) {
      params.set("cue", state.activeCueId);
    } else {
      params.delete("cue");
    }
    const nextUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, "", nextUrl);
  }

  function renderSequenceOptions() {
    refs.sequenceSelect.innerHTML = sequences.map((sequence) => {
      const prefix = sequence.isMain ? "Main" : "Seq";
      const cueCount = (sequence.cues || []).length;
      return `<option value="${escapeHtml(sequence.number)}">${prefix} ${escapeHtml(sequence.number || "-")} | ${escapeHtml(sequence.name || "Unnamed sequence")} | ${cueCount} cues</option>`;
    }).join("");
    refs.sequenceSelect.value = state.sequenceNumber;
  }

  function renderTriggerOptions() {
    refs.triggerSelect.innerHTML = triggerOptions.map((option) => {
      const label = option === "all" ? "All triggers" : option;
      return `<option value="${escapeHtml(option)}">${escapeHtml(label)}</option>`;
    }).join("");
    refs.triggerSelect.value = state.filters.trigger;
  }

  function renderColumnToggles() {
    refs.columnVisibility.innerHTML = COLUMN_DEFS.map((column) => `
      <label class="column-toggle">
        <input type="checkbox" data-column-key="${escapeHtml(column.key)}" ${state.visibleColumns.has(column.key) ? "checked" : ""}>
        <span>${escapeHtml(column.label)}</span>
      </label>
    `).join("");
  }

  function statsMarkup(sequence, rows, filteredRows) {
    const warningCount = rows.filter((row) => row.warnings.length).length;
    const hardCount = rows.filter((row) => row.hardValuesCount > 0).length;
    const effectCount = rows.filter((row) => row.effectRefs.length > 0).length;
    const selectedCount = [...state.selectedCueIds].filter((cueId) => rows.some((row) => row.id === cueId)).length;
    return [
      metricCard("Sequence", sequence ? `${sequence.number || "-"}` : "-", sequence ? sequence.name || "Unnamed sequence" : "No sequence selected"),
      metricCard("Total cues", rows.length, `Visible ${filteredRows.length}`),
      metricCard("Warnings", warningCount, `${rows.length ? Math.round((warningCount / rows.length) * 100) : 0}% of sequence`),
      metricCard("Hard values", hardCount, "Cues with local data"),
      metricCard("Effects", effectCount, "Cues using effect refs"),
      metricCard("Selected", selectedCount, `${state.visibleColumns.size} visible columns`),
    ].join("");
  }

  function metricCard(label, value, helper) {
    return `<div class="stat"><div class="muted">${escapeHtml(label)}</div><div class="stat-value">${escapeHtml(value)}</div><div class="muted">${escapeHtml(helper || "")}</div></div>`;
  }

  function renderSequenceSummary(sequence, rows) {
    if (!sequence) {
      refs.sequenceSummary.innerHTML = `<div class="sequence-meta">No sequence selected.</div>`;
      return;
    }
    const warningCount = rows.filter((row) => row.warnings.length).length;
    const hardCount = rows.filter((row) => row.hardValuesCount > 0).length;
    const effectCount = rows.filter((row) => row.effectRefs.length > 0).length;
    refs.sequenceSummary.innerHTML = `
      <div class="sequence-summary">
        <div class="sequence-meta">
          <div class="muted">Current sequence</div>
          <div style="font-size:24px; font-weight:700;">Seq ${escapeHtml(sequence.number || "-")}</div>
          <div>${escapeHtml(sequence.name || "Unnamed sequence")}</div>
          <div class="muted">${escapeHtml(sequence.sourceFile || "No source file metadata")}</div>
        </div>
        <div class="summary-badges">
          <span class="badge badge-accent">cues ${rows.length}</span>
          <span class="badge ${warningCount ? "badge-danger" : "badge-success"}">warnings ${warningCount}</span>
          <span class="badge ${hardCount ? "badge-warn" : "badge-success"}">hard ${hardCount}</span>
          <span class="badge ${effectCount ? "badge-warn" : "badge-success"}">effects ${effectCount}</span>
        </div>
      </div>
    `;
  }

  function sortIndicator(columnKey) {
    if (state.sortKey !== columnKey) {
      return "";
    }
    return state.sortDirection === "asc" ? " ▲" : " ▼";
  }

  function renderHeader() {
    const visibleColumns = COLUMN_DEFS.filter((column) => state.visibleColumns.has(column.key));
    refs.tableHead.innerHTML = `
      <tr>
        <th class="selection-chip">Sel</th>
        ${visibleColumns.map((column) => `
          <th class="${column.sortable ? "sortable" : ""}" data-sort-key="${escapeHtml(column.key)}">
            ${escapeHtml(column.label)}${sortIndicator(column.key)}
          </th>
        `).join("")}
      </tr>
    `;
  }

  function cellContent(row, columnKey) {
    switch (columnKey) {
      case "cueNumber":
        return `<div class="cue-number">${escapeHtml(row.cueNumber || "-")}</div><div class="cue-subline">${escapeHtml(row.id)}</div>`;
      case "cueName":
        return `<div class="cue-name">${escapeHtml(row.cueName || "Unnamed cue")}</div><div class="cue-subline">${escapeHtml(row.cueType || row.notes[0] || "No cue note")}</div>`;
      case "presetRefs":
        return formatList(row.presetRefs, "No presets");
      case "effectRefs":
        return formatList(row.effectRefs, "No effects");
      case "warnings":
        return row.warnings.length
          ? row.warnings.map((warning) => `<span class="warning-pill ${warning === "missing cue name" || warning === "too many fixtures changed" ? "is-critical" : ""}">${escapeHtml(warning)}</span>`).join("")
          : `<span class="badge badge-success">clean</span>`;
      case "notes":
        return row.notes.length ? row.notes.map((note) => `<span class="tag">${escapeHtml(note)}</span>`).join("") : `<span class="muted">No notes</span>`;
      case "triggerTime":
      case "fade":
      case "delay":
        return escapeHtml(formatNumber(row[columnKey]));
      case "block":
      case "assert":
      case "mib":
        return row[columnKey] ? `<span class="badge badge-accent">yes</span>` : `<span class="muted">-</span>`;
      case "command":
        return row.command ? escapeHtml(row.command) : `<span class="muted">-</span>`;
      default:
        return escapeHtml(row[columnKey] || "-");
    }
  }

  function renderRows(filteredRows) {
    const visibleColumns = COLUMN_DEFS.filter((column) => state.visibleColumns.has(column.key));
    if (!filteredRows.length) {
      refs.tableBody.innerHTML = "";
      refs.emptyState.hidden = false;
      refs.resultMeta.textContent = "No results for the current filter set.";
      return;
    }
    refs.emptyState.hidden = true;
    refs.resultMeta.textContent = `${filteredRows.length} visible cues`;
    refs.tableBody.innerHTML = filteredRows.map((row) => `
      <tr class="${row.warnings.length ? "has-warnings" : ""} ${state.activeCueId === row.id ? "is-active" : ""}" data-row-id="${escapeHtml(row.id)}">
        <td class="selection-chip">
          <input type="checkbox" data-select-id="${escapeHtml(row.id)}" ${state.selectedCueIds.has(row.id) ? "checked" : ""}>
        </td>
        ${visibleColumns.map((column) => `<td class="${escapeHtml(column.className || "")}">${cellContent(row, column.key)}</td>`).join("")}
      </tr>
    `).join("");
  }

  function detailBox(label, value) {
    return `
      <div class="detail-box">
        <div class="detail-label">${escapeHtml(label)}</div>
        <div class="detail-value">${escapeHtml(value)}</div>
      </div>
    `;
  }

  function renderDrawer(sequence, rows) {
    const activeRow = rows.find((row) => row.id === state.activeCueId) || rows[0] || null;
    if (!activeRow) {
      refs.drawer.innerHTML = `<div class="drawer-empty">Select a cue row to inspect its detail, warnings and fixture changes.</div>`;
      return;
    }
    if (state.activeCueId !== activeRow.id) {
      state.activeCueId = activeRow.id;
      updateUrl();
    }
    const warningsMarkup = activeRow.warnings.length
      ? activeRow.warnings.map((warning) => `<span class="warning-pill ${warning === "missing cue name" || warning === "too many fixtures changed" ? "is-critical" : ""}">${escapeHtml(warning)}</span>`).join("")
      : `<span class="badge badge-success">No warnings</span>`;
    const changeMarkup = activeRow.changePreview.length
      ? activeRow.changePreview.map((change) => `
          <div class="change-row">
            <strong>${escapeHtml(change.attribute)} | ${escapeHtml(change.fixtureLabel)}</strong>
            <div class="muted">Fixture ${escapeHtml(change.fixtureId || "-")} | ${escapeHtml(change.valueType)}</div>
            <div>${escapeHtml(change.referenceTarget || change.rawValue || "-")}</div>
          </div>
        `).join("")
      : `<div class="muted">No attribute preview available.</div>`;

    refs.drawer.innerHTML = `
      <div class="panel-inner stack">
        <div>
          <div class="muted">Cue detail</div>
          <div style="font-size:24px; font-weight:700; margin-top:6px;">Cue ${escapeHtml(activeRow.cueNumber || "-")}</div>
          <div style="margin-top:6px;">${escapeHtml(activeRow.cueName || "Unnamed cue")}</div>
          <div class="muted">Sequence ${escapeHtml((sequence && sequence.number) || "-")} | ${escapeHtml((sequence && sequence.name) || "Unnamed sequence")}</div>
        </div>
        <div class="detail-grid">
          ${detailBox("Trigger", activeRow.trigger || "-")}
          ${detailBox("Trigger Time", formatNumber(activeRow.triggerTime))}
          ${detailBox("Fade", formatNumber(activeRow.fade))}
          ${detailBox("Delay", formatNumber(activeRow.delay))}
          ${detailBox("Part", activeRow.part || "-")}
          ${detailBox("Fixtures", activeRow.fixtureCount)}
          ${detailBox("Hard Values", activeRow.hardValuesCount)}
          ${detailBox("Command", activeRow.command || "-")}
        </div>
        <div class="drawer-section">
          <div class="detail-label">Preset References</div>
          <div class="tag-list">${formatList(activeRow.presetRefs, "No preset refs")}</div>
        </div>
        <div class="drawer-section">
          <div class="detail-label">Effect References</div>
          <div class="tag-list">${formatList(activeRow.effectRefs, "No effect refs")}</div>
        </div>
        <div class="drawer-section">
          <div class="detail-label">Warnings</div>
          <div class="warning-list">${warningsMarkup}</div>
        </div>
        <div class="drawer-section">
          <div class="detail-label">Notes</div>
          <div class="tag-list">${formatList(activeRow.notes, "No notes")}</div>
        </div>
        <div class="drawer-section">
          <div class="detail-label">Fixture Changes / Attributes</div>
          <div class="change-list">${changeMarkup}</div>
        </div>
        <div class="drawer-section">
          <div class="detail-label">Fixture Scope</div>
          <div class="tag-list">${formatList(activeRow.fixtureLabels, "No fixture list")}</div>
        </div>
      </div>
    `;
  }

  function applyDomState() {
    refs.searchInput.value = state.filters.search;
    refs.triggerSelect.value = state.filters.trigger;
    refs.onlyHard.checked = state.filters.onlyHard;
    refs.onlyPreset.checked = state.filters.onlyPreset;
    refs.onlyEffects.checked = state.filters.onlyEffects;
    refs.onlyWarnings.checked = state.filters.onlyWarnings;
    refs.onlyFade.checked = state.filters.onlyFade;
    refs.onlyDelay.checked = state.filters.onlyDelay;
  }

  function render() {
    refs.loadingState.hidden = true;
    const sequence = sequenceForState();
    const rows = rowsForSequence(sequence);
    const filteredRows = visibleRows(sequence);
    refs.statsRoot.innerHTML = statsMarkup(sequence, rows, filteredRows);
    renderSequenceSummary(sequence, rows);
    renderHeader();
    renderRows(filteredRows);
    renderDrawer(sequence, filteredRows);
    applyDomState();
  }

  function handleSort(sortKey) {
    if (state.sortKey === sortKey) {
      state.sortDirection = state.sortDirection === "asc" ? "desc" : "asc";
    } else {
      state.sortKey = sortKey;
      state.sortDirection = sortKey === "cueNumber" ? "asc" : "desc";
    }
    render();
  }

  function bindEvents() {
    refs.sequenceSelect.addEventListener("change", function (event) {
      state.sequenceNumber = event.target.value;
      state.activeCueId = "";
      state.selectedCueIds.clear();
      updateUrl();
      render();
    });
    refs.searchInput.addEventListener("input", function (event) {
      state.filters.search = event.target.value;
      render();
    });
    refs.triggerSelect.addEventListener("change", function (event) {
      state.filters.trigger = event.target.value;
      render();
    });
    [
      ["onlyHard", "onlyHard"],
      ["onlyPreset", "onlyPreset"],
      ["onlyEffects", "onlyEffects"],
      ["onlyWarnings", "onlyWarnings"],
      ["onlyFade", "onlyFade"],
      ["onlyDelay", "onlyDelay"],
    ].forEach(function (pair) {
      refs[pair[0]].addEventListener("change", function (event) {
        state.filters[pair[1]] = !!event.target.checked;
        render();
      });
    });
    refs.resetFilters.addEventListener("click", function () {
      state.filters = {
        search: "",
        trigger: "all",
        onlyHard: false,
        onlyPreset: false,
        onlyEffects: false,
        onlyWarnings: false,
        onlyFade: false,
        onlyDelay: false,
      };
      render();
    });
    refs.columnVisibility.addEventListener("change", function (event) {
      const target = event.target;
      if (!(target instanceof HTMLInputElement)) {
        return;
      }
      const key = target.getAttribute("data-column-key");
      if (!key) {
        return;
      }
      if (target.checked) {
        state.visibleColumns.add(key);
      } else if (state.visibleColumns.size > 1) {
        state.visibleColumns.delete(key);
      } else {
        target.checked = true;
      }
      render();
    });
    refs.tableHead.addEventListener("click", function (event) {
      const header = event.target.closest("[data-sort-key]");
      if (!header) {
        return;
      }
      handleSort(header.getAttribute("data-sort-key"));
    });
    refs.tableBody.addEventListener("click", function (event) {
      const target = event.target;
      if (target instanceof HTMLInputElement && target.hasAttribute("data-select-id")) {
        const cueId = target.getAttribute("data-select-id");
        if (!cueId) {
          return;
        }
        if (target.checked) {
          state.selectedCueIds.add(cueId);
        } else {
          state.selectedCueIds.delete(cueId);
        }
        render();
        return;
      }
      const row = event.target.closest("[data-row-id]");
      if (!row) {
        return;
      }
      state.activeCueId = row.getAttribute("data-row-id") || "";
      updateUrl();
      render();
    });
  }

  function initializeActiveCue() {
    const params = new URLSearchParams(window.location.search);
    const requestedCue = params.get("cue");
    const sequence = sequenceForState();
    const rows = rowsForSequence(sequence);
    state.activeCueId = rows.some((row) => row.id === requestedCue) ? requestedCue : (rows[0] ? rows[0].id : "");
  }

  function bootstrap() {
    renderSequenceOptions();
    renderTriggerOptions();
    renderColumnToggles();
    initializeActiveCue();
    bindEvents();
    render();
  }

  bootstrap();
})();
