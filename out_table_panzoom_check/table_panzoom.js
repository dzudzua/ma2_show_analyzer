(function () {
  const STYLE_ID = 'graindma-table-panzoom-style';
  const WRAPPER_SELECTOR = '.table-wrap, .matrix-wrap, [data-panzoom-table]';
  const INTERACTIVE_SELECTOR = 'a, button, input, select, textarea, label, summary, [role="button"]';
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
      .panzoom-ready { position: relative; cursor: grab; overscroll-behavior: contain; }
      .panzoom-ready.is-dragging { cursor: grabbing; user-select: none; }
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
      @media print {
        .panzoom-toolbar { display: none !important; }
        .panzoom-stage { width: auto !important; height: auto !important; }
        .panzoom-content { transform: none !important; }
      }
    `;
    document.head.appendChild(style);
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
        <div class="panzoom-hint">drag = move</div>
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
    const { stage, content, toolbar } = parts;
    const scaleLabel = toolbar.querySelector('.panzoom-scale');
    let scale = 1;
    let baseWidth = 0;
    let baseHeight = 0;
    let drag = null;
    let suppressClick = false;

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

    wrapper.addEventListener('pointerdown', (event) => {
      if (event.button !== 0) return;
      if (event.target.closest(INTERACTIVE_SELECTOR)) return;
      drag = {
        pointerId: event.pointerId,
        x: event.clientX,
        y: event.clientY,
        left: wrapper.scrollLeft,
        top: wrapper.scrollTop,
        moved: false,
      };
      suppressClick = false;
      wrapper.classList.add('is-dragging');
      wrapper.setPointerCapture(event.pointerId);
    });

    wrapper.addEventListener('pointermove', (event) => {
      if (!drag || event.pointerId !== drag.pointerId) return;
      const dx = event.clientX - drag.x;
      const dy = event.clientY - drag.y;
      if (Math.abs(dx) > 4 || Math.abs(dy) > 4) {
        drag.moved = true;
        suppressClick = true;
      }
      wrapper.scrollLeft = drag.left - dx;
      wrapper.scrollTop = drag.top - dy;
    });

    function stopDrag(event) {
      if (!drag) return;
      if (event && event.pointerId === drag.pointerId && wrapper.hasPointerCapture(event.pointerId)) {
        wrapper.releasePointerCapture(event.pointerId);
      }
      wrapper.classList.remove('is-dragging');
      drag = null;
      window.setTimeout(() => { suppressClick = false; }, 0);
    }

    wrapper.addEventListener('pointerup', stopDrag);
    wrapper.addEventListener('pointercancel', stopDrag);
    wrapper.addEventListener('click', (event) => {
      if (!suppressClick) return;
      event.preventDefault();
      event.stopPropagation();
    }, true);

    const resizeObserver = new ResizeObserver(() => refreshStage());
    resizeObserver.observe(content);
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
