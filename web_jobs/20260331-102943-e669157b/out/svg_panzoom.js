(function () {
  const STYLE_ID = 'graindma-svg-panzoom-style';
  const WRAPPER_SELECTOR = '.svg-wrap';
  const NODE_SELECTOR = '[data-graph-node="true"]';
  const MIN_SCALE = 0.35;
  const MAX_SCALE = 10;
  const ZOOM_FACTOR = 1.18;
  const DRAG_THRESHOLD = 4;

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function injectStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = `
      .svg-wrap.svg-panzoom-ready {
        position: relative;
        overflow: hidden;
        overscroll-behavior: contain;
        touch-action: none;
      }
      .svg-wrap.svg-panzoom-ready svg {
        display: block;
        width: 100%;
        height: auto;
        user-select: none;
        -webkit-user-drag: none;
      }
      .svg-wrap.is-panning { cursor: grabbing; }
      .svg-wrap:not(.is-panning) svg { cursor: grab; }
      .svg-panzoom-toolbar {
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 7;
        display: flex;
        justify-content: flex-end;
        pointer-events: none;
      }
      .svg-panzoom-toolbar-inner {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid #334155;
        border-radius: 999px;
        padding: 6px 8px;
        box-shadow: 0 6px 18px rgba(0,0,0,.24);
        pointer-events: auto;
      }
      .svg-panzoom-toolbar button {
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
      .svg-panzoom-toolbar button:hover { background: #22304b; }
      .svg-panzoom-scale {
        min-width: 52px;
        text-align: center;
        color: #cbd5e1;
        font-size: 12px;
        font-weight: 700;
      }
      .svg-panzoom-hint {
        color: #94a3b8;
        font-size: 11px;
        white-space: nowrap;
      }
    `;
    document.head.appendChild(style);
  }

  function parseViewBox(svg) {
    const raw = svg.getAttribute('viewBox');
    if (raw) {
      const values = raw.trim().split(/\s+/).map(Number);
      if (values.length === 4 && values.every(Number.isFinite)) {
        return { x: values[0], y: values[1], width: values[2], height: values[3] };
      }
    }
    const width = Number(svg.getAttribute('width')) || svg.clientWidth || 1000;
    const height = Number(svg.getAttribute('height')) || svg.clientHeight || 600;
    return { x: 0, y: 0, width, height };
  }

  function setViewBox(svg, viewBox) {
    svg.setAttribute('viewBox', `${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`);
  }

  function getPointInViewBox(svg, viewBox, clientX, clientY) {
    const rect = svg.getBoundingClientRect();
    const relX = clamp((clientX - rect.left) / Math.max(rect.width, 1), 0, 1);
    const relY = clamp((clientY - rect.top) / Math.max(rect.height, 1), 0, 1);
    return {
      x: viewBox.x + relX * viewBox.width,
      y: viewBox.y + relY * viewBox.height,
      relX,
      relY,
    };
  }

  function prepareWrapper(wrapper) {
    if (!wrapper || wrapper.dataset.svgPanzoomReady === 'true') return null;
    const svg = wrapper.querySelector('svg');
    if (!svg) return null;

    const toolbar = document.createElement('div');
    toolbar.className = 'svg-panzoom-toolbar';
    toolbar.innerHTML = `
      <div class="svg-panzoom-toolbar-inner">
        <button type="button" data-svg-panzoom="out" aria-label="Zoom out">-</button>
        <div class="svg-panzoom-scale">100%</div>
        <button type="button" data-svg-panzoom="in" aria-label="Zoom in">+</button>
        <button type="button" data-svg-panzoom="reset" aria-label="Reset zoom">100</button>
        <div class="svg-panzoom-hint">wheel = zoom, drag = pan</div>
      </div>
    `;

    wrapper.insertBefore(toolbar, wrapper.firstChild);
    wrapper.classList.add('svg-panzoom-ready');
    wrapper.dataset.svgPanzoomReady = 'true';
    return { wrapper, svg, toolbar };
  }

  function attachPanzoom(wrapper) {
    const parts = prepareWrapper(wrapper);
    if (!parts) return;

    const { wrapper: host, svg, toolbar } = parts;
    const scaleLabel = toolbar.querySelector('.svg-panzoom-scale');
    const initialViewBox = parseViewBox(svg);
    let viewBox = { ...initialViewBox };
    let drag = null;

    function currentScale() {
      return initialViewBox.width / viewBox.width;
    }

    function refresh() {
      setViewBox(svg, viewBox);
      scaleLabel.textContent = `${Math.round(currentScale() * 100)}%`;
    }

    function zoomAround(clientX, clientY, zoomIn) {
      const factor = zoomIn ? 1 / ZOOM_FACTOR : ZOOM_FACTOR;
      const nextWidth = clamp(viewBox.width * factor, initialViewBox.width / MAX_SCALE, initialViewBox.width / MIN_SCALE);
      const nextHeight = clamp(viewBox.height * factor, initialViewBox.height / MAX_SCALE, initialViewBox.height / MIN_SCALE);
      if (Math.abs(nextWidth - viewBox.width) < 0.001 && Math.abs(nextHeight - viewBox.height) < 0.001) return;

      const point = getPointInViewBox(svg, viewBox, clientX, clientY);
      viewBox = {
        x: point.x - point.relX * nextWidth,
        y: point.y - point.relY * nextHeight,
        width: nextWidth,
        height: nextHeight,
      };
      refresh();
    }

    function zoomCentered(zoomIn) {
      const rect = svg.getBoundingClientRect();
      zoomAround(rect.left + rect.width / 2, rect.top + rect.height / 2, zoomIn);
    }

    function resetView() {
      viewBox = { ...initialViewBox };
      refresh();
    }

    toolbar.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-svg-panzoom]');
      if (!button) return;
      const action = button.dataset.svgPanzoom;
      if (action === 'in') zoomCentered(true);
      if (action === 'out') zoomCentered(false);
      if (action === 'reset') resetView();
    });

    host.addEventListener('wheel', (event) => {
      event.preventDefault();
      zoomAround(event.clientX, event.clientY, event.deltaY < 0);
    }, { passive: false });

    host.addEventListener('pointerdown', (event) => {
      if (event.button !== 0) return;
      if (event.target.closest('button, select, option, a')) return;
      if (event.target.closest(NODE_SELECTOR)) return;
      drag = {
        pointerId: event.pointerId,
        clientX: event.clientX,
        clientY: event.clientY,
        viewBox: { ...viewBox },
        panning: false,
      };
      host.setPointerCapture(event.pointerId);
    });

    host.addEventListener('pointermove', (event) => {
      if (!drag || event.pointerId !== drag.pointerId) return;
      const rect = svg.getBoundingClientRect();
      const rawDx = event.clientX - drag.clientX;
      const rawDy = event.clientY - drag.clientY;
      if (!drag.panning && (Math.abs(rawDx) > DRAG_THRESHOLD || Math.abs(rawDy) > DRAG_THRESHOLD)) {
        drag.panning = true;
        host.classList.add('is-panning');
      }
      if (!drag.panning) return;
      const dx = (rawDx / Math.max(rect.width, 1)) * drag.viewBox.width;
      const dy = (rawDy / Math.max(rect.height, 1)) * drag.viewBox.height;
      viewBox = {
        x: drag.viewBox.x - dx,
        y: drag.viewBox.y - dy,
        width: drag.viewBox.width,
        height: drag.viewBox.height,
      };
      refresh();
    });

    function stopDrag(event) {
      if (!drag) return;
      if (event && event.pointerId === drag.pointerId && host.hasPointerCapture(event.pointerId)) {
        host.releasePointerCapture(event.pointerId);
      }
      drag = null;
      host.classList.remove('is-panning');
    }

    host.addEventListener('pointerup', stopDrag);
    host.addEventListener('pointercancel', stopDrag);
    host.addEventListener('pointerleave', (event) => {
      if (drag && event.pointerId === drag.pointerId) stopDrag(event);
    });

    window.__svgPanzoomApi = window.__svgPanzoomApi || {};
    if (svg.id) {
      window.__svgPanzoomApi[svg.id] = {
        zoomIn() { zoomCentered(true); },
        zoomOut() { zoomCentered(false); },
        reset() { resetView(); },
        fit() { resetView(); },
      };
    }

    refresh();
  }

  function init() {
    injectStyles();
    document.querySelectorAll(WRAPPER_SELECTOR).forEach(attachPanzoom);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
