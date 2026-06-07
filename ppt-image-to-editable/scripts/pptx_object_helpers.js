"use strict";

/**
 * Reusable pptxgenjs helpers for image-to-editable reconstruction.
 *
 * These helpers do not replace page-specific coordinates. They enforce the
 * repeatable rules that should stay consistent across decks:
 * - integer font sizes;
 * - explicit vs wrapped line-break policy;
 * - positive geometry for lines/arrows;
 * - recorded arrow variants;
 * - measured rounded-corner radius.
 */

function assertIntegerFontSize(fontSize, label = "fontSize") {
  if (!Number.isInteger(fontSize)) {
    throw new Error(`${label} must be an integer point size, got ${fontSize}`);
  }
  return fontSize;
}

function normalizeText(text, lineBreakPolicy = "wrap_by_box") {
  const value = String(text ?? "");
  const hasHardBreak = value.includes("\n");
  const hardBreakPolicies = new Set([
    "explicit_source",
    "intentional_layout",
    "manual_after_visual_check",
  ]);

  if (hasHardBreak && !hardBreakPolicies.has(lineBreakPolicy)) {
    throw new Error(
      `Text contains hard line breaks but policy is ${lineBreakPolicy}. ` +
        "Use explicit_source/intentional_layout/manual_after_visual_check, " +
        "or remove hard breaks and let the text box wrap."
    );
  }
  if (!hasHardBreak && lineBreakPolicy === "explicit_source") {
    throw new Error("explicit_source line-break policy requires a hard line break in text");
  }
  return value;
}

function pxScaler(pagePx, slideInches) {
  const sx = slideInches.w / pagePx.w;
  const sy = slideInches.h / pagePx.h;
  return {
    x: (px) => px * sx,
    y: (px) => px * sy,
    w: (px) => px * sx,
    h: (px) => px * sy,
    box: (b) => ({ x: b.x * sx, y: b.y * sy, w: b.w * sx, h: b.h * sy }),
  };
}

function addTextBox(slide, text, box, options = {}) {
  const fontSize = assertIntegerFontSize(options.fontSize ?? options.size ?? 14);
  const lineBreakPolicy = options.lineBreakPolicy ?? options.line_break_policy ?? "wrap_by_box";
  const normalized = normalizeText(text, lineBreakPolicy);
  slide.addText(normalized, {
    x: box.x,
    y: box.y,
    w: box.w,
    h: box.h,
    fontFace: options.fontFace ?? "Microsoft YaHei",
    fontSize,
    color: options.color ?? "111827",
    bold: Boolean(options.bold),
    italic: Boolean(options.italic),
    align: options.align ?? "left",
    valign: options.valign ?? "top",
    margin: options.margin ?? 0,
    breakLine: false,
    fit: options.fit ?? "shrink",
    autoFit: options.autoFit,
    rotate: options.rotate,
  });
}

function positiveLineGeometry(start, end) {
  let x1 = start.x;
  let y1 = start.y;
  let x2 = end.x;
  let y2 = end.y;
  let reversed = false;
  if (x2 < x1 || (x2 === x1 && y2 < y1)) {
    [x1, x2] = [x2, x1];
    [y1, y2] = [y2, y1];
    reversed = true;
  }
  return { x: x1, y: y1, w: x2 - x1, h: y2 - y1, reversed };
}

const ARROW_PRESETS = {
  line_no_head: {},
  line_end_triangle: { endArrowType: "triangle" },
  line_begin_triangle: { beginArrowType: "triangle" },
  line_double_triangle: { beginArrowType: "triangle", endArrowType: "triangle" },
  line_end_stealth: { endArrowType: "stealth" },
  line_begin_stealth: { beginArrowType: "stealth" },
  line_double_stealth: { beginArrowType: "stealth", endArrowType: "stealth" },
  line_end_oval: { endArrowType: "oval" },
  line_begin_oval: { beginArrowType: "oval" },
  line_double_oval: { beginArrowType: "oval", endArrowType: "oval" },
};

function swapArrowHeads(opts) {
  const swapped = { ...opts };
  const begin = swapped.beginArrowType;
  swapped.beginArrowType = swapped.endArrowType;
  swapped.endArrowType = begin;
  return swapped;
}

function addLineArrow(pptx, slide, arrowKind, start, end, options = {}) {
  if (!ARROW_PRESETS[arrowKind]) {
    throw new Error(`Unsupported line arrow kind: ${arrowKind}`);
  }
  const g = positiveLineGeometry(start, end);
  const preset = g.reversed ? swapArrowHeads(ARROW_PRESETS[arrowKind]) : ARROW_PRESETS[arrowKind];
  slide.addShape(pptx.ShapeType.line, {
    x: g.x,
    y: g.y,
    w: g.w,
    h: g.h,
    line: {
      color: options.color ?? "1f77c9",
      width: options.width ?? options.lineWidth ?? 1.5,
      dash: options.dash,
      beginArrowType: preset.beginArrowType,
      endArrowType: preset.endArrowType,
    },
  });
}

function cornerRadiusRatio(cornerRadiusPx, boxPx) {
  if (!Number.isFinite(cornerRadiusPx) || cornerRadiusPx < 0) {
    throw new Error(`cornerRadiusPx must be a non-negative number, got ${cornerRadiusPx}`);
  }
  const minSide = Math.max(1, Math.min(boxPx.w, boxPx.h));
  return Math.max(0, Math.min(0.5, cornerRadiusPx / minSide));
}

function addRoundedRect(pptx, slide, box, options = {}) {
  const radiusRatio =
    options.cornerRadiusRatio ??
    (options.cornerRadiusPx !== undefined && options.boxPx
      ? cornerRadiusRatio(options.cornerRadiusPx, options.boxPx)
      : undefined);

  slide.addShape(pptx.ShapeType.roundRect, {
    x: box.x,
    y: box.y,
    w: box.w,
    h: box.h,
    rectRadius: radiusRatio,
    fill: options.fill ?? { color: "FFFFFF", transparency: 0 },
    line: options.line ?? { color: "1f77c9", width: 1 },
    shadow: options.shadow,
  });
}

module.exports = {
  ARROW_PRESETS,
  addLineArrow,
  addRoundedRect,
  addTextBox,
  assertIntegerFontSize,
  cornerRadiusRatio,
  normalizeText,
  positiveLineGeometry,
  pxScaler,
};
