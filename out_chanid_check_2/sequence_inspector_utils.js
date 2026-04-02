const WARNING_THRESHOLDS = Object.freeze({
  longFade: 8,
  longDelay: 3,
  manyFixtures: 12,
  manyHardValues: 18,
});

const DEFAULT_VISIBLE_COLUMNS = [
  "cueNumber",
  "cueName",
  "part",
  "trigger",
  "triggerTime",
  "fade",
  "delay",
  "command",
  "presetRefs",
  "hardValuesCount",
  "fixtureCount",
  "effectRefs",
  "warnings",
];

const COLUMN_DEFS = [
  { key: "cueNumber", label: "Cue Number", className: "cell-tight", sticky: 1 },
  { key: "cueName", label: "Cue Name", className: "cell-name", sticky: 2 },
  { key: "part", label: "Part", className: "cell-tight" },
  { key: "trigger", label: "Trigger", className: "cell-tight" },
  { key: "triggerTime", label: "Trigger Time", className: "cell-tight" },
  { key: "fade", label: "Fade", className: "cell-tight" },
  { key: "delay", label: "Delay", className: "cell-tight" },
  { key: "command", label: "Command", className: "cell-command" },
  { key: "presetRefs", label: "Preset References" },
  { key: "hardValuesCount", label: "Hard Values Count", className: "cell-tight" },
  { key: "fixtureCount", label: "Fixture Count", className: "cell-tight" },
  { key: "effectRefs", label: "Effect References" },
  { key: "warnings", label: "Warnings", className: "cell-warning" },
  { key: "cueType", label: "Cue Type", className: "cell-tight" },
  { key: "trackingState", label: "Tracking State", className: "cell-tight" },
  { key: "block", label: "Block", className: "cell-tight" },
  { key: "assert", label: "Assert", className: "cell-tight" },
  { key: "mib", label: "MIB", className: "cell-tight" },
  { key: "notes", label: "Notes", className: "cell-warning" },
];

function normalizeText(value) {
  return String(value || "").trim().toLowerCase();
}

function uniqueStrings(values) {
  return [...new Set((values || []).filter((value) => value !== null && value !== undefined && String(value).trim() !== "").map((value) => String(value)))];
}

function toNumber(value) {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  const parsed = Number(String(value).replace(",", "."));
  return Number.isFinite(parsed) ? parsed : null;
}

