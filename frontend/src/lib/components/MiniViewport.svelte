<script lang="ts">
  import { browser } from '$app/environment';
  import { onMount } from 'svelte';

  import { modelBounds, normalizeBBox } from '$lib/utils/bbox';
  import type { BBox, ChangeEvent, Element } from '$lib/types/contracts';

  export let elements: Element[] = [];
  export let changedIds: string[] = [];
  export let impactedIds: string[] = [];
  export let selectedImpactedId = '';
  export let changeEvent: ChangeEvent | null = null;

  const width = 560;
  const height = 320;
  const padding = 18;
  const minZoom = 1;
  const maxZoom = 6;
  const usageHintDismissKey = 'mini_viewport_usage_hint_dismissed_v1';

  let showBackground = true;
  let showChanged = true;
  let showImpacted = true;
  let showChangedBefore = true;
  let focusSelectedImpacted = true;
  let showUsageHint = true;

  let zoom = 1;
  let panX = 0;
  let panY = 0;
  let isPanning = false;
  let activePointerId: number | null = null;
  let dragStartClientX = 0;
  let dragStartClientY = 0;
  let dragStartPanX = 0;
  let dragStartPanY = 0;
  let viewportSvg: SVGSVGElement | null = null;

  function translateBBox(bbox: BBox, dx: number, dy: number): BBox {
    return {
      x1: bbox.x1 + dx,
      y1: bbox.y1 + dy,
      x2: bbox.x2 + dx,
      y2: bbox.y2 + dy
    };
  }

  function applyChangeEvent(source: Element[], event: ChangeEvent | null): Element[] {
    if (!event) {
      return source;
    }

    const changed = new Set(event.elementIds);
    return source.map((element) => {
      if (!changed.has(element.id)) {
        return element;
      }

      if (event.newBbox) {
        return { ...element, bbox: { ...event.newBbox } };
      }

      if (event.delta) {
        return { ...element, bbox: translateBBox(element.bbox, event.delta.dx, event.delta.dy) };
      }

      return element;
    });
  }

  function labelX(rectX: number): number {
    return Math.max(4, Math.min(width - 4, rectX + 4));
  }

  function labelY(rectY: number): number {
    return Math.max(12, rectY - 4);
  }

  function clamp(value: number, lower: number, upper: number): number {
    return Math.max(lower, Math.min(upper, value));
  }

  function toSvgCoordinates(clientX: number, clientY: number): { x: number; y: number } | null {
    if (!viewportSvg) {
      return null;
    }

    const rect = viewportSvg.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) {
      return null;
    }

    return {
      x: ((clientX - rect.left) / rect.width) * width,
      y: ((clientY - rect.top) / rect.height) * height
    };
  }

  function setZoom(nextZoom: number, centerX = width / 2, centerY = height / 2): void {
    const clamped = clamp(nextZoom, minZoom, maxZoom);
    if (clamped === zoom) {
      return;
    }

    const worldX = (centerX - panX) / zoom;
    const worldY = (centerY - panY) / zoom;

    zoom = clamped;
    panX = centerX - worldX * zoom;
    panY = centerY - worldY * zoom;
  }

  function zoomIn(): void {
    setZoom(zoom * 1.2);
  }

  function zoomOut(): void {
    setZoom(zoom / 1.2);
  }

  function resetViewport(): void {
    zoom = 1;
    panX = 0;
    panY = 0;
  }

  function handleWheel(event: WheelEvent): void {
    const svgPoint = toSvgCoordinates(event.clientX, event.clientY);
    if (!svgPoint) {
      return;
    }

    const factor = event.deltaY < 0 ? 1.12 : 0.9;
    setZoom(zoom * factor, svgPoint.x, svgPoint.y);
  }

  function handlePointerDown(event: PointerEvent): void {
    if (event.button !== 0 || !viewportSvg) {
      return;
    }

    isPanning = true;
    activePointerId = event.pointerId;
    dragStartClientX = event.clientX;
    dragStartClientY = event.clientY;
    dragStartPanX = panX;
    dragStartPanY = panY;
    viewportSvg.setPointerCapture(event.pointerId);
  }

  function handlePointerMove(event: PointerEvent): void {
    if (!isPanning || event.pointerId !== activePointerId || !viewportSvg) {
      return;
    }

    const rect = viewportSvg.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) {
      return;
    }

    const dx = ((event.clientX - dragStartClientX) / rect.width) * width;
    const dy = ((event.clientY - dragStartClientY) / rect.height) * height;
    panX = dragStartPanX + dx;
    panY = dragStartPanY + dy;
  }

  function handlePointerUp(event: PointerEvent): void {
    if (event.pointerId !== activePointerId) {
      return;
    }

    if (viewportSvg && viewportSvg.hasPointerCapture(event.pointerId)) {
      viewportSvg.releasePointerCapture(event.pointerId);
    }

    isPanning = false;
    activePointerId = null;
  }

  function dismissUsageHint(): void {
    showUsageHint = false;
    if (browser) {
      localStorage.setItem(usageHintDismissKey, '1');
    }
  }

  onMount(() => {
    if (!browser) {
      return;
    }
    showUsageHint = localStorage.getItem(usageHintDismissKey) !== '1';
  });

  $: changedSet = new Set(changedIds);
  $: impactedSet = new Set(impactedIds);
  $: changedBeforeElements = elements.filter((element) => changedSet.has(element.id));
  $: viewportElements = applyChangeEvent(elements, changeEvent);
  $: allImpactedElements = viewportElements.filter((element) => impactedSet.has(element.id) && !changedSet.has(element.id));
  $: focusedImpactedElements =
    focusSelectedImpacted && selectedImpactedId
      ? allImpactedElements.filter((element) => element.id === selectedImpactedId)
      : allImpactedElements;
  $: backgroundElements = viewportElements.filter((element) => !changedSet.has(element.id) && !impactedSet.has(element.id));
  $: changedAfterElements = viewportElements.filter((element) => changedSet.has(element.id));
  $: bounds = modelBounds([...viewportElements, ...changedBeforeElements]);
