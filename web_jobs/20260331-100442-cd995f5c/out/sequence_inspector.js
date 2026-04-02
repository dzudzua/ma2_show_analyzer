import {
  COLUMN_DEFS,
  DEFAULT_VISIBLE_COLUMNS,
  buildTriggerOptions,
  createSequenceViewModel,
  escapeHtml,
  filterCueRows,
  formatNumber,
  mapSequenceToCueRows,
  sortCueRows,
  summarizeSequenceRows,
} from "./sequence_inspector_utils.js";

(function () {
  "use strict";

  const STORAGE_KEY = "graindma.sequenceInspector.columns";
  const dataNode = document.getElementById("sequenceInspectorData");
  const rawData = dataNode ? JSON.parse(dataNode.textContent || "{}") : {};
  const model = createSequenceViewModel(rawData);

  const refs = {
    appShell: document.getElementById("appShell"),
    loadingState: document.getElementById("loadingState"),
    sequenceSelect: document.getElementById("sequenceSelect"),
    sequenceHeadline: document.getElementById("sequenceHeadline"),
    sequenceMeta: document.getElementById("sequenceMeta"),
    triggerSelect: document.getElementById("triggerSelect"),
    searchInput: document.getElementById("searchInput"),
    onlyHard: document.getElementById("onlyHard"),
    onlyPreset: document.getElementById("onlyPreset"),
    onlyEffects: document.getElementById("onlyEffects"),
    onlyWarnings: document.getElementById("onlyWarnings"),
    onlyFade: document.getElementById("onlyFade"),
    onlyDelay: document.getElementById("onlyDelay"),
    resetFilters: document.getElementById("resetFilters"),
    columnVisibility: document.getElementById("columnVisibility"),
    stats: document.getElementById("stats"),
    tableHead: document.getElementById("tableHead"),
    tableBody: document.getElementById("tableBody"),
    resultMeta: document.getElementById("resultMeta"),
    activeFilterSummary: document.getElementById("activeFilterSummary"),
    emptySequenceState: document.getElementById("emptySequenceState"),
    noResultsState: document.getElementById("noResultsState"),
    detailTitle: document.getElementById("detailTitle"),
    detailBadges: document.getElementById("detailBadges"),
    detailContent: document.getElementById("detailContent"),
    cueNavigator: document.getElementById("cueNavigator"),
    printBtn: document.getElementById("printBtn"),
  };

  const sequenceRowCache = new Map();
  const initialParams = new URLSearchParams(window.location.search);
  const persistedColumns = loadStoredColumns();

  const state = {
    sequenceNumber: resolveInitialSequence(initialParams.get("sequence")),
    activeCueId: initialParams.get("cue") || "",
    sort: {
      key: initialParams.get("sort") || "cueNumber",
      direction: initialParams.get("dir") === "desc" ? "desc" : "asc",
    },
    filters: {
      search: initialParams.get("q") || "",
      trigger: initialParams.get("trigger") || "all",
      onlyHard: initialParams.get("hard") === "1",
      onlyPreset: initialParams.get("preset") === "1",
      onlyEffects: initialParams.get("effects") === "1",
      onlyWarnings: initialParams.get("warnings") === "1",
      onlyFade: initialParams.get("fade") === "1",
      onlyDelay: initialParams.get("delay") === "1",
    },
    visibleColumns: new Set(persistedColumns.length ? persistedColumns : DEFAULT_VISIBLE_COLUMNS),
  };

  function loadStoredColumns() {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return [];
      }
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) {
        return [];
      }
      return parsed.filter((key) => COLUMN_DEFS.some((column) => column.key === key));
    } catch (_error) {
      return [];
    }
  }

  function storeVisibleColumns() {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify([...state.visibleColumns]));
    } catch (_error) {
      return;
    }
  }

  function resolveInitialSequence(requested) {
    if (requested && model.sequences.some((sequence) => sequence.number === requested)) {
      return requested;
    }
    const firstMain = model.sequences.find((sequence) => sequence.isMain && sequence.cues.length > 0);
    const fallback = firstMain || model.sequences.find((sequence) => sequence.cues.length > 0) || model.sequences[0];
    return fallback ? fallback.number : "";
  }

  function currentSequence() {
    return model.sequences.find((sequence) => sequence.number === state.sequenceNumber) || null;
  }

  function rowsForSequence(sequence) {
    if (!sequence) {
      return [];
    }
    if (!sequenceRowCache.has(sequence.number)) {
      sequenceRowCache.set(sequence.number, mapSequenceToCueRows(sequence, model));
    }
    return sequenceRowCache.get(sequence.number) || [];
  }

  function currentVisibleRows() {
    const sequence = currentSequence();
    const rows = rowsForSequence(sequence);
    return sortCueRows(filterCueRows(rows, state.filters), state.sort);
  }

  function syncUrl() {
    const params = new URLSearchParams();
    if (state.sequenceNumber) {
      params.set("sequence", state.sequenceNumber);
    }
    if (state.activeCueId) {
      params.set("cue", state.activeCueId);
    }
    if (state.sort.key !== "cueNumber") {
      params.set("sort", state.sort.key);
    }
    if (state.sort.direction !== "asc") {
      params.set("dir", state.sort.direction);
    }
    if (state.filters.search) {
      params.set("q", state.filters.search);
    }
    if (state.filters.trigger !== "all") {
      params.set("trigger", state.filters.trigger);
    }
    if (state.filters.onlyHard) {
      params.set("hard", "1");
    }
    if (state.filters.onlyPreset) {
      params.set("preset", "1");
    }
    if (state.filters.onlyEffects) {
      params.set("effects", "1");
    }
    if (state.filters.onlyWarnings) {
      params.set("warnings", "1");
    }
    if (state.filters.onlyFade) {
      params.set("fade", "1");
    }
    if (state.filters.onlyDelay) {
      params.set("delay", "1");
    }
    const query = params.toString();
    const nextUrl = query ? `${window.location.pathname}?${query}` : window.location.pathname;
    window.history.replaceState({}, "", nextUrl);
  }

  function ensureActiveCue(rows) {
    if (rows.some((row) => row.id === state.activeCueId)) {
      return;
    }
    state.activeCueId = rows[0] ? rows[0].id : "";
  }

  function activeCue(rows) {
    return rows.find((row) => row.id === state.activeCueId) || null;
  }

  function visibleColumnDefs() {
    return COLUMN_DEFS.filter((column) => state.visibleColumns.has(column.key));
  }

  function sortIndicator(column) {
    if (state.sort.key !== column.key) {
      return "";
    }
    return state.sort.direction === "asc" ? " ^" : " v";
  }

  function metricCard(label, value, helper, tone) {
    const badgeTone = tone ? ` metric-badge ${tone}` : " metric-badge";
    return `
      <div class="metric-card">
        <div class="muted">${escapeHtml(label)}</div>
        <div class="metric-value">${escapeHtml(value)}</div>
        <div class="metric-sub">${escapeHtml(helper || "")}</div>
        <div class="${badgeTone.trim()}">${escapeHtml(label)}</div>
      </div>
    `;
  }

  function renderSequenceMeta(sequence, rows, filteredRows) {
    const summary = summarizeSequenceRows(rows);
    refs.sequenceHeadline.textContent = sequence ? `Sequence ${sequence.number || "-"}` : "No sequence";
    refs.sequenceMeta.innerHTML = sequence ? `
      <div class="navigator-card">
        <div><strong>${escapeHtml(sequence.name || "Unnamed sequence")}</strong></div>
        <div class="muted">${escapeHtml(sequence.sourceFile || "No source file metadata")}</div>
      </div>
      <div class="metric-grid-inline">
        ${metricCard("Total", summary.total, `${filteredRows.length} visible`, "")}
        ${metricCard("Warnings", summary.warnings, "Analytical flags", "")}
      </div>
    ` : `<div class="muted">No sequence available.</div>`;
  }

  function renderStats(rows, filteredRows) {
    const summary = summarizeSequenceRows(rows);
    refs.stats.innerHTML = [
      metricCard("Total cues", summary.total, `${filteredRows.length} after filters`, ""),
      metricCard("Warnings", summary.warnings, "Rows with warnings", ""),
      metricCard("Dimmer hard", summary.dimmer, "Cues using D values", ""),
      metricCard("Hard values", summary.hard, "Cues using hard values", ""),
      metricCard("Effects", summary.effects, "Cues using effect refs", ""),
      metricCard("Preset refs", summary.presets, "Cues using presets", ""),
      metricCard("Columns", state.visibleColumns.size, "Visible table columns", ""),
    ].join("");
  }

  function renderSequenceSelect() {
    refs.sequenceSelect.innerHTML = model.sequences.map((sequence) => {
      const prefix = sequence.isMain ? "Main" : "Seq";
      return `<option value="${escapeHtml(sequence.number)}">${escapeHtml(prefix)} ${escapeHtml(sequence.number || "-")} | ${escapeHtml(sequence.name || "Unnamed sequence")} | ${sequence.cues.length} cues</option>`;
    }).join("");
    refs.sequenceSelect.value = state.sequenceNumber;
  }

  function renderTriggerSelect(rows) {
    const options = buildTriggerOptions(rows);
    if (!options.includes(state.filters.trigger)) {
      state.filters.trigger = "all";
    }
    refs.triggerSelect.innerHTML = options.map((option) => {
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

  function renderFilterSummary() {
    const tags = [];
    if (state.filters.search) {
      tags.push(`search: ${state.filters.search}`);
    }
    if (state.filters.trigger !== "all") {
      tags.push(`trigger: ${state.filters.trigger}`);
    }
    if (state.filters.onlyHard) {
      tags.push("hard");
    }
    if (state.filters.onlyPreset) {
      tags.push("presets");
    }
    if (state.filters.onlyEffects) {
      tags.push("effects");
    }
    if (state.filters.onlyWarnings) {
      tags.push("warnings");
    }
    if (state.filters.onlyFade) {
      tags.push("fade > 0");
    }
    if (state.filters.onlyDelay) {
      tags.push("delay > 0");
    }
    refs.activeFilterSummary.innerHTML = tags.length
      ? tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")
      : `<span class="muted">No active filters</span>`;
  }

  function renderHeader() {
    refs.tableHead.innerHTML = `
      <tr>
        ${visibleColumnDefs().map((column) => {
          const stickyClass = column.sticky ? ` is-sticky sticky-${column.sticky}` : "";
          return `<th class="${stickyClass.trim()}" data-sort-key="${escapeHtml(column.key)}">${escapeHtml(column.label)}${escapeHtml(sortIndicator(column))}</th>`;
        }).join("")}
      </tr>
    `;
  }

  function renderList(values, emptyLabel, className) {
    if (!(values || []).length) {
      return `<span class="muted">${escapeHtml(emptyLabel)}</span>`;
    }
    return values.map((value) => `<span class="${className || "tag"}">${escapeHtml(value)}</span>`).join("");
  }

  function renderWarnings(row) {
    if (!row.warnings.length) {
      return `<span class="tag">clean</span>`;
    }
    return row.warnings.map((warning) => {
      const critical = (warning.includes("no name") || warning.includes("many fixtures")) && !warning.includes("dimmer hard");
      return `<span class="warning-pill${critical ? " critical" : ""}">${escapeHtml(warning)}</span>`;
    }).join("");
  }

  function cellMarkup(row, column) {
    if (column.key === "cueNumber") {
      return `<div class="cue-number">${escapeHtml(row.cueNumber || "-")}</div><div class="subline">${escapeHtml(row.id || "")}</div>`;
    }
    if (column.key === "cueName") {
      return `<div class="cue-name">${escapeHtml(row.cueName || "Unnamed cue")}</div><div class="subline">${escapeHtml(row.cueType || row.trackingState || "sequence row")}</div>`;
    }
    if (column.key === "triggerTime" || column.key === "fade" || column.key === "delay") {
      return escapeHtml(formatNumber(row[column.key]));
    }
    if (column.key === "presetRefs") {
      return renderList(row.presetRefs, "No presets", "tag");
    }
    if (column.key === "dimmerValuesCount") {
      return row.dimmerValuesCount ? `<span class="value-pill dimmer">D ${escapeHtml(row.dimmerValuesCount)}</span>` : `<span class="muted">-</span>`;
    }
    if (column.key === "effectRefs") {
      return renderList(row.effectRefs, "No effects", "value-pill effect");
    }
    if (column.key === "warnings") {
      return renderWarnings(row);
    }
    if (column.key === "command") {
      return row.command ? escapeHtml(row.command) : `<span class="muted">-</span>`;
    }
    if (column.key === "notes") {
      return renderList(row.notes, "No notes", "value-pill note");
    }
    if (column.key === "block" || column.key === "assert" || column.key === "mib") {
      return row[column.key] ? `<span class="tag">yes</span>` : `<span class="muted">-</span>`;
    }
    return escapeHtml(row[column.key] || "-");
  }

  function renderRows(rows) {
    refs.tableBody.innerHTML = rows.map((row) => `
      <tr data-row-id="${escapeHtml(row.id)}" class="${row.id === state.activeCueId ? "is-selected " : ""}${row.warnings.length ? "has-warning" : ""}">
        ${visibleColumnDefs().map((column) => {
          const stickyClass = column.sticky ? ` is-sticky sticky-${column.sticky}` : "";
          const classes = [column.className || "", stickyClass].join(" ").trim();
          return `<td class="${classes}">${cellMarkup(row, column)}</td>`;
        }).join("")}
      </tr>
    `).join("");
  }

  function detailBox(label, value) {
    return `
      <div class="detail-box">
        <div class="detail-box-label">${escapeHtml(label)}</div>
        <div class="detail-box-value">${value}</div>
      </div>
    `;
  }

  function renderDetail(sequence, row) {
    if (!row) {
      refs.detailTitle.textContent = "No cue selected";
      refs.detailBadges.innerHTML = "";
      refs.detailContent.innerHTML = `<div class="empty-detail">Vyber cue row v tabulce pro zobrazeni detailu.</div>`;
      return;
    }

    refs.detailTitle.textContent = `Cue ${row.cueNumber || "-"} ${row.cueName || ""}`.trim();
    refs.detailBadges.innerHTML = [
      `<span class="tag">Seq ${escapeHtml(sequence ? sequence.number || "-" : "-")}</span>`,
      row.dimmerValuesCount ? `<span class="value-pill dimmer">D ${row.dimmerValuesCount}</span>` : "",
      row.hardValuesCount ? `<span class="value-pill hard">Hard ${row.hardValuesCount}</span>` : "",
      row.effectRefs.length ? `<span class="value-pill effect">Effects ${row.effectRefs.length}</span>` : "",
      row.warnings.length ? `<span class="warning-pill">${row.warnings.length} warnings</span>` : `<span class="tag">clean</span>`,
    ].filter(Boolean).join("");

    const changeMarkup = row.changeGroups.length
      ? row.changeGroups.map((group) => `
          <div class="change-card">
            <div class="change-header">
              <div>
                <strong>${escapeHtml(group.fixtureLabel || "Unbound values")}</strong>
                <div class="muted">${escapeHtml([group.fixtureId ? `Fixture ${group.fixtureId}` : "", group.fixtureType, group.patch].filter(Boolean).join(" | ") || "-")}</div>
              </div>
              <span class="tag">${group.lines.length} changes</span>
            </div>
            <div class="change-lines">
              ${group.lines.map((line) => `<div class="change-line"><strong>${escapeHtml(line.attribute)}</strong> | ${escapeHtml(line.valueType)} | ${escapeHtml(line.displayValue)}</div>`).join("")}
            </div>
          </div>
        `).join("")
      : `<div class="muted">No fixture change preview available.</div>`;

    refs.detailContent.innerHTML = `
      <div class="detail-grid">
        ${detailBox("Cue Number", escapeHtml(row.cueNumber || "-"))}
        ${detailBox("Cue Name", escapeHtml(row.cueName || "Unnamed cue"))}
        ${detailBox("Trigger", escapeHtml(row.trigger || "-"))}
        ${detailBox("Trigger Time", escapeHtml(formatNumber(row.triggerTime)))}
        ${detailBox("Fade", escapeHtml(formatNumber(row.fade)))}
        ${detailBox("Delay", escapeHtml(formatNumber(row.delay)))}
        ${detailBox("Command", row.command ? escapeHtml(row.command) : "-")}
        ${detailBox("Fixture Count", escapeHtml(row.fixtureCount))}
        ${detailBox("Dimmer Hard Count", escapeHtml(row.dimmerValuesCount))}
        ${detailBox("Hard Values Count", escapeHtml(row.hardValuesCount))}
        ${detailBox("Cue Type", escapeHtml(row.cueType || "-"))}
        ${detailBox("Tracking State", escapeHtml(row.trackingState || "-"))}
        ${detailBox("Flags", escapeHtml([row.block ? "Block" : "", row.assert ? "Assert" : "", row.mib ? "MIB" : ""].filter(Boolean).join(", ") || "-"))}
      </div>
      <div>
        <div class="detail-section-title">Preset References</div>
        <div class="detail-tag-list">${renderList(row.presetRefs, "No preset references", "tag")}</div>
      </div>
      <div>
        <div class="detail-section-title">Effect References</div>
        <div class="detail-tag-list">${renderList(row.effectRefs, "No effect references", "value-pill effect")}</div>
      </div>
      <div>
        <div class="detail-section-title">Warnings</div>
        <div class="warning-list">${renderWarnings(row)}</div>
      </div>
      <div>
        <div class="detail-section-title">Notes</div>
        <div class="detail-tag-list">${renderList(row.notes, "No notes", "value-pill note")}</div>
      </div>
      <div>
        <div class="detail-section-title">Fixture Scope</div>
        <div class="detail-tag-list">${renderList(row.fixtureLabels, "No fixture list", "tag")}</div>
      </div>
      <div>
        <div class="detail-section-title">Fixture Changes / Attributes</div>
        <div class="change-list">${changeMarkup}</div>
      </div>
    `;
  }

  function renderNavigator(rows) {
    const currentIndex = rows.findIndex((row) => row.id === state.activeCueId);
    const activeRow = currentIndex >= 0 ? rows[currentIndex] : null;
    refs.cueNavigator.innerHTML = `
      <div class="navigator-card">
        <div class="navigator-caption">Selected row</div>
        <div><strong>${escapeHtml(activeRow ? `${activeRow.cueNumber} ${activeRow.cueName || ""}`.trim() : "No cue")}</strong></div>
        <div class="muted">${activeRow ? `Row ${currentIndex + 1} of ${rows.length}` : "No visible rows"}</div>
      </div>
      <div class="cue-nav-buttons">
        <button type="button" id="prevCueBtn" ${currentIndex <= 0 ? "disabled" : ""}>Previous Cue</button>
        <button type="button" id="nextCueBtn" ${currentIndex === -1 || currentIndex >= rows.length - 1 ? "disabled" : ""}>Next Cue</button>
      </div>
    `;

    const prevButton = document.getElementById("prevCueBtn");
    const nextButton = document.getElementById("nextCueBtn");
    if (prevButton) {
      prevButton.addEventListener("click", function () {
        if (currentIndex > 0) {
          state.activeCueId = rows[currentIndex - 1].id;
          syncUrl();
          render();
        }
      });
    }
    if (nextButton) {
      nextButton.addEventListener("click", function () {
        if (currentIndex >= 0 && currentIndex < rows.length - 1) {
          state.activeCueId = rows[currentIndex + 1].id;
          syncUrl();
          render();
        }
      });
    }
  }

  function applyInputState() {
    refs.searchInput.value = state.filters.search;
    refs.onlyHard.checked = state.filters.onlyHard;
    refs.onlyPreset.checked = state.filters.onlyPreset;
    refs.onlyEffects.checked = state.filters.onlyEffects;
    refs.onlyWarnings.checked = state.filters.onlyWarnings;
    refs.onlyFade.checked = state.filters.onlyFade;
    refs.onlyDelay.checked = state.filters.onlyDelay;
  }

  function render() {
    const sequence = currentSequence();
    const rows = rowsForSequence(sequence);
    const rawFilteredRows = filterCueRows(rows, state.filters);
    renderSequenceSelect();
    renderTriggerSelect(rows);
    renderColumnToggles();
    renderFilterSummary();
    renderSequenceMeta(sequence, rows, rawFilteredRows);
    renderStats(rows, rawFilteredRows);

    const filteredRows = currentVisibleRows();
    ensureActiveCue(filteredRows);
    syncUrl();
    renderHeader();
    renderRows(filteredRows);
    renderNavigator(filteredRows);
    renderDetail(sequence, activeCue(filteredRows));

    refs.emptySequenceState.hidden = rows.length !== 0;
    refs.noResultsState.hidden = !(rows.length > 0 && filteredRows.length === 0);
    refs.resultMeta.textContent = `${filteredRows.length} visible cues | default sort by cue number | URL params sync active sequence and cue`;
    applyInputState();
  }

  function setSort(key) {
    if (state.sort.key === key) {
      state.sort.direction = state.sort.direction === "asc" ? "desc" : "asc";
    } else {
      state.sort.key = key;
      state.sort.direction = key === "cueNumber" ? "asc" : "desc";
    }
    render();
  }

  function bindEvents() {
    refs.sequenceSelect.addEventListener("change", function (event) {
      state.sequenceNumber = event.target.value;
      state.activeCueId = "";
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
    ].forEach(function ([refName, stateKey]) {
      refs[refName].addEventListener("change", function (event) {
        state.filters[stateKey] = !!event.target.checked;
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
      storeVisibleColumns();
      render();
    });

    refs.tableHead.addEventListener("click", function (event) {
      const header = event.target.closest("[data-sort-key]");
      if (!header) {
        return;
      }
      setSort(header.getAttribute("data-sort-key"));
    });

    refs.tableBody.addEventListener("click", function (event) {
      const row = event.target.closest("[data-row-id]");
      if (!row) {
        return;
      }
      state.activeCueId = row.getAttribute("data-row-id") || "";
      syncUrl();
      render();
    });

    refs.printBtn.addEventListener("click", function () {
      window.print();
    });

    window.addEventListener("keydown", function (event) {
      const tag = String(event.target && event.target.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select" || (event.target && event.target.isContentEditable)) {
        return;
      }
      const rows = currentVisibleRows();
      const currentIndex = rows.findIndex((row) => row.id === state.activeCueId);
      if (event.key === "ArrowDown" && currentIndex < rows.length - 1) {
        event.preventDefault();
        state.activeCueId = rows[currentIndex + 1].id;
        syncUrl();
        render();
      } else if (event.key === "ArrowUp" && currentIndex > 0) {
        event.preventDefault();
        state.activeCueId = rows[currentIndex - 1].id;
        syncUrl();
        render();
      }
    });
  }

  function bootstrap() {
    refs.loadingState.hidden = true;
    refs.appShell.hidden = false;
    bindEvents();
    render();
  }

  bootstrap();
})();
