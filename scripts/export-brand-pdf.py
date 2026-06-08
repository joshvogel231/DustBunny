"""
export-brand-pdf.py
Generates The Dust Bunny brand guide PDF.
Run: python3 scripts/export-brand-pdf.py
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, Image as RLImage
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
MASCOT_PNG = os.path.join(ROOT, "public", "mascot", "mascot.png")
OUT_PATH   = os.path.join(ROOT, "public", "mascot", "dust-bunny-brand-guide.pdf")

# ── Brand colors ─────────────────────────────────────────────────────────────
CREAM       = colors.HexColor("#f4ead2")
INK         = colors.HexColor("#1a1714")
COMIC_RED   = colors.HexColor("#e23b2e")
MUSTARD     = colors.HexColor("#f2b93b")
TEAL        = colors.HexColor("#2a9d9b")
DUST        = colors.HexColor("#c9b79c")
NEWSPRINT   = colors.HexColor("#efe3c8")
PAPER_SHADOW= colors.HexColor("#d8c9a8")

# ── Styles ───────────────────────────────────────────────────────────────────
def make_styles():
    return {
        "cover_title": ParagraphStyle("cover_title",
            fontName="Helvetica-Bold", fontSize=42, leading=46,
            textColor=CREAM, alignment=TA_CENTER, spaceAfter=8),
        "cover_sub": ParagraphStyle("cover_sub",
            fontName="Helvetica-Bold", fontSize=14, leading=18,
            textColor=MUSTARD, alignment=TA_CENTER, spaceAfter=4,
            letterSpacing=3),
        "cover_url": ParagraphStyle("cover_url",
            fontName="Helvetica", fontSize=11, leading=14,
            textColor=DUST, alignment=TA_CENTER),
        "section_label": ParagraphStyle("section_label",
            fontName="Helvetica-Bold", fontSize=8, leading=10,
            textColor=TEAL, spaceAfter=4, letterSpacing=2),
        "h1": ParagraphStyle("h1",
            fontName="Helvetica-Bold", fontSize=26, leading=28,
            textColor=INK, spaceAfter=6),
        "h2": ParagraphStyle("h2",
            fontName="Helvetica-Bold", fontSize=17, leading=20,
            textColor=INK, spaceBefore=18, spaceAfter=6),
        "h3": ParagraphStyle("h3",
            fontName="Helvetica-Bold", fontSize=12, leading=15,
            textColor=INK, spaceBefore=10, spaceAfter=3),
        "body": ParagraphStyle("body",
            fontName="Helvetica", fontSize=10, leading=15,
            textColor=INK, spaceAfter=6),
        "body_sm": ParagraphStyle("body_sm",
            fontName="Helvetica", fontSize=9, leading=13,
            textColor=INK, spaceAfter=4),
        "mono": ParagraphStyle("mono",
            fontName="Courier", fontSize=9, leading=13,
            textColor=INK),
        "caption": ParagraphStyle("caption",
            fontName="Helvetica", fontSize=8, leading=11,
            textColor=colors.HexColor("#666666"), spaceAfter=4),
        "bullet": ParagraphStyle("bullet",
            fontName="Helvetica", fontSize=10, leading=15,
            textColor=INK, leftIndent=14, spaceAfter=3,
            bulletIndent=0),
        "tag": ParagraphStyle("tag",
            fontName="Helvetica-Bold", fontSize=8, leading=10,
            textColor=CREAM, alignment=TA_CENTER),
        "quote": ParagraphStyle("quote",
            fontName="Helvetica-Oblique", fontSize=13, leading=18,
            textColor=INK, alignment=TA_CENTER,
            spaceBefore=8, spaceAfter=8),
    }

S = make_styles()

# ── Custom flowables ─────────────────────────────────────────────────────────
class ColorRect(Flowable):
    """A solid colored rectangle, full page width."""
    def __init__(self, height, fill_color, border_color=None):
        super().__init__()
        self.rect_height = height
        self.fill_color = fill_color
        self.border_color = border_color

    def wrap(self, avail_w, avail_h):
        self.width = avail_w
        return avail_w, self.rect_height

    def draw(self):
        c = self.canv
        c.setFillColor(self.fill_color)
        c.rect(0, 0, self.width, self.rect_height, stroke=0, fill=1)
        if self.border_color:
            c.setStrokeColor(self.border_color)
            c.setLineWidth(3)
            c.rect(0, 0, self.width, self.rect_height, stroke=1, fill=0)


class InkHRule(Flowable):
    """A thick ink-colored horizontal rule."""
    def __init__(self, thickness=3):
        super().__init__()
        self.thickness = thickness

    def wrap(self, avail_w, avail_h):
        self.width = avail_w
        return avail_w, self.thickness + 4

    def draw(self):
        c = self.canv
        c.setStrokeColor(INK)
        c.setLineWidth(self.thickness)
        c.line(0, self.thickness / 2, self.width, self.thickness / 2)


class ColorSwatch(Flowable):
    """A single color swatch: rect + label below."""
    def __init__(self, hex_val, name, role, w=90, h=60):
        super().__init__()
        self.hex_val = hex_val
        self.name = name
        self.role = role
        self.sw = w
        self.sh = h

    def wrap(self, aw, ah):
        return self.sw, self.sh + 30

    def draw(self):
        c = self.canv
        fill = colors.HexColor(self.hex_val)
        c.setFillColor(fill)
        c.setStrokeColor(INK)
        c.setLineWidth(2)
        c.rect(0, 30, self.sw, self.sh, stroke=1, fill=1)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(0, 18, self.name)
        c.setFont("Helvetica", 7)
        c.drawString(0, 8, self.hex_val)
        c.setFont("Helvetica-Oblique", 7)
        c.drawString(0, 0, self.role)


class HalftoneBox(Flowable):
    """Colored box with halftone dot texture and white label."""
    def __init__(self, color, label, w=130, h=70):
        super().__init__()
        self.bg = color
        self.label = label
        self.bw = w
        self.bh = h

    def wrap(self, aw, ah):
        return self.bw, self.bh

    def draw(self):
        c = self.canv
        # fill
        c.setFillColor(self.bg)
        c.setStrokeColor(INK)
        c.setLineWidth(2.5)
        c.rect(0, 0, self.bw, self.bh, stroke=1, fill=1)
        # halftone dots
        c.setFillColor(colors.Color(0, 0, 0, 0.12))
        dot_spacing = 8
        for x in range(0, self.bw + dot_spacing, dot_spacing):
            for y in range(0, self.bh + dot_spacing, dot_spacing):
                c.circle(x, y, 1.2, stroke=0, fill=1)
        # hard shadow
        c.setFillColor(INK)
        c.rect(4, -4, self.bw, self.bh, stroke=0, fill=1)
        c.setFillColor(self.bg)
        c.setStrokeColor(INK)
        c.rect(0, 0, self.bw, self.bh, stroke=1, fill=1)
        c.setFillColor(colors.Color(0, 0, 0, 0.12))
        for x in range(0, self.bw + dot_spacing, dot_spacing):
            for y in range(0, self.bh + dot_spacing, dot_spacing):
                c.circle(x, y, 1.2, stroke=0, fill=1)
        # label
        c.setFillColor(CREAM)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(self.bw / 2, self.bh / 2 - 4, self.label)


# ── Page template ─────────────────────────────────────────────────────────────
class PageTemplate:
    def __init__(self):
        self.page_num = 0

    def on_page(self, canv, doc):
        self.page_num += 1
        w, h = letter
        # Cream background
        canv.setFillColor(CREAM)
        canv.rect(0, 0, w, h, stroke=0, fill=1)
        # Halftone texture
        canv.setFillColor(colors.HexColor("#d8c9a8"))
        for x in range(0, int(w) + 7, 7):
            for y in range(0, int(h) + 7, 7):
                canv.circle(x, y, 0.9, stroke=0, fill=1)
        # Footer bar
        canv.setFillColor(INK)
        canv.rect(0, 0, w, 28, stroke=0, fill=1)
        canv.setFillColor(CREAM)
        canv.setFont("Helvetica-Bold", 8)
        canv.drawString(0.5 * inch, 10, "THE DUST BUNNY  ·  BRAND GUIDE")
        canv.setFont("Helvetica", 8)
        canv.drawRightString(w - 0.5 * inch, 10, f"the-dustbunny.com  ·  pg {self.page_num}")


# ── Cover page ───────────────────────────────────────────────────────────────
def build_cover(elements):
    # Red header bar
    elements.append(Spacer(1, 0.1 * inch))

    # Mascot image centered
    if os.path.exists(MASCOT_PNG):
        img = RLImage(MASCOT_PNG, width=2.2 * inch, height=2.7 * inch)
        img.hAlign = "CENTER"
        elements.append(img)
    elements.append(Spacer(1, 0.15 * inch))

    # Cover text on ink background
    cover_data = [
        [Paragraph("THE DUST BUNNY", S["cover_title"])],
        [Paragraph("BRAND GUIDE", S["cover_sub"])],
        [Paragraph("the-dustbunny.com", S["cover_url"])],
    ]
    cover_table = Table(cover_data, colWidths=[6.5 * inch])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), INK),
        ("LEFTPADDING",  (0,0), (-1,-1), 30),
        ("RIGHTPADDING", (0,0), (-1,-1), 30),
        ("TOPPADDING",   (0,0), (0,0),  20),
        ("BOTTOMPADDING",(0,-1),(-1,-1),20),
        ("TOPPADDING",   (0,1), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0), (0,0),  4),
        ("BOTTOMPADDING",(0,1), (0,1),  4),
    ]))
    elements.append(cover_table)
    elements.append(Spacer(1, 0.25 * inch))

    # Tagline burst
    tagline_data = [[Paragraph(
        '<font color="#1a1714"><b>Don\'t get left in the digital dust.</b></font>',
        ParagraphStyle("tl", fontName="Helvetica-Bold", fontSize=13,
                       leading=16, alignment=TA_CENTER)
    )]]
    tagline_table = Table(tagline_data, colWidths=[6.5 * inch])
    tagline_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), MUSTARD),
        ("INNERGRID",    (0,0), (-1,-1), 2, INK),
        ("BOX",          (0,0), (-1,-1), 3, INK),
        ("TOPPADDING",   (0,0), (-1,-1), 12),
        ("BOTTOMPADDING",(0,0), (-1,-1), 12),
    ]))
    elements.append(tagline_table)
    elements.append(Spacer(1, 0.2 * inch))

    # One-line purpose
    elements.append(Paragraph(
        "This guide covers the brand's identity, visual language, voice, and social media usage — "
        "everything needed to create on-brand graphics and content.",
        S["body"]
    ))


# ── Section helpers ────────────────────────────────────────────────────────────
def section_header(elements, label, title, accent=COMIC_RED):
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(InkHRule(3))
    elements.append(Spacer(1, 6))
    # Label chip
    label_data = [[Paragraph(label, S["section_label"])]]
    label_t = Table(label_data, colWidths=[2 * inch])
    label_t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), accent),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ]))
    elements.append(label_t)
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(title, S["h1"]))
    elements.append(Spacer(1, 4))


def bullet(text, bold_prefix=None):
    if bold_prefix:
        return Paragraph(f"<b>{bold_prefix}</b> {text}", S["bullet"], bulletText="•")
    return Paragraph(text, S["bullet"], bulletText="•")


# ── Content sections ─────────────────────────────────────────────────────────

def build_brand_overview(elements):
    section_header(elements, "01  ·  OVERVIEW", "Brand at a Glance", COMIC_RED)
    elements.append(Paragraph(
        "The Dust Bunny is a freelance web development studio targeting small businesses — "
        "specifically those with a site they hate, no site at all, or a digital footprint that's "
        "invisible to search engines. The brand delivers big-tech-quality custom-coded sites with "
        "SEO and AI SEO baked in from day one.",
        S["body"]
    ))
    elements.append(Spacer(1, 0.1 * inch))

    overview_rows = [
        ["Brand Name",    "The Dust Bunny"],
        ["Website",       "the-dustbunny.com"],
        ["Owner",         "Josh Vogel — Founder · Builder · Bunny-in-Chief"],
        ["Target Client", "Small businesses: no site, bad site, or invisible site"],
        ["Core Promise",  "Custom-built sites with SEO + AI SEO — traffic that converts"],
        ["Tagline",       '"Don\'t get left in the dust."'],
        ["CTAs",          '"Clean My Site\'s Dust Bunnies" · "Sweep It"'],
    ]
    t = Table(overview_rows, colWidths=[1.6 * inch, 4.9 * inch])
    t.setStyle(TableStyle([
        ("FONTNAME",     (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",     (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",     (0,0), (-1,-1), 9),
        ("LEADING",      (0,0), (-1,-1), 13),
        ("VALIGN",       (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [NEWSPRINT, CREAM]),
        ("BOX",          (0,0), (-1,-1), 2, INK),
        ("INNERGRID",    (0,0), (-1,-1), 0.5, PAPER_SHADOW),
    ]))
    elements.append(t)


def build_visual_language(elements):
    section_header(elements, "02  ·  VISUAL LANGUAGE", "Design Style", TEAL)
    elements.append(Paragraph(
        "The visual language is <b>vintage comic book / Americana</b> — think mid-century "
        "newsprint, Ben-Day halftone dots, bold ink outlines, hard offset drop shadows, "
        "action starbursts, and comic-stamp stickers. Bold, tactile, and unapologetically fun.",
        S["body"]
    ))
    elements.append(Spacer(1, 6))
    keywords = [
        ("Ink outlines", "4px solid black borders on all elements — nothing floats without a frame"),
        ("Hard drop shadows", "Flat 6px offset box-shadow in ink — no blur, no gradients"),
        ("Ben-Day halftone", "Dot-pattern texture overlaid on colored fills (8px grid)"),
        ("Starbursts / Bursts", "Action-style starburst shapes for badges, prices, CTAs"),
        ("Comic panels", "Content cards use cream fills + thick ink borders like comic panels"),
        ("Action lines", "Radial speed-line background used on the hero"),
        ("Sticker hover", "Elements nudge + slightly rotate on hover with bigger shadow"),
        ("Speech bubbles", "Pointed speech bubble tail on highlight quotes"),
        ("-1°/+1° tilts", "Slight rotation on labels and stickers for hand-placed feel"),
    ]
    for kw, desc in keywords:
        elements.append(bullet(desc, f"{kw}:"))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(
        "<b>What to AVOID:</b> gradients, rounded pill buttons, drop shadows with blur, "
        "soft pastels, geometric sans-serif minimalism, or anything that looks like a SaaS "
        "startup. The brand is deliberately tactile and printed-not-digital in feel.",
        ParagraphStyle("warn", fontName="Helvetica", fontSize=9, leading=13,
                       textColor=INK, leftIndent=0, spaceAfter=4,
                       backColor=colors.HexColor("#fdf0c0"), borderPad=8)
    ))


def build_color_palette(elements):
    section_header(elements, "03  ·  COLOR", "Palette", MUSTARD)
    elements.append(Paragraph(
        "Six core colors. Cream is the base — everything else is used as accent, panel fill, "
        "or halftone fill. Ink is always the border/outline color.",
        S["body"]
    ))
    elements.append(Spacer(1, 0.1 * inch))

    swatches = [
        ("#f4ead2", "Cream",       "Page background / base"),
        ("#1a1714", "Ink",         "Borders · text · shadows"),
        ("#e23b2e", "Comic Red",   "CTAs · hero accent · badges"),
        ("#f2b93b", "Mustard",     "Starbursts · highlights · selection"),
        ("#2a9d9b", "Teal",        "Service tags · secondary accent"),
        ("#c9b79c", "Dust",        "Mascot · muted fills · footer"),
    ]
    row = []
    for hex_val, name, role in swatches:
        row.append(ColorSwatch(hex_val, name, role, w=85, h=55))
    swatch_table = Table([row], colWidths=[85] * 6,
                         rowHeights=[85])
    swatch_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING",   (0,0), (-1,-1), 0),
        ("BOTTOMPADDING",(0,0), (-1,-1), 0),
    ]))
    elements.append(swatch_table)
    elements.append(Spacer(1, 0.1 * inch))

    # Usage rules
    rules = [
        ("Cream #f4ead2",    "Page background, card interiors, text on dark fills"),
        ("Ink #1a1714",      "ALL borders, ALL drop shadows, body text, headlines"),
        ("Comic Red #e23b2e","Primary CTA buttons, starburst fills, hero headline accent"),
        ("Mustard #f2b93b",  "Starburst / burst fills, section label backgrounds, badges"),
        ("Teal #2a9d9b",     "Secondary section labels, service card fills, hero glow"),
        ("Dust #c9b79c",     "Mascot body color, muted panel backgrounds, footer"),
    ]
    rt = Table([["Color", "Use"]] + rules, colWidths=[1.6 * inch, 4.9 * inch])
    rt.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",      (1,1), (1,-1), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("LEADING",       (0,0), (-1,-1), 12),
        ("BACKGROUND",    (0,0), (-1,0), INK),
        ("TEXTCOLOR",     (0,0), (-1,0), CREAM),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [NEWSPRINT, CREAM]),
        ("BOX",           (0,0), (-1,-1), 2, INK),
        ("INNERGRID",     (0,0), (-1,-1), 0.5, PAPER_SHADOW),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]))
    elements.append(rt)


def build_typography(elements):
    section_header(elements, "04  ·  TYPOGRAPHY", "Fonts", COMIC_RED)
    fonts = [
        ("Anton",         "Headlines / Impact",   "Google Fonts",
         "H1, H2, H3 — all-caps, tight leading (0.95), minimal letter-spacing"),
        ("Bungee",        "Display / Logo",        "Google Fonts",
         "Buttons, nav items, stickers, badges — uppercase, tracking-wide"),
        ("Space Grotesk", "Body",                  "Google Fonts",
         "Body copy, captions, form labels, small UI text"),
    ]
    for name, role, source, usage in fonts:
        row_data = [
            [Paragraph(f"<b>{name}</b>", S["h3"]),
             Paragraph(f"<b>Role:</b> {role}  ·  <b>Source:</b> {source}", S["body_sm"])],
            [Paragraph("", S["body_sm"]),
             Paragraph(usage, S["body_sm"])],
        ]
        ft = Table(row_data, colWidths=[1.6 * inch, 4.9 * inch])
        ft.setStyle(TableStyle([
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ("TOPPADDING",   (0,0), (-1,-1), 5),
            ("BOTTOMPADDING",(0,0), (-1,-1), 3),
            ("LEFTPADDING",  (0,0), (-1,-1), 6),
            ("BACKGROUND",   (0,0), (-1,-1), NEWSPRINT),
            ("BOX",          (0,0), (-1,-1), 2, INK),
            ("SPAN",         (0,0), (0,1)),
        ]))
        elements.append(ft)
        elements.append(Spacer(1, 6))

    elements.append(Spacer(1, 4))
    elements.append(Paragraph(
        "<b>Rules:</b> Headlines are ALWAYS all-caps. Never use sentence-case on a button "
        "or badge. Bungee is reserved for UI labels — don't use it for body copy. "
        "Space Grotesk at weight 400–700.",
        S["body_sm"]
    ))


def build_mascot(elements):
    section_header(elements, "05  ·  MASCOT", "The Dust Bunny", TEAL)
    elements.append(Paragraph(
        "The mascot is the brand's most recognizable visual asset. "
        "It is a fuzzy, spiky dust ball with long bunny ears, big cartoon eyes, "
        "rosy cheeks, and floating dust-puff motes around it. "
        "The mascot appears in the hero, page-transition animation, scroll cameos, "
        "loading screen, and as a corner peek-a-boo element.",
        S["body"]
    ))
    elements.append(Spacer(1, 8))

    col_text = [
        [Paragraph("<b>Colors used</b>", S["h3"])],
        [bullet("Body: Dust #c9b79c with halftone fuzz overlay")],
        [bullet("Inner ears: Pinkish #e0a89f")],
        [bullet("Outline: Ink #1a1714, 6px stroke")],
        [bullet("Eyes: Ink fill with Cream highlights")],
        [bullet("Cheeks: Comic Red at 30% opacity")],
        [bullet("Dust puffs: Dust color, 55% opacity")],
        [Spacer(1, 8)],
        [Paragraph("<b>Usage rules</b>", S["h3"])],
        [bullet("Never recolor the mascot's body away from Dust/Cream tones")],
        [bullet("Always keep the ink outline — never make it outline-free")],
        [bullet("Minimum display size: 80px / 1 inch wide")],
        [bullet("On dark backgrounds use as-is (ink outline reads fine)")],
        [bullet("On colored backgrounds use the transparent-bg PNG version")],
    ]

    if os.path.exists(MASCOT_PNG):
        img = RLImage(MASCOT_PNG, width=1.8 * inch, height=2.2 * inch)
        mascot_cell = img
    else:
        mascot_cell = Paragraph("[mascot image]", S["body"])

    layout = Table(
        [[mascot_cell, [p for row in col_text for p in row]]],
        colWidths=[2.1 * inch, 4.4 * inch]
    )
    layout.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING",   (0,0), (-1,-1), 0),
        ("BOTTOMPADDING",(0,0), (-1,-1), 0),
    ]))
    elements.append(layout)


def build_voice(elements):
    section_header(elements, "06  ·  VOICE & TONE", "How We Sound", MUSTARD)
    elements.append(Paragraph(
        "The Dust Bunny sounds like a sharp contractor friend — direct, confident, "
        "and a little bit funny. Not corporate. Not bro-y. Honest about what we do and "
        "don't do. The humor is deadpan Americana, not startup-quirky.",
        S["body"]
    ))
    elements.append(Spacer(1, 8))

    attrs = [
        ("Direct",      "Get to the point. No filler. Every sentence earns its spot."),
        ("Confident",   "We know what we're doing. No hedging, no apologies."),
        ("Conversational", "Talks like a real person, not a landing page template."),
        ("Playful",     "Dry humor is welcome. Exclamation-point spam is not."),
        ("Grounded",    "Roots in the South, serving small business — not Silicon Valley."),
    ]
    for trait, desc in attrs:
        elements.append(KeepTogether([
            Paragraph(f"<b>{trait}</b>", S["h3"]),
            Paragraph(desc, S["body_sm"]),
        ]))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>Examples — actual brand copy:</b>", S["h3"]))
    quotes = [
        '"Bad site? No site? Same problem."',
        '"Don\'t get left in the dust."',
        '"From dusty to dominant."',
        '"Clean My Site\'s Dust Bunnies"',
        '"Sweep It"  (the form submit CTA)',
        '"Free Sweep!" (the contact section badge)',
        '"We dig into your current setup — bad site, no site, or somewhere in between."',
    ]
    for q in quotes:
        elements.append(bullet(q))

    elements.append(Spacer(1, 8))
    dos_donts = [
        ["DO say",   "DON'T say"],
        ["We build it",           "We craft bespoke digital experiences"],
        ["Your site's invisible", "Your online presence lacks visibility"],
        ["Traffic that converts", "Cutting-edge conversion-optimized solutions"],
        ["3–5 days turnaround",   "Quick turnaround (be specific)"],
        ["We watch the numbers",  "We leverage data-driven insights"],
    ]
    ddt = Table(dos_donts, colWidths=[3.25 * inch, 3.25 * inch])
    ddt.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("LEADING",       (0,0), (-1,-1), 13),
        ("BACKGROUND",    (0,0), (0,0),  TEAL),
        ("BACKGROUND",    (1,0), (1,0),  COMIC_RED),
        ("TEXTCOLOR",     (0,0), (-1,0), CREAM),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [NEWSPRINT, CREAM]),
        ("BOX",           (0,0), (-1,-1), 2, INK),
        ("INNERGRID",     (0,0), (-1,-1), 0.5, PAPER_SHADOW),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elements.append(ddt)


def build_services(elements):
    section_header(elements, "07  ·  SERVICES", "What We Sell", COMIC_RED)
    services = [
        ("01", COMIC_RED,  "Digital Footprint",
         "Fast, modern site + Google Business, maps, and local listings. "
         "Get found everywhere it counts."),
        ("02", TEAL,       "SEO That Sticks",
         "Real keyword research, clean technical SEO, and content that ranks. "
         "We chase the searches your customers actually type."),
        ("03", MUSTARD,    "AI SEO",
         "When people ask ChatGPT, Gemini, or Google's AI for a recommendation, "
         "we make sure your business is the answer."),
        ("04", INK,        "Traffic That Converts",
         "Pretty doesn't pay the bills. Pages tuned to turn visitors into "
         "calls, bookings, and paying customers."),
    ]
    rows = [[
        Paragraph(f'<font color="#f4ead2"><b>{n}</b></font>', S["tag"]),
        Paragraph(f"<b>{title}</b>", S["h3"]),
        Paragraph(desc, S["body_sm"]),
    ] for n, color, title, desc in services]

    colors_list = [s[1] for s in services]
    st = Table(rows, colWidths=[0.4 * inch, 1.7 * inch, 4.4 * inch])
    style_cmds = [
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("BOX",           (0,0), (-1,-1), 2, INK),
        ("INNERGRID",     (0,0), (-1,-1), 0.5, PAPER_SHADOW),
    ]
    for i, c in enumerate(colors_list):
        style_cmds.append(("BACKGROUND", (0, i), (0, i), c))
        style_cmds.append(("ROWBACKGROUNDS", (1, i), (-1, i), [NEWSPRINT if i % 2 == 0 else CREAM]))
    st.setStyle(TableStyle(style_cmds))
    elements.append(st)


def build_social_guide(elements):
    section_header(elements, "08  ·  SOCIAL MEDIA", "Graphics Guide", TEAL)
    elements.append(Paragraph(
        "Use this section as the primary reference when generating social media graphics. "
        "Every post should feel like it could be a panel from a vintage comic strip.",
        S["body"]
    ))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph("Formats & Sizes", S["h2"]))
    sizes = [
        ["Platform", "Format", "Size",          "Notes"],
        ["Instagram Feed",   "Square",    "1080 × 1080 px", "Core format — always have this"],
        ["Instagram Story",  "Portrait",  "1080 × 1920 px", "Use mascot-9x16.jpg as base"],
        ["Instagram Reel",   "Portrait",  "1080 × 1920 px", "Same as Story"],
        ["LinkedIn",         "Landscape", "1200 × 627 px",  "More formal tone, less playful"],
        ["Facebook",         "Square",    "1080 × 1080 px", "Same as Instagram"],
        ["Twitter/X",        "Landscape", "1600 × 900 px",  "Bold headline-first"],
        ["TikTok",           "Portrait",  "1080 × 1920 px", "Mascot + motion-friendly"],
    ]
    st = Table(sizes, colWidths=[1.3*inch, 0.9*inch, 1.3*inch, 3.0*inch])
    st.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("LEADING",       (0,0), (-1,-1), 12),
        ("BACKGROUND",    (0,0), (-1,0),  INK),
        ("TEXTCOLOR",     (0,0), (-1,0),  CREAM),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [NEWSPRINT, CREAM]),
        ("BOX",           (0,0), (-1,-1), 2, INK),
        ("INNERGRID",     (0,0), (-1,-1), 0.5, PAPER_SHADOW),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
    ]))
    elements.append(st)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Graphic Templates — What to Include", S["h2"]))
    templates = [
        ("Stat Card",
         "Cream or Ink background · halftone dot texture · "
         "big Anton number in Mustard · small Space Grotesk body text in Cream · "
         "ink border + 6px hard shadow · small mascot or dust puff in corner"),
        ("Service Highlight",
         "Halftone fill (Red/Teal/Mustard/Ink) · "
         "numbered tag in top-left corner · "
         "Anton service title all-caps · 2–3 line description · "
         "Dust Bunny mascot peeking from one edge"),
        ("Tip / Quote",
         "Cream panel with ink border · "
         "Mustard starburst badge in corner with 'TIP' or 'FREE' · "
         "Bungee quote text · mascot with speech bubble tail · "
         "slight -1deg or +2deg rotation on the panel"),
        ("Client Win / Case Study",
         "Work card flip style: halftone color fill front, screenshot back · "
         "business name in Anton · 1-line result in Space Grotesk · "
         "'Visit site →' in Comic Red"),
        ("Call to Action",
         "Full bleed halftone-red or halftone-ink · "
         "Anton headline 'DON\'T GET LEFT IN THE DUST' · "
         "Cream panel button 'CLEAN MY SITE\'S DUST BUNNIES' with ink border + shadow · "
         "mascot centered or in corner"),
    ]
    for name, desc in templates:
        elements.append(KeepTogether([
            Paragraph(f"<b>{name}</b>", S["h3"]),
            Paragraph(desc, S["body_sm"]),
            Spacer(1, 4),
        ]))

    elements.append(Spacer(1, 6))
    elements.append(Paragraph("Caption Voice", S["h2"]))
    captions = [
        ("Stat card",   "Lead with the number. 1 sentence of context. CTA: 'Link in bio.'"),
        ("Tips",        "Short, punchy headline. 2–3 lines max. End with a question or CTA."),
        ("Client win",  "'[Business] needed X. We built Y. Now they're Z.' Keep it concrete."),
        ("CTA post",    "One clear action. Hashtags in first comment, not the caption."),
    ]
    for fmt, rule in captions:
        elements.append(bullet(rule, f"{fmt}:"))

    elements.append(Spacer(1, 8))
    elements.append(Paragraph("Hashtag Bank", S["h2"]))
    elements.append(Paragraph(
        "#smallbusiness #websitedesign #SEO #localSEO #AISEO #webdev #smallbiz "
        "#floridabusiness #tampasmallbiz #customwebsite #digitalmarketing "
        "#GetFoundOnline #TheDustBunny #DontGetLeftInTheDust",
        S["body_sm"]
    ))


def build_assets(elements):
    section_header(elements, "09  ·  ASSET FILES", "Ready-to-Use Files", MUSTARD)
    assets = [
        ["File",                          "Format", "Use"],
        ["public/mascot/mascot.png",      "PNG 1040px, transparent bg",
         "Overlays on any colored background"],
        ["public/mascot/mascot.jpg",      "JPG 1040px, cream bg, 1:1 square",
         "Feed posts, profile thumbnails"],
        ["public/mascot/mascot-9x16.jpg", "JPG 1080×1920, cream bg",
         "Stories, Reels, TikTok"],
        ["public/mascot/mascot.svg",      "SVG vector",
         "Print, large-format, scalable"],
        ["public/favicon.svg",            "SVG vector",
         "Favicon / app icon reference"],
    ]
    at = Table(assets, colWidths=[2.4*inch, 1.9*inch, 2.2*inch])
    at.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("LEADING",       (0,0), (-1,-1), 12),
        ("FONTNAME",      (0,1), (0,-1),  "Courier"),
        ("BACKGROUND",    (0,0), (-1,0),  INK),
        ("TEXTCOLOR",     (0,0), (-1,0),  CREAM),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),  [NEWSPRINT, CREAM]),
        ("BOX",           (0,0), (-1,-1), 2, INK),
        ("INNERGRID",     (0,0), (-1,-1), 0.5, PAPER_SHADOW),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 5),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    elements.append(at)


def build_cheatsheet(elements):
    section_header(elements, "10  ·  QUICK REFERENCE", "Claude Prompt Cheat Sheet", COMIC_RED)
    elements.append(Paragraph(
        "Paste any of these prompts directly into Claude when creating social media graphics:",
        S["body"]
    ))
    elements.append(Spacer(1, 6))
    prompts = [
        ("Stat card (IG square)",
         "Create a 1080×1080 social media graphic in The Dust Bunny brand style. "
         "Vintage comic / Americana aesthetic. Cream (#f4ead2) background with halftone dot texture. "
         "Thick ink (#1a1714) border, 6px hard drop shadow. "
         "Big Anton-style number in Mustard (#f2b93b). "
         "Body copy in Space Grotesk. "
         "Small dust-bunny character in corner. "
         "Stat: [INSERT STAT HERE]"),
        ("Story / Reel (9:16)",
         "Create a 1080×1920 vertical social graphic for The Dust Bunny. "
         "Vintage comic book style with halftone red fill (#e23b2e + dot texture). "
         "Cream panel in center with ink border and 6px offset shadow. "
         "Anton headline all-caps. Mascot (fuzzy spiky bunny with long ears) bottom third. "
         "CTA button: 'CLEAN MY SITE'S DUST BUNNIES' in Bungee, cream on ink."),
        ("Service highlight",
         "Create a social graphic for The Dust Bunny web studio. "
         "Halftone teal (#2a9d9b) background. "
         "Number tag '02' in top-left corner (cream on teal, ink border). "
         "Anton headline: 'SEO THAT STICKS'. "
         "Short description in Space Grotesk on cream panel. "
         "Comic-style ink outlines on all elements. 6px hard drop shadow."),
        ("Call to action",
         "Design a CTA social graphic for The Dust Bunny web studio. "
         "Full-bleed halftone ink (#1a1714) background. "
         "Large Anton headline in cream: 'DON'T GET LEFT IN THE DUST.' "
         "Mustard starburst badge: 'FREE SWEEP'. "
         "Cream button with ink border: 'CLEAN MY SITE'S DUST BUNNIES →'. "
         "Mascot peeking from bottom edge."),
    ]
    for title, prompt in prompts:
        elements.append(Paragraph(f"<b>{title}</b>", S["h3"]))
        # Prompt box
        prompt_data = [[Paragraph(prompt, ParagraphStyle("pt",
            fontName="Courier", fontSize=8, leading=12, textColor=INK))]]
        pt = Table(prompt_data, colWidths=[6.5 * inch])
        pt.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), NEWSPRINT),
            ("BOX",          (0,0), (-1,-1), 1.5, DUST),
            ("LEFTPADDING",  (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING",   (0,0), (-1,-1), 6),
            ("BOTTOMPADDING",(0,0), (-1,-1), 6),
        ]))
        elements.append(pt)
        elements.append(Spacer(1, 8))


# ── Build PDF ─────────────────────────────────────────────────────────────────
def build():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    tmpl = PageTemplate()

    doc = SimpleDocTemplate(
        OUT_PATH,
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.55 * inch,
        title="The Dust Bunny — Brand Guide",
        author="Josh Vogel / The Dust Bunny",
        subject="Brand Guide for Social Media Graphics",
    )

    elements = []
    build_cover(elements)
    build_brand_overview(elements)
    build_visual_language(elements)
    build_color_palette(elements)
    build_typography(elements)
    build_mascot(elements)
    build_voice(elements)
    build_services(elements)
    build_social_guide(elements)
    build_assets(elements)
    build_cheatsheet(elements)

    doc.build(elements, onFirstPage=tmpl.on_page, onLaterPages=tmpl.on_page)
    print(f"✔  Brand guide written → {OUT_PATH}")


if __name__ == "__main__":
    build()
