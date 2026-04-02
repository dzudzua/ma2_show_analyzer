(function () {
  const STYLE_ID = 'graindma-svg-panzoom-style';
  const WRAPPER_SELECTOR = '.svg-wrap';
  const MIN_SCALE = 0.55;
  const MAX_SCALE = 2.6;
  const SCALE_STEP = 0.12;

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function injectStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = `
      .svg-wrap.svg-panzoom-ready { position: relative; overscroll-behavior: contain; }
      .svg-panzoom-stage { position: relative; min-width: 100%; min-height: 100%; }
      .svg-panzoom-content { transform-origin: top left; will-change: transform; }
      .svg-panzoom-toolbar {
        position: sticky;
        top: 8px;
        z-index: 7;
        display: flex;
        justify-content: flex-end;
        padding: 8px;
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

  function prepareWrapper(wrapper) {
    if (!wrapper || wrapper.dataset.svgPanzoomReady === 'true') return null;
    const svg = wrapper.querySelector('svg');
    if (!svg) return null;

    const stage = document.createElement('div');
    stage.className = 'svg-panzoom-stage';
    const content = document.createElement('div');
    content.className = 'svg-panzoom-content';
    stage.appendChild(content);
    content.appendChild(svg);

    const toolbar = document.createElement('div');
    toolbar.className = 'svg-panzoom-toolbar';
    toolbar.innerHTML = `
      <div class="svg-panzoom-toolbar-inner">
        <button type="button" data-svg-panzoom="out" aria-label="Zoom out">-</button>
        <div class="svg-panzoom-scale">100%</div>
        <button type="button" data-svg-panzoom="in" aria-label="Zoom in">+</button>
        <button type="button" data-svg-panzoom="reset" aria-label="Reset zoom">100</button>
        <div class="svg-panzoom-hint">wheel = zoom</div>
      </div>
    `;

    wrapper.insertBefore(toolbar, wrapper.firstChild);
    wrapper.insertBefore(stage, toolbar.nextSibling);
    wrapper.classList.add('svg-panzoom-ready');
    wrapper.dataset.svgPanzoomReady = 'true';
    return { wrapper, svg, stage, content, toolbar };
  }

  function attachPanzoom(wrapper) {
    const parts = prepareWrapper(wrapper);
    if (!parts) return;
    const { wrapper: host, content, stage, toolbar } = parts;
    const scaleLabel = toolbar.querySelector('.svg-panzoom-scale');
    let scale = 1;
    let baseWidth = 0;
    let baseHeight = 0;
    let drag = null;

    function measureBase() {
      const rect = content.getBoundingClientRect();
      baseWidth = Math.max(1, Math.ceil(rect.width / scale));
      baseHeight = Math.max(1, Math.ceil(rect.height / scale));
    }

    function refresh() {
      measureBase();
      content.style.transform = `scale(${scale})`;
      stage.style.width = `${Math.ceil(baseWidth * scale)}px`;
      stage.style.height = `${Math.ceil(baseHeight * scale)}px`;
      scaleLabel.textContent = `${Math.round(scale * 100)}%`;
    }

    function applyScale(nextScale, centerX, centerY) {
      const clamped = clamp(nextScale, MIN_SCALE, MAX_SCALE);
      if (Math.abs(clamped - scale) < 0.001) return;
      measureBase();
      const prevScale = scale;
      const cx = centerX ?? host.clientWidth / 2;
      const cy = centerY ?? host.clientHeight / 2;
      const contentX = (host.scrollLeft + cx) / prevScale;
      const contentY = (host.scrollTop + cy) / prevScale;
      scale = clamped;
      refresh();
      host.scrollLeft = Math.max(0, contentX * scale - cx);
      host.scrollTop = Math.max(0, contentY * scale - cy);
    }

    toolbar.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-svg-panzoom]');
      if (!button) return;
      const action = button.dataset.svgPanzoom;
      if (action === 'in') applyScale(scale + SCALE_STEP);
      if (action === 'out') applyScale(scale - SCALE_STEP);
      if (action === 'reset') {
        scale = 1;
        refresh();
        host.scrollLeft = 0;
        host.scrollTop = 0;
      }
    });

    host.addEventListener('wheel', (event) => {
      event.preventDefault();
      const rect = host.getBoundingClientRect();
      const centerX = event.clientX - rect.left;
      const centerY = event.clientY - rect.top;
      const direction = event.deltaY < 0 ? SCALE_STEP : -SCALE_STEP;
      applyScale(scale + direction, centerX, centerY);
    }, { passive: false });

    host.addEventListener('pointerdown', (event) => {
      if (event.button !== 0) return;
      if (event.target.closest('button, select, option')) return;
      drag = {
        pointerId: event.pointerId,
        x: event.clientX,
        y: event.clientY,
        left: host.scrollLeft,
        top: host.scrollTop,
        moved: false,
      };
      host.setPointerCapture(event.pointerId);
    });

    host.addEventListener('pointermove', (event) => {
      if (!drag || event.pointerId !== drag.pointerId) return;
      const dx = event.clientX - drag.x;
      const dy = event.clientY - drag.y;
      if (Math.abs(dx) > 4 || Math.abs(dy) > 4) drag.moved = true;
      host.scrollLeft = drag.left - dx;
      host.scrollTop = drag.top - dy;
    });

    function stopDrag(event) {
      if (!drag) return;
      if (event && event.pointerId === drag.pointerId && host.hasPointerCapture(event.pointerId)) {
        host.releasePointerCapture(event.pointerId);
      }
      drag = null;
    }

    host.addEventListener('pointerup', stopDrag);
    host.addEventListener('pointercancel', stopDrag);

    const observer = new ResizeObserver(() => refresh());
    observer.observe(content);
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