</script>

<div class="panel">
  <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-600">2D impact overlay</h3>
  <p class="mt-1 text-xs text-slate-500">
    Simplified bounding-box view (not detailed CAD). Orange is changed, red is impacted, dashed orange is pre-change.
  </p>
  {#if showUsageHint}
    <div class="mt-3 flex flex-wrap items-center gap-2 rounded-lg border border-sky-200 bg-sky-50 px-3 py-2 text-xs text-sky-900">
      <span>Tip: scroll to zoom, drag to pan, and click the pills below to show/hide layers.</span>
      <button
        type="button"
        class="chip border border-sky-300 bg-white text-sky-800 hover:bg-sky-100"
        on:click={dismissUsageHint}
      >
        Got it
      </button>
    </div>
  {/if}

  {#if elements.length === 0}
    <p class="mt-3 text-sm text-slate-500">No geometry available for this job.</p>
  {:else}
    <div class="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-600">
      <button
        type="button"
        class="chip border border-slate-300 bg-white text-slate-700 hover:bg-slate-100"
        on:click={zoomOut}
        disabled={zoom <= minZoom}
      >
        Zoom out
      </button>
      <button type="button" class="chip border border-slate-300 bg-white text-slate-700 hover:bg-slate-100" on:click={zoomIn}>
        Zoom in
      </button>
      <button type="button" class="chip border border-slate-300 bg-white text-slate-700 hover:bg-slate-100" on:click={resetViewport}>
        Reset view
      </button>
      <span>Zoom {zoom.toFixed(1)}x</span>
      <span class="text-slate-500">Drag to pan</span>
    </div>
    <svg
      bind:this={viewportSvg}
      class={`mt-3 h-auto w-full rounded-lg border border-slate-200 bg-slate-50 ${isPanning ? 'cursor-grabbing' : 'cursor-grab'}`}
      style="touch-action: none;"
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="Model impact viewport"
      on:wheel|preventDefault={handleWheel}
      on:pointerdown={handlePointerDown}
      on:pointermove={handlePointerMove}
      on:pointerup={handlePointerUp}
      on:pointercancel={handlePointerUp}
      on:dblclick={resetViewport}
    >
      <rect x="0" y="0" width={width} height={height} fill="#f8fafc" />
      <g transform={`matrix(${zoom} 0 0 ${zoom} ${panX} ${panY})`}>
        {#if showBackground}
          {#each backgroundElements as element}
            {@const rect = normalizeBBox(element.bbox, bounds, width, height, padding)}
            <rect
              x={rect.x}
              y={rect.y}
              width={Math.max(rect.w, 2)}
              height={Math.max(rect.h, 2)}
              fill="#94a3b81e"
              stroke="#64748b88"
              stroke-width="1.0"
              vector-effect="non-scaling-stroke"
              rx="2"
            >
              <title>{element.id}</title>
            </rect>
          {/each}
        {/if}

        {#if showImpacted}
          {#each focusedImpactedElements as element}
            {@const rect = normalizeBBox(element.bbox, bounds, width, height, padding)}
            {@const isSelected = selectedImpactedId === element.id}
            <rect
              x={rect.x}
              y={rect.y}
              width={Math.max(rect.w, 2)}
              height={Math.max(rect.h, 2)}
              fill="#ef444455"
              stroke={isSelected ? '#b91c1c' : '#ef4444'}
              stroke-width={isSelected ? 2.2 : 1.1}
              vector-effect="non-scaling-stroke"
              rx="2"
            >
              <title>{element.id}</title>
            </rect>
            {#if isSelected}
              <text
                x={labelX(rect.x)}
                y={labelY(rect.y)}
                font-size="9"
                font-weight="700"
                fill="#7f1d1d"
                stroke="#f8fafc"
                stroke-width="2"
                paint-order="stroke"
              >
                {element.id}
              </text>
            {/if}
          {/each}
        {/if}

        {#if showChangedBefore}
          {#each changedBeforeElements as element}
            {@const rect = normalizeBBox(element.bbox, bounds, width, height, padding)}
            <rect
              x={rect.x}
              y={rect.y}
              width={Math.max(rect.w, 2)}
              height={Math.max(rect.h, 2)}
              fill="none"
              stroke="#c2410c"
              stroke-width="1.3"
              stroke-dasharray="4 3"
              vector-effect="non-scaling-stroke"
              rx="2"
            >
              <title>{element.id} (before change)</title>
            </rect>
          {/each}
        {/if}

        {#if showChanged}
          {#each changedAfterElements as element}
            {@const rect = normalizeBBox(element.bbox, bounds, width, height, padding)}
            <rect
              x={rect.x}
              y={rect.y}
              width={Math.max(rect.w, 2)}
              height={Math.max(rect.h, 2)}
              fill="#fb923c55"
              stroke="#f97316"
              stroke-width="1.8"
              vector-effect="non-scaling-stroke"
              rx="2"
            >
              <title>{element.id}</title>
            </rect>
            <text
              x={labelX(rect.x)}
              y={labelY(rect.y)}
              font-size="9"
              font-weight="700"
              fill="#9a3412"
              stroke="#f8fafc"
              stroke-width="2"
              paint-order="stroke"
            >
              {element.id}
            </text>
          {/each}
        {/if}
      </g>
    </svg>
    <p class="mt-2 text-xs text-slate-500">Layer controls: click pills to toggle visibility.</p>
    <div class="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
      <button
        type="button"
        class={`chip border ${showChanged ? 'border-orange-200 bg-orange-100 text-orange-800' : 'border-slate-200 bg-white text-slate-500'}`}
        on:click={() => (showChanged = !showChanged)}
      >
        Changed ({changedAfterElements.length})
      </button>
      <button
        type="button"
        class={`chip border ${showChangedBefore ? 'border-orange-200 bg-orange-50 text-orange-700' : 'border-slate-200 bg-white text-slate-500'}`}
        on:click={() => (showChangedBefore = !showChangedBefore)}
      >
        Changed before
      </button>
      <button
        type="button"
        class={`chip border ${showImpacted ? 'border-red-200 bg-red-100 text-red-800' : 'border-slate-200 bg-white text-slate-500'}`}
        on:click={() => (showImpacted = !showImpacted)}
      >
        Impacted ({allImpactedElements.length})
      </button>
      <button
        type="button"
        class={`chip border ${showBackground ? 'border-slate-300 bg-slate-200 text-slate-700' : 'border-slate-200 bg-white text-slate-500'}`}
        on:click={() => (showBackground = !showBackground)}
      >
        Background model
      </button>
      <button
        type="button"
        class={`chip border ${focusSelectedImpacted ? 'border-red-200 bg-red-50 text-red-700' : 'border-slate-200 bg-white text-slate-500'}`}
        on:click={() => (focusSelectedImpacted = !focusSelectedImpacted)}
        disabled={!selectedImpactedId}
      >
        Focus selected impact
      </button>
    </div>
  {/if}
</div>
