(function () {
  const STYLE_ID = 'graindma-table-panzoom-style';
  const WRAPPER_SELECTOR = '.table-wrap, .matrix-wrap, [data-panzoom-table]';
  const MIN_SCALE = 0.65;
  const MAX_SCALE = 2.25;
  const SCALE_STEP = 0.1;

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function injectStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = `
      .panzoom-ready { position: relative; overscroll-behavior: contain; }
      .panzoom-stage { position: relative; min-width: 100%; min-height: 100%; }
      .panzoom-content { transform-origin: top left; will-change: transform; }
      .panzoom-toolbar {
        position: sticky;
        top: 8px;
        right: 8px;
        z-index: 6;
        display: flex;
        justify-content: flex-end;
        gap: 6px;
        padding: 8px;
        pointer-events: none;
      }
      .panzoom-toolbar-inner {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid #334155;
        border-radius: 999px;
        padding: 6px 8px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.24);
        pointer-events: auto;
      }
      .panzoom-toolbar button {
        width: auto;
        min-width: 34px;
        height: 34px;
        padding: 0 10px;
        border-radius: 999px;
        border: 1px solid #475569;
        background: #172033;
        color: #e5e7eb;
        cursor: pointer;
        font: inherit;
      }
      .panzoom-toolbar button:hover { background: #22304b; }
      .panzoom-scale {
        min-width: 52px;
        text-align: center;
        color: #cbd5e1;
        font-size: 12px;
        font-weight: 700;
      }
      .panzoom-hint {
        color: #94a3b8;
        font-size: 11px;
        white-space: nowrap;
      }
      .col-resize-ready { table-layout: fixed; }
      .col-resize-header {
        position: relative;
      }
      .col-resize-handle {
        position: absolute;
        top: 0;
        right: -4px;
        width: 8px;
        height: 100%;
        cursor: col-resize;
        user-select: none;
        touch-action: none;
        z-index: 8;
      }
      .col-resize-handle::after {
        content: '';
        position: absolute;
        top: 20%;
        bottom: 20%;
        left: 3px;
        width: 2px;
        border-radius: 999px;
        background: rgba(148, 163, 184, 0.55);
        transition: background 120ms ease;
      }
      .col-resize-header:hover .col-resize-handle::after,
      .col-resize-handle.is-active::after {
        background: rgba(56, 189, 248, 0.95);
      }
      @media print {
        .panzoom-toolbar { display: none !important; }
        .panzoom-stage { width: auto !important; height: auto !important; }
        .panzoom-content { transform: none !important; }
        .col-resize-handle { display: none !important; }
      }
    `;
    document.head.appendChild(style);
  }

  function debounceFrame(fn) {
    let scheduled = false;
    return function debounced() {
      if (scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(() => {
        scheduled = false;
        fn();
      });
    };
  }

  function getLeafHeaderCells(table) {
    const head = table.tHead;
    if (!head || !head.rows.length) return [];
    const rows = Array.from(head.rows);
    const grid = [];
    const leaves = [];

    rows.forEach((row, rowIndex) => {
      if (!grid[rowIndex]) grid[rowIndex] = [];
      let columnIndex = 0;
      Array.from(row.cells).forEach((cell) => {
        while (grid[rowIndex][columnIndex]) columnIndex += 1;
        const colspan = Math.max(1, Number(cell.colSpan) || 1);
        const rowspan = Math.max(1, Number(cell.rowSpan) || 1);
        for (let r = rowIndex; r < rowIndex + rowspan; r += 1) {
          if (!grid[r]) grid[r] = [];
          for (let c = columnIndex; c < columnIndex + colspan; c += 1) {
            grid[r][c] = cell;
          }
        }
        if (rowIndex + rowspan >= rows.length) {
          leaves.push({ cell, start: columnIndex, span: colspan });
        }
        columnIndex += colspan;
      });
    });

    return leaves.sort((left, right) => left.start - right.start);
  }

  function ensureColgroup(table, columnCount) {
    let colgroup = table.querySelector(':scope > colgroup');
    if (!colgroup) {
      colgroup = document.createElement('colgroup');
      table.insertBefore(colgroup, table.firstChild);
    }
    while (colgroup.children.length < columnCount) {
      colgroup.appendChild(document.createElement('col'));
    }
    while (colgroup.children.length > columnCount) {
      colgroup.removeChild(colgroup.lastElementChild);
    }
    return Array.from(colgroup.children);
  }

  function setupColumnResize(table) {
    if (!table || table.dataset.columnResizeBound === 'true') return;
    table.dataset.columnResizeBound = 'true';
    table.classList.add('col-resize-ready');

    const MIN_COLUMN_WIDTH = 56;

    function syncHandles() {
      const leaves = getLeafHeaderCells(table);
      if (!leaves.length) return;
      const cols = ensureColgroup(table, leaves.reduce((max, item) => Math.max(max, item.start + item.span), 0));

      table.querySelectorAll('.col-resize-handle').forEach((handle) => handle.remove());
      table.querySelectorAll('.col-resize-header').forEach((cell) => cell.classList.remove('col-resize-header'));

      leaves.forEach(({ cell, start, span }) => {
        if (!cell || span !== 1) return;
        cell.classList.add('col-resize-header');
        const handle = document.createElement('div');
        handle.className = 'col-resize-handle';
        handle.title = 'Tazenim zmenis sirku sloupce';
        handle.dataset.colIndex = String(start);
        handle.addEventListener('pointerdown', (event) => {
          event.preventDefault();
          event.stopPropagation();
          const colIndex = Number(handle.dataset.colIndex || '-1');
          const col = cols[colIndex];
          if (!col) return;
          const startX = event.clientX;
          const initialWidth = Math.max(MIN_COLUMN_WIDTH, Math.round(col.getBoundingClientRect().width || cell.getBoundingClientRect().width));
          handle.classList.add('is-active');
          document.body.style.cursor = 'col-resize';
          document.body.style.userSelect = 'none';

          function onMove(moveEvent) {
            const nextWidth = Math.max(MIN_COLUMN_WIDTH, initialWidth + (moveEvent.clientX - startX));
            col.style.width = `${nextWidth}px`;
          }

          function cleanup() {
            handle.classList.remove('is-active');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            window.removeEventListener('pointermove', onMove);
            window.removeEventListener('pointerup', cleanup);
            window.removeEventListener('pointercancel', cleanup);
          }

          window.addEventListener('pointermove', onMove);
          window.addEventListener('pointerup', cleanup, { once: true });
          window.addEventListener('pointercancel', cleanup, { once: true });
        });
        handle.addEventListener('dblclick', (event) => {
          event.preventDefault();
          event.stopPropagation();
          const colIndex = Number(handle.dataset.colIndex || '-1');
          const col = cols[colIndex];
          if (col) col.style.width = '';
        });
        cell.appendChild(handle);
      });
    }

    const scheduleSync = debounceFrame(syncHandles);
    const observer = new MutationObserver(scheduleSync);
    observer.observe(table, { childList: true, subtree: true });
    window.addEventListener('resize', scheduleSync);
    syncHandles();
  }

  function getViewportForTable(table) {
    if (!table) return null;
    let node = table.parentElement;
    while (node && node !== document.body) {
      if (node.matches && node.matches(WRAPPER_SELECTOR)) return node;
      const style = window.getComputedStyle(node);
      const overflowX = style.overflowX;
      const overflowY = style.overflowY;
      const isScrollable = ['auto', 'scroll'].includes(overflowX) || ['auto', 'scroll'].includes(overflowY);
      if (isScrollable) return node;
      node = node.parentElement;
    }
    return null;
  }

  function normalizeWrapper(wrapper) {
    if (!wrapper || wrapper.dataset.panzoomReady === 'true') return null;
    const table = wrapper.querySelector('table');
    if (!table) return null;

    let stage = wrapper.querySelector(':scope > .panzoom-stage');
    let content = wrapper.querySelector(':scope > .panzoom-stage > .panzoom-content');
    if (!stage || !content) {
      stage = document.createElement('div');
      stage.className = 'panzoom-stage';
      content = document.createElement('div');
      content.className = 'panzoom-content';
      stage.appendChild(content);
      wrapper.insertBefore(stage, wrapper.firstChild);
      content.appendChild(table);
    }

    const toolbar = document.createElement('div');
    toolbar.className = 'panzoom-toolbar';
    toolbar.innerHTML = `
      <div class="panzoom-toolbar-inner">
        <button type="button" data-panzoom-action="out" aria-label="Zoom out">-</button>
        <div class="panzoom-scale">100%</div>
        <button type="button" data-panzoom-action="in" aria-label="Zoom in">+</button>
        <button type="button" data-panzoom-action="reset" aria-label="Reset zoom">100</button>
        <div class="panzoom-hint">Ctrl + wheel = zoom</div>
      </div>
    `;
    wrapper.insertBefore(toolbar, wrapper.firstChild);
    wrapper.classList.add('panzoom-ready');
    wrapper.dataset.panzoomReady = 'true';
    return { wrapper, table, stage, content, toolbar };
  }

  function setupPanzoom(wrapper) {
    const parts = normalizeWrapper(wrapper);
    if (!parts) return;
    const { table, stage, content, toolbar } = parts;
    const scaleLabel = toolbar.querySelector('.panzoom-scale');
    let scale = 1;
    let baseWidth = 0;
    let baseHeight = 0;
    function measureBase() {
      const rect = content.getBoundingClientRect();
      baseWidth = Math.max(1, Math.ceil(rect.width / scale));
      baseHeight = Math.max(1, Math.ceil(rect.height / scale));
    }

    function applyScale(nextScale, centerX, centerY) {
      const clamped = clamp(nextScale, MIN_SCALE, MAX_SCALE);
      if (Math.abs(clamped - scale) < 0.001) return;
      measureBase();
      const prevScale = scale;
      const cx = centerX ?? (wrapper.clientWidth / 2);
      const cy = centerY ?? (wrapper.clientHeight / 2);
      const contentX = (wrapper.scrollLeft + cx) / prevScale;
      const contentY = (wrapper.scrollTop + cy) / prevScale;
      scale = clamped;
      content.style.transform = `scale(${scale})`;
      stage.style.width = `${Math.ceil(baseWidth * scale)}px`;
      stage.style.height = `${Math.ceil(baseHeight * scale)}px`;
      wrapper.scrollLeft = Math.max(0, contentX * scale - cx);
      wrapper.scrollTop = Math.max(0, contentY * scale - cy);
      scaleLabel.textContent = `${Math.round(scale * 100)}%`;
    }

    function refreshStage() {
      measureBase();
      content.style.transform = `scale(${scale})`;
      stage.style.width = `${Math.ceil(baseWidth * scale)}px`;
      stage.style.height = `${Math.ceil(baseHeight * scale)}px`;
      scaleLabel.textContent = `${Math.round(scale * 100)}%`;
    }

    toolbar.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-panzoom-action]');
      if (!button) return;
      const action = button.dataset.panzoomAction;
      if (action === 'in') applyScale(scale + SCALE_STEP);
      if (action === 'out') applyScale(scale - SCALE_STEP);
      if (action === 'reset') {
        scale = 1;
        refreshStage();
      }
    });

    wrapper.addEventListener('wheel', (event) => {
      if (!event.ctrlKey) return;
      event.preventDefault();
      const rect = wrapper.getBoundingClientRect();
      const centerX = event.clientX - rect.left;
      const centerY = event.clientY - rect.top;
      const direction = event.deltaY < 0 ? SCALE_STEP : -SCALE_STEP;
      applyScale(scale + direction, centerX, centerY);
    }, { passive: false });

    const resizeObserver = new ResizeObserver(() => refreshStage());
    resizeObserver.observe(content);
    setupColumnResize(table);
    refreshStage();
  }

  function init() {
    injectStyles();
    const wrappers = new Set([...document.querySelectorAll(WRAPPER_SELECTOR)]);
    document.querySelectorAll('table').forEach((table) => {
      const wrapper = getViewportForTable(table);
      if (wrapper) wrappers.add(wrapper);
    });
    wrappers.forEach(setupPanzoom);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
