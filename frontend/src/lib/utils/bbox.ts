import type { BBox, Element } from '$lib/types/contracts';

export function modelBounds(elements: Element[]): BBox {
  if (elements.length === 0) {
    return { x1: 0, y1: 0, x2: 1, y2: 1 };
  }

  let x1 = Number.POSITIVE_INFINITY;
  let y1 = Number.POSITIVE_INFINITY;
  let x2 = Number.NEGATIVE_INFINITY;
  let y2 = Number.NEGATIVE_INFINITY;

  for (const element of elements) {
    x1 = Math.min(x1, element.bbox.x1);
    y1 = Math.min(y1, element.bbox.y1);
    x2 = Math.max(x2, element.bbox.x2);
    y2 = Math.max(y2, element.bbox.y2);
  }

  return { x1, y1, x2, y2 };
}

export function normalizeBBox(
  bbox: BBox,
  bounds: BBox,
  width: number,
  height: number,
  padding = 16
): { x: number; y: number; w: number; h: number } {
  const dx = Math.max(1, bounds.x2 - bounds.x1);
  const dy = Math.max(1, bounds.y2 - bounds.y1);
  const innerW = width - padding * 2;
  const innerH = height - padding * 2;

  const x = ((bbox.x1 - bounds.x1) / dx) * innerW + padding;
  const y = ((bbox.y1 - bounds.y1) / dy) * innerH + padding;
  const w = ((bbox.x2 - bbox.x1) / dx) * innerW;
  const h = ((bbox.y2 - bbox.y1) / dy) * innerH;

  return {
    x,
    y: height - y - h,
    w,
    h
  };
}
