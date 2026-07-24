"""Build pptx/6g_talk.pptx from content.py — mirrors the Beamer deck 1:1.

16:9; dark title/section/standout slides, light content slides; equations and
TikZ block diagrams rendered to 300-dpi PNG via latex_render and inserted as
images; speaker notes in the notes pane; demo figures on the backup slides.

Run:  ../.venv/bin/python build_pptx.py     (from pptx/)
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

import content as C
import latex_render as LR

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "figures")

# ---- palette ----
DARK = RGBColor(0x1A, 0x1A, 0x19)
LIGHT = RGBColor(0xFC, 0xFC, 0xFB)
ACCENT = RGBColor(0x0F, 0x71, 0x73)
ACCENT_L = RGBColor(0x6F, 0xB0, 0xB1)
INK = RGBColor(0x0B, 0x0B, 0x0B)
INK2 = RGBColor(0x52, 0x51, 0x4E)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Arial"

SW, SH = 13.333, 7.5   # inches

prs = Presentation()
prs.slide_width = Inches(SW)
prs.slide_height = Inches(SH)
BLANK = prs.slide_layouts[6]


# ----------------------------- primitives -----------------------------
def _bg(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def _rect(slide, l, t, w, h, color, line=None, shape=MSO_SHAPE.RECTANGLE):
    sp = slide.shapes.add_shape(shape, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid(); sp.fill.fore_color.rgb = color
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line; sp.line.width = Pt(1)
    sp.shadow.inherit = False
    return sp


def _text(slide, l, t, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
          wrap=True):
    """runs: list of paragraphs; each paragraph is list of (text, size, color,
    bold, italic) tuples."""
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = 0; tf.margin_right = 0
    tf.margin_top = Pt(2); tf.margin_bottom = Pt(2)
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        for (txt, size, color, bold, italic) in para:
            r = p.add_run(); r.text = txt
            r.font.size = Pt(size); r.font.color.rgb = color
            r.font.bold = bold; r.font.italic = italic; r.font.name = FONT
    return tb


def _fit(slide, path, bl, bt, bw, bh, halign="center", valign="middle"):
    with Image.open(path) as im:
        iw, ih = im.size
    ar = iw / ih
    if bw / bh > ar:
        h = bh; w = bh * ar
    else:
        w = bw; h = bw / ar
    l = bl + (bw - w) / 2 if halign == "center" else (bl if halign == "left" else bl + bw - w)
    t = bt + (bh - h) / 2 if valign == "middle" else (bt if valign == "top" else bt + bh - h)
    slide.shapes.add_picture(path, Inches(l), Inches(t), Inches(w), Inches(h))
    return w, h


def _notes(slide, text):
    if text:
        slide.notes_slide.notes_text_frame.text = text


def _img_path(name):
    return name if os.path.isabs(name) else os.path.join(FIGDIR, name)


# ----------------------------- slide title chrome -----------------------------
def _content_header(slide, title, idx, total):
    _rect(slide, 0, 0, SW, 0.12, ACCENT)                      # top accent strip
    _text(slide, 0.55, 0.30, 11.0, 0.9,
          [[(title, 27, INK, True, False)]], anchor=MSO_ANCHOR.MIDDLE)
    _rect(slide, 0.57, 1.16, 3.1, 0.035, ACCENT)             # title underline
    _text(slide, SW - 1.7, SH - 0.42, 1.2, 0.3,
          [[(f"{idx} / {total}", 11, INK2, False, False)]], align=PP_ALIGN.RIGHT)


def _bullets(slide, bullets, l, t, w, h):
    if not bullets:
        return
    n = len(bullets)
    size = 20 if n <= 3 else (18 if n == 4 else (16 if n == 5 else 15))
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = 0; tf.margin_right = 0
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(8); p.space_before = Pt(0); p.line_spacing = 1.05
        r = p.add_run(); r.text = "▸  "
        r.font.size = Pt(size); r.font.color.rgb = ACCENT; r.font.bold = True
        r.font.name = FONT
        r2 = p.add_run(); r2.text = b
        r2.font.size = Pt(size); r2.font.color.rgb = INK; r2.font.name = FONT


def _demo_banner(slide, text):
    _rect(slide, 0.7, 6.34, SW - 1.4, 0.56, ACCENT,
          shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    _text(slide, 0.95, 6.34, SW - 1.9, 0.56,
          [[(text, 14.5, WHITE, True, False)]], anchor=MSO_ANCHOR.MIDDLE)


def _equations(slide, eqs, top, max_w=11.0, each_h=1.35):
    """Render + stack equation images centered; return y after last eq."""
    y = top
    for name, latex in eqs:
        path = LR.eq(latex, name=name)
        w, h = _fit(slide, path, (SW - max_w) / 2, y, max_w, each_h,
                    halign="center", valign="top")
        y += h + 0.18
    return y


# ----------------------------- slide kinds -----------------------------
def title_slide(s):
    slide = prs.slides.add_slide(BLANK); _bg(slide, DARK)
    _rect(slide, 0, 0, 0.28, SH, ACCENT)
    _text(slide, 0.9, 1.75, 11.3, 2.2,
          [[(s["title"], 40, WHITE, True, False)]], anchor=MSO_ANCHOR.MIDDLE)
    _rect(slide, 0.95, 3.95, 6.0, 0.04, ACCENT_L)
    _text(slide, 0.95, 4.15, 11.0, 0.6,
          [[(s["subtitle"], 19, ACCENT_L, False, False)]])
    _text(slide, 0.95, 5.7, 11.0, 1.4,
          [[(s["author"], 20, WHITE, True, False)],
           [(s["institute"], 15, RGBColor(0xC3, 0xC2, 0xB7), False, False)],
           [(s["date"], 13, RGBColor(0xC3, 0xC2, 0xB7), False, True)]])
    _notes(slide, s.get("notes"))


def section_slide(s):
    slide = prs.slides.add_slide(BLANK); _bg(slide, DARK)
    num, _, rest = s["title"].partition(" · ")
    _text(slide, 0.9, 2.5, 1.8, 1.6,
          [[(num, 66, ACCENT_L, True, False)]], anchor=MSO_ANCHOR.MIDDLE)
    _rect(slide, 2.75, 2.7, 0.045, 1.6, ACCENT)
    _text(slide, 3.05, 2.5, 9.2, 1.6,
          [[(rest, 34, WHITE, True, False)]], anchor=MSO_ANCHOR.MIDDLE)
    _notes(slide, s.get("notes") or f"Section transition — {rest}. "
           "Pause, re-orient the audience, then move into the first slide.")


def standout_slide(s):
    slide = prs.slides.add_slide(BLANK); _bg(slide, ACCENT)
    _text(slide, 0.9, 2.1, 11.5, 1.5,
          [[(s["title"], 48, WHITE, True, False)]],
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    paras = []
    for i, ln in enumerate(s["lines"]):
        big = (i == 1)
        paras.append([(ln, 22 if big else 17, WHITE, big, i != 1)])
    _text(slide, 1.4, 4.0, 10.5, 2.2, paras,
          align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.TOP)
    _notes(slide, s.get("notes"))


def refs_slide(s, idx, total):
    slide = prs.slides.add_slide(BLANK); _bg(slide, LIGHT)
    _content_header(slide, s["title"], idx, total)
    refs = C.REFERENCES
    half = (len(refs) + 1) // 2
    cols = [refs[:half], refs[half:]]
    for c, group in enumerate(cols):
        l = 0.6 + c * 6.15
        tb = slide.shapes.add_textbox(Inches(l), Inches(1.35), Inches(5.95),
                                      Inches(5.6))
        tf = tb.text_frame; tf.word_wrap = True
        tf.margin_left = 0; tf.margin_right = 0
        start = c * half
        for i, ref in enumerate(group):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(6); p.line_spacing = 1.0
            r = p.add_run(); r.text = f"[{start + i + 1}] "
            r.font.size = Pt(10.5); r.font.bold = True; r.font.color.rgb = ACCENT
            r.font.name = FONT
            r2 = p.add_run(); r2.text = ref
            r2.font.size = Pt(10.5); r2.font.color.rgb = INK; r2.font.name = FONT
    _text(slide, 0.6, 7.0, 12.0, 0.4,
          [[("Tools: MATLAB (SPT / CommT / DLT)  •  NVIDIA Sionna  •  this "
             "talk's code", 12, INK2, False, True)]])
    _notes(slide, s.get("notes"))


def table_slide(s, idx, total):
    slide = prs.slides.add_slide(BLANK); _bg(slide, LIGHT)
    _content_header(slide, s["title"], idx, total)
    t = s["table"]
    nrows, ncols = len(t["rows"]) + 1, len(t["headers"])
    has_bul = bool(s.get("bullets"))
    tbl_h = 4.2 if has_bul else 5.2
    gt = slide.shapes.add_table(nrows, ncols, Inches(0.7), Inches(1.4),
                                Inches(SW - 1.4), Inches(tbl_h)).table
    # header
    for j, htxt in enumerate(t["headers"]):
        cell = gt.cell(0, j)
        cell.fill.solid(); cell.fill.fore_color.rgb = ACCENT
        p = cell.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
        r = p.add_run(); r.text = htxt
        r.font.size = Pt(15); r.font.bold = True; r.font.color.rgb = WHITE
        r.font.name = FONT
    for i, row in enumerate(t["rows"], start=1):
        for j, val in enumerate(row):
            cell = gt.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if i % 2 else RGBColor(0xEF, 0xF3, 0xF3)
            p = cell.text_frame.paragraphs[0]
            r = p.add_run(); r.text = val
            r.font.size = Pt(13.5); r.font.name = FONT
            emph = j == 0 or val in ("NEED",)
            r.font.bold = emph
            r.font.color.rgb = ACCENT if val == "NEED" else INK
    if has_bul:
        _bullets(slide, s["bullets"], 0.7, 5.85, SW - 1.4, 1.3)
    _notes(slide, s.get("notes"))


def content_slide(s, idx, total):
    slide = prs.slides.add_slide(BLANK); _bg(slide, LIGHT)
    _content_header(slide, s["title"], idx, total)
    layout = s["layout"]
    eqs = s.get("eq") or []
    tikz = s.get("tikz")
    bullets = s.get("bullets") or []
    img = s.get("img")
    demo = s.get("demo")
    bottom = 6.2 if demo else 7.05

    if layout == "bullets":
        _bullets(slide, bullets, 0.75, 1.5, SW - 1.5, bottom - 1.5)

    elif layout == "bullets_img":
        _bullets(slide, bullets, 0.7, 1.55, 6.4, bottom - 1.55)
        if img:
            _fit(slide, _img_path(img), 7.25, 1.4, 5.5, bottom - 1.4)

    elif layout == "img_bullets":
        if img:
            _fit(slide, _img_path(img), 0.6, 1.4, 5.6, bottom - 1.4)
        _bullets(slide, bullets, 6.4, 1.55, 6.35, bottom - 1.55)

    elif layout == "eq_bullets":
        y = _equations(slide, eqs, 1.35) if eqs else 1.4
        if tikz:
            path = LR.tikz(tikz)
            _, th = _fit(slide, path, 0.7, y + 0.05, SW - 1.4,
                         min(2.6, bottom - y - 0.05), valign="top")
            y += th + 0.2
        _bullets(slide, bullets, 0.9, y + 0.1, SW - 1.8, max(0.6, bottom - y - 0.1))

    elif layout == "eq_bullets_img":
        y = _equations(slide, eqs, 1.32)
        _bullets(slide, bullets, 0.7, y + 0.15, 6.5, bottom - y - 0.15)
        if img:
            _fit(slide, _img_path(img), 7.35, y + 0.1, 5.4, bottom - y - 0.1)

    elif layout == "img":
        bh = (bottom - 1.35) - (0.9 if bullets else 0.0)
        if img:
            _fit(slide, _img_path(img), 1.1, 1.35, SW - 2.2, bh)
        if bullets:
            _bullets(slide, bullets, 0.9, 1.35 + bh + 0.05, SW - 1.8, 0.85)

    if demo:
        _demo_banner(slide, demo)
    _notes(slide, s.get("notes"))


def backup_slide(s, idx, total):
    slide = prs.slides.add_slide(BLANK); _bg(slide, LIGHT)
    _content_header(slide, s["title"], idx, total)
    _text(slide, 0.6, 1.18, 6.0, 0.35,
          [[("Backup: pre-computed result", 13, ACCENT, True, True)]])
    _fit(slide, _img_path(s["img"]), 1.2, 1.7, SW - 2.4, 5.2)
    _notes(slide, s.get("notes"))


# ----------------------------- build -----------------------------
def build():
    total = len(C.SLIDES)
    for idx, s in enumerate(C.SLIDES, start=1):
        k = s["kind"]
        if k == "title":
            title_slide(s)
        elif k == "section":
            section_slide(s)
        elif k == "standout":
            standout_slide(s)
        elif k == "backup":
            backup_slide(s, idx, total)
        elif k == "content" and s["layout"] == "table":
            table_slide(s, idx, total)
        elif k == "content" and s["layout"] == "refs":
            refs_slide(s, idx, total)
        elif k == "content":
            content_slide(s, idx, total)
        else:
            raise ValueError(f"unknown slide: {s}")
    out = os.path.join(HERE, "6g_talk.pptx")
    prs.save(out)
    print(f"saved {out}  ({total} slides)")


if __name__ == "__main__":
    build()