function naturalCompare(left, right) {
  return String(left || "").localeCompare(String(right || ""), undefined, {
    numeric: true,
    sensitivity: "base",
  });
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
  const numericValue = toNumber(value);
  if (numericValue === null) {
    return "-";
  }
  return Number.isInteger(numericValue) ? String(numericValue) : numericValue.toFixed(2).replace(/\.00$/, "");
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
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

function createReferenceIndex(references) {
  const index = new Map();
  for (const reference of references || []) {
    const key = `${reference.owner_type || ""}:${reference.owner_id || ""}`;
    if (!index.has(key)) {
      index.set(key, []);
    }
    index.get(key).push(reference);
  }
  return index;
}

function formatPresetReference(reference, presetIndex) {
  const normalized = String(reference || "").replace(/^preset:/, "");
  const preset = presetIndex[normalized] || {};
  const presetName = String(preset.name || "").trim();
  return presetName ? `${normalized} ${presetName}` : normalized;
}

function createCueRow() {
  return {
    id: "",
    cueNumber: "",
    cueName: "",
    part: "",
    trigger: "",
    triggerTime: null,
    fade: null,
    delay: null,
    command: "",
    presetRefs: [],
    effectRefs: [],
    hardValuesCount: 0,
    fixtureCount: 0,
    warnings: [],
    notes: [],
    cueType: "",
    trackingState: "",
    block: false,
    assert: false,
    mib: false,
    fixtureIds: [],
    fixtureLabels: [],
    changeGroups: [],
  };
}

function buildCueReferences(cue, referenceIndex, presetIndex) {
  const references = referenceIndex.get(`cue:${cue.id || ""}`) || [];
  const presetRefs = uniqueStrings([
    ...(cue.values || [])
      .filter((atom) => atom.value_type === "preset_ref" && atom.reference_target)
      .map((atom) => atom.reference_target),
    ...references
      .filter((reference) => reference.kind === "preset_ref" && reference.target)
      .map((reference) => reference.target),
  ]).map((reference) => formatPresetReference(reference, presetIndex));

  const effectRefs = uniqueStrings([
    ...(cue.values || [])
      .filter((atom) => atom.value_type === "effect_ref" && atom.reference_target)
      .map((atom) => String(atom.reference_target).replace(/^effect:/, "")),
    ...references
      .filter((reference) => reference.kind === "effect_ref" && reference.target)
      .map((reference) => String(reference.target).replace(/^effect:/, "")),
  ]);

  return { presetRefs, effectRefs };
}

function mapCueChangeGroups(cue, fixtureIndex) {
  const grouped = new Map();
  for (const atom of cue.values || []) {
    const fixtureId = atom.fixture_id !== null && atom.fixture_id !== undefined ? String(atom.fixture_id) : "unbound";
    if (!grouped.has(fixtureId)) {
      const fixture = fixtureIndex[fixtureId] || {};
      grouped.set(fixtureId, {
        fixtureId: fixtureId === "unbound" ? "" : fixtureId,
        fixtureLabel: fixture.label || fixture.name || (fixtureId === "unbound" ? "Unbound values" : `Fixture ${fixtureId}`),
        fixtureType: fixture.fixture_type || "",
        patch: fixture.patch || "",
        lines: [],
      });
    }
    const target = atom.reference_target ? String(atom.reference_target).replace(/^(preset|effect|group):/, "") : "";
    grouped.get(fixtureId).lines.push({
      attribute: String(atom.attribute || "?"),
      valueType: String(atom.value_type || "unknown"),
      displayValue: target || (atom.raw_value !== null && atom.raw_value !== undefined && atom.raw_value !== "" ? String(atom.raw_value) : "-"),
    });
  }
  return [...grouped.values()].slice(0, 16);
}

function analyzeCueWarnings(cueRow, thresholds = WARNING_THRESHOLDS) {
  const warnings = [];
  if (cueRow.hardValuesCount > 0) {
    warnings.push("cue has hard values");
  }
  if (normalizeText(cueRow.command)) {
    warnings.push("cue has command");
  }
  if (!normalizeText(cueRow.cueName)) {
    warnings.push("cue has no name");
  }
  if (cueRow.effectRefs.length > 0) {
    warnings.push("cue uses effects");
  }
  if (cueRow.fade !== null && cueRow.fade > thresholds.longFade) {
    warnings.push("cue has long fade");
  }
  if (cueRow.delay !== null && cueRow.delay > thresholds.longDelay) {
    warnings.push("cue has long delay");
  }
  if (cueRow.presetRefs.length === 0) {
    warnings.push("cue has no preset references");
  }
  if (cueRow.fixtureCount > thresholds.manyFixtures) {
    warnings.push("cue changes many fixtures");
  }
  if (cueRow.hardValuesCount > thresholds.manyHardValues) {
    warnings.push("cue has many hard values");
  }
  return warnings;
}

function mapSequenceToCueRows(sequence, context) {
  const { presetIndex, fixtureIndex, referenceIndex } = context;
  return (sequence.cues || []).map((cue) => {
    const meta = cue.metadata || {};
    const refsForCue = buildCueReferences(cue, referenceIndex, presetIndex);
    const hardAtoms = (cue.values || []).filter((atom) => atom.value_type === "hard");
    const fixtureIds = uniqueStrings((cue.fixture_ids || []).map((fixtureId) => String(fixtureId)));

    const cueRow = createCueRow();
    cueRow.id = String(cue.id || "");
    cueRow.cueNumber = String(cue.cue_number || "");
    cueRow.cueName = String(cue.name || "");
    cueRow.part = String(cue.part || metaValue(meta, ["cuepart.index", "part", "part.index"]) || "");
    cueRow.trigger = String(cue.trigger || metaValue(meta, ["trigger", "cue.trigger"]) || "");
    cueRow.triggerTime = toNumber(metaValue(meta, [
      "cuepart.triggertime",
      "triggertime",
      "cue.triggertime",
      "cuepart.triggertimeinseconds",
    ]));
    cueRow.fade = toNumber(cue.fade ?? metaValue(meta, ["cuepart.basicfade", "basicfade", "fade"]));
    cueRow.delay = toNumber(cue.delay ?? metaValue(meta, ["cuepart.basicdelay", "cuepart.basicdowndelay", "basicdelay", "delay"]));
    cueRow.command = cue.command ? String(cue.command) : "";
    cueRow.presetRefs = refsForCue.presetRefs;
    cueRow.effectRefs = refsForCue.effectRefs;
    cueRow.hardValuesCount = hardAtoms.length;
    cueRow.fixtureCount = fixtureIds.length;
    cueRow.notes = uniqueStrings([
      metaValue(meta, ["cuepart.name", "part.name"]),
      metaValue(meta, ["cuepart.commanddelay", "commanddelay"]) ? `command delay ${metaValue(meta, ["cuepart.commanddelay", "commanddelay"])}` : "",
      boolFromMeta(meta, ["cuepart.forceeffecttime"]) ? "force effect time" : "",
      cue.source_file ? `source ${cue.source_file}` : "",
    ]);
    cueRow.cueType = String(metaValue(meta, ["cuetype", "cue.type"]) || "");
    cueRow.trackingState = String(metaValue(meta, ["trackingstate", "cue.trackingstate"]) || "");
    cueRow.block = boolFromMeta(meta, ["blockcue", "block", "cue.block"]);
    cueRow.assert = boolFromMeta(meta, ["assertcue", "assert", "cue.assert"]);
    cueRow.mib = boolFromMeta(meta, ["mibcue.number", "mib", "cue.mib"]);
    cueRow.fixtureIds = fixtureIds;
    cueRow.fixtureLabels = fixtureIds.map((fixtureId) => {
      const fixture = fixtureIndex[fixtureId] || {};
      const label = fixture.label || fixture.name || `Fixture ${fixtureId}`;
      const parts = [fixtureId, label];
      if (fixture.fixture_type) {
        parts.push(fixture.fixture_type);
      }
      if (fixture.patch) {
        parts.push(fixture.patch);
      }
      return parts.join(" | ");
    });
    cueRow.changeGroups = mapCueChangeGroups(cue, fixtureIndex);
    cueRow.warnings = analyzeCueWarnings(cueRow);
    return cueRow;
  });
}

function normalizeSequences(rawSequences) {
  return (rawSequences || [])
    .map((sequence) => ({
      id: String(sequence.id || ""),
      number: String(sequence.number || ""),
      name: String(sequence.name || ""),
      sourceFile: String(sequence.source_file || ""),
      isMain: !!sequence.is_main_cue_list,
      cues: sequence.cues || [],
    }))
    .sort((left, right) => {
      if (left.isMain !== right.isMain) {
        return left.isMain ? -1 : 1;
      }
      return naturalCompare(left.number, right.number);
    });
}

function createSequenceViewModel(data) {
  const sequences = normalizeSequences(data.sequences || []);
  const presetIndex = Object.fromEntries((data.presets || []).map((preset) => [String(preset.number || ""), preset]));
  const fixtureIndex = Object.fromEntries(((data.fixture_registry || data.patch_fixtures || [])).map((fixture) => [String(fixture.fixture_id), fixture]));
  const referenceIndex = createReferenceIndex(data.normalized_references || data.references || []);
  return {
    data,
    sequences,
    presetIndex,
    fixtureIndex,
    referenceIndex,
  };
}

function buildTriggerOptions(rows) {
  return ["all", ...uniqueStrings(rows.map((row) => row.trigger)).sort(naturalCompare)];
}

function filterCueRows(rows, filters) {
  const search = normalizeText(filters.search);
  return rows.filter((row) => {
    if (filters.trigger && filters.trigger !== "all" && normalizeText(row.trigger) !== normalizeText(filters.trigger)) {
      return false;
    }
    if (filters.onlyHard && row.hardValuesCount === 0) {
      return false;
    }
    if (filters.onlyPreset && row.presetRefs.length === 0) {
      return false;
    }
    if (filters.onlyEffects && row.effectRefs.length === 0) {
      return false;
    }
    if (filters.onlyWarnings && row.warnings.length === 0) {
      return false;
    }
    if (filters.onlyFade && !(row.fade !== null && row.fade > 0)) {
      return false;
    }
    if (filters.onlyDelay && !(row.delay !== null && row.delay > 0)) {
      return false;
    }
    if (!search) {
      return true;
    }
    const haystack = [
      row.cueNumber,
      row.cueName,
      row.command,
      row.warnings.join(" "),
    ].map(normalizeText).join(" ");
    return haystack.includes(search);
  });
}

function sortCueRows(rows, sortState) {
  const direction = sortState.direction === "desc" ? -1 : 1;
  return [...rows].sort((left, right) => {
    const key = sortState.key;
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

function summarizeSequenceRows(rows) {
  const warnings = rows.filter((row) => row.warnings.length > 0).length;
  const hard = rows.filter((row) => row.hardValuesCount > 0).length;
  const effects = rows.filter((row) => row.effectRefs.length > 0).length;
  const presets = rows.filter((row) => row.presetRefs.length > 0).length;
  return {
    total: rows.length,
    warnings,
    hard,
    effects,
    presets,
  };
}

export {
  COLUMN_DEFS,
  DEFAULT_VISIBLE_COLUMNS,
  WARNING_THRESHOLDS,
  analyzeCueWarnings,
  buildTriggerOptions,
  createCueRow,
  createSequenceViewModel,
  escapeHtml,
  filterCueRows,
  formatNumber,
  mapSequenceToCueRows,
  naturalCompare,
  sortCueRows,
  summarizeSequenceRows,
};
