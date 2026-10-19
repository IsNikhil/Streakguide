"""
make_pdf.py
Builds guide.pdf from the guide text below, using the ReportLab library.

How to run:   python3 make_pdf.py
Needs:        pip install reportlab
"""

import os
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (Flowable, Image, KeepTogether, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)


# =====================================================================
# 1. THE GUIDE TEXT (edit the words here)
#    Links (https://...) and mail.google.com become clickable by themselves.
# =====================================================================

STORE_URL = "https://chromewebstore.google.com/detail/streak-crm-for-gmail/pnnfemgpilpdaojpnkjdgfgbnnjojfik"

TITLE = "How to Know If Your Email Was Opened (Streak for Gmail)"

BYLINE = "Nikhil Shah  \u00b7  ENGL3220  \u00b7  Fall 2026"

INTRO = ("This guide shows you how to see when someone opens your Gmail message, "
         "like a read receipt. You will use a free Chrome extension called Streak. "
         "It takes about 10 minutes.")

BEFORE_YOU_START = {
    "lead": "You need four things:",
    "needs": [
        "A Gmail account",
        "Google Chrome on a laptop or desktop computer",
        "About 10 minutes",
        "A second email address to send a test email to (your school email works)",
    ],
    "how_it_works": ("Streak adds a tiny, hidden picture to the email you send. When the "
                     "reader opens the email, that picture loads. Streak sees this and "
                     "shows you a \"view.\""),
}

# Each part has a title and a list of steps.
# A step can have an "image" (file name inside the images folder) and a "caption".
# It can also have a second picture: "image2" and "caption2".
PARTS = [
    {
        "title": "Part 1: Install Streak",
        "steps": [
            {"title": "Open the Streak page.",
             "text": "Open Chrome. Click this link: " + STORE_URL + " . It opens the Streak page in the Chrome Web Store."},
            {"title": "Add Streak to Chrome.",
             "text": "Click the blue \"Add to Chrome\" button.",
             "image": "chrome-store-add-to-chrome.png",
             "caption": "The blue \"Add to Chrome\" button on the Streak page."},
            {"title": "Confirm.",
             "text": "A small box pops up near the top of Chrome. It asks if you want to add Streak. Click \"Add extension\".",
             "image": "add-extension-popup.png",
             "caption": "The pop up box. Click \"Add extension\".",
             "image2": "extension-added.png",
             "caption2": "After you click \"Add extension\", Chrome shows this message."},
            {"title": "Open Gmail.",
             "text": "Go to mail.google.com. If Gmail is already open, refresh the page."},
            {"title": "Give Streak permission.",
             "text": "Streak asks for permission to work with your Gmail. Pick your Google account and click \"Allow\".",
             "image": "allow-permission.png",
             "caption": "First, click \"Sign in with Google\". Then pick your account and click \"Allow\"."},
            {"title": "Choose email tracking.",
             "text": "A window opens that says \"Where do you want to start?\" Click \"Email & link tracking\". "
                     "The box gets a blue border when you pick it. Then click \"Next\".",
             "image": "01-streak-welcome-choose-tracking.png",
             "caption": "Pick \"Email & link tracking\", then click \"Next\"."},
        ],
    },
    {
        "title": "Part 2: Turn On Tracking and Send a Test Email",
        "steps": [
            {"title": "Start a new email.",
             "text": "In Gmail, click \"Compose\" in the top left."},
            {"title": "Write the email.",
             "text": "Type your second email address in the \"To\" line. Add a subject and a short message. "
                     "In our test, the subject was \"streak crm\" and the message was \"Find out if my email is opened?\""},
            {"title": "Check the eye icon.",
             "text": "Look at the bottom of the email window, next to the blue Send button. You will see a row of "
                     "small icons. Find the eye. When the eye is orange, tracking is on. If it is not orange, click it once.",
             "image": "02-gmail-compose-tracking-on.png",
             "caption": "The orange eye next to Send means tracking is on."},
            {"title": "Click Send.",
             "text": "Click the blue \"Send\" button. Streak now watches this email."},
        ],
    },
    {
        "title": "Part 3: See If Your Email Was Opened",
        "steps": [
            {"title": "Look at the Tracking panel.",
             "text": "Right after you send, a \"Tracking\" panel shows on the right side of Gmail. It says "
                     "\"No views\" and \"Sent seconds ago.\" This means nobody has opened the email yet.",
             "image": "03-tracking-panel-no-views.png",
             "caption": "Right after sending: \"No views\" yet."},
            {"title": "Open the email as the reader.",
             "text": "Open your second email account and open the message you sent. Wait a few seconds. "
                     "Then go back to the Tracking panel in your first account."},
            {"title": "Read the new result.",
             "text": "The panel now says \"Viewed seconds ago.\" It also shows the total views and total clicks. "
                     "Each row below is one view. Each row shows a device icon, a place, and the time. In our test, "
                     "there were 2 views at 3:11 PM, and the place was \"Unknown location.\"",
             "image": "04-tracking-panel-viewed.png",
             "caption": "After the reader opens it: \"Viewed seconds ago\" with 2 views."},
            {"title": "Check your Sent list.",
             "text": "You can also see the result without opening the email. Go to your Sent folder. A green eye "
                     "shows next to the message once it is opened. The word next to the eye tells you how long ago "
                     "it was opened. Here, it says \"seconds.\"",
             "image": "05-sent-list-eye-icon.png",
             "caption": "The green eye in your Sent list means the email was opened."},
        ],
    },
]

RESULTS = {
    "lead": ("A \"view\" means the hidden picture in your email loaded. It is a good sign that the email "
             "was opened, but it is not perfect. Keep these limits in mind:"),
    "limits": [
        ("The place can be unknown.",
         "In our test, the place was \"Unknown location.\" Email apps like Gmail often hide the reader's real place."),
        ("The number of views is not exact.",
         "One person can make more than one view, for example by opening the email on a phone and a laptop."),
        ("No views does not mean unread.",
         "If the reader blocks images, Streak cannot see the open."),
        ("The free plan shows limited details.",
         "The panel says \"Upgrade for more info\" for extra features. You do not need to pay to follow this guide."),
    ],
    "fair_use": ("Use tracking in a fair way. It works well for school, club, and job emails, such as "
                 "checking if a teacher or a team saw your message."),
}

QUICK_FIXES = [
    ("No Tracking panel", "Refresh Gmail. Then check that the eye icon was orange before you clicked Send."),
    ("Streak is missing in Gmail", "Open chrome://extensions in a new Chrome tab. Make sure the switch next to Streak is on."),
    ("Still \"No views\"", "Wait a minute and refresh. Also make sure you sent the test to a different email address, "
                           "not the same account you sent it from."),
    ("Reader blocks images", "Streak cannot count the view in this case. This is normal."),
]

SOURCE = "Source: Streak CRM for Gmail, Chrome Web Store: " + STORE_URL


# =====================================================================
# 2. COLORS, SIZES, AND TEXT STYLES (the "look" of the PDF)
# =====================================================================

HERE = os.path.dirname(os.path.abspath(__file__))   # the streak-guide folder
IMAGES = os.path.join(HERE, "images")
OUTPUT = os.path.join(HERE, "guide.pdf")

# Fonts: use Helvetica Neue from the Mac and put it inside the PDF.
# If the Mac font is not there (for example on Windows), use the built-in Helvetica.
FONT, BOLD, MEDIUM = "Helvetica", "Helvetica-Bold", "Helvetica-Bold"
MAC_FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
if os.path.exists(MAC_FONT):
    try:
        for name, index in (("Neue", 0), ("Neue-Bold", 1), ("Neue-Italic", 2), ("Neue-Medium", 10)):
            pdfmetrics.registerFont(TTFont(name, MAC_FONT, subfontIndex=index))
        pdfmetrics.registerFontFamily("Neue", normal="Neue", bold="Neue-Bold", italic="Neue-Italic", boldItalic="Neue-Bold")
        FONT, BOLD, MEDIUM = "Neue", "Neue-Bold", "Neue-Medium"
    except Exception:
        pass   # keep the built-in Helvetica

BLUE = colors.HexColor("#0066cc")       # links and step labels (same as the website)
ORANGE = colors.HexColor("#f5821f")     # accent color (the Streak eye)
TEXT = colors.HexColor("#1d1d1f")       # near black
MUTED = colors.HexColor("#6e6e73")      # gray for small text
TILE = colors.HexColor("#f5f5f7")       # light gray boxes
LINE = colors.HexColor("#d2d2d7")

MARGIN = 0.85 * inch
CONTENT_WIDTH = letter[0] - 2 * MARGIN - 12   # usable width (the page frame keeps 6pt padding on each side)
MAX_IMAGE_HEIGHT = 3.4 * inch            # keeps tall screenshots from filling a whole page
RETINA_SCALE = 0.375                     # Mac screenshots have 2 pixels per screen dot: 0.5 x 0.75 points

# Text styles: font, size, spacing, color
body = ParagraphStyle("body", fontName=FONT, fontSize=11.5, leading=16.5, textColor=TEXT, spaceAfter=6)
title_style = ParagraphStyle("title", parent=body, fontName=BOLD, fontSize=27, leading=31, spaceAfter=8)
byline_style = ParagraphStyle("byline", parent=body, fontName=MEDIUM, fontSize=10.5, textColor=MUTED, spaceAfter=14)
intro_style = ParagraphStyle("intro", parent=body, fontSize=12.5, leading=18, textColor=MUTED, spaceAfter=14)
h1 = ParagraphStyle("h1", parent=body, fontName=BOLD, fontSize=19, leading=24, spaceBefore=18, spaceAfter=6)
step_title = ParagraphStyle("step", parent=body, fontName=BOLD, fontSize=12.5, leading=17,
                            spaceBefore=10, spaceAfter=3)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=16, bulletIndent=4, spaceAfter=3)
caption = ParagraphStyle("caption", parent=body, fontName=FONT, fontSize=10, leading=13,
                         textColor=MUTED, alignment=TA_CENTER, spaceBefore=4, spaceAfter=8)
card_title = ParagraphStyle("cardtitle", parent=body, fontName=BOLD, fontSize=11.5, spaceAfter=3)
card_text = ParagraphStyle("cardtext", parent=body, fontSize=11, leading=15, textColor=MUTED, spaceAfter=0)
small = ParagraphStyle("small", parent=body, fontSize=10, leading=14, textColor=MUTED)


# =====================================================================
# 3. HELPERS (small tools that turn text and pictures into PDF pieces)
# =====================================================================

LINK_PATTERN = re.compile(r"(https?://\S+|mail\.google\.com)")


def rich(text):
    """Make text safe for ReportLab and turn web addresses into clickable blue links."""
    parts = LINK_PATTERN.split(text)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:   # this piece is a link
            href = part if part.startswith("http") else "https://" + part
            out.append('<a href="%s" color="#0066cc"><u>%s</u></a>' % (escape(href), escape(part)))
        else:
            out.append(escape(part))
    # "Click this link: URL ." looks odd in print, so remove the space before the final period
    return "".join(out).replace("</u></a> .", "</u></a>.")


class PhotoComingSoon(Flowable):
    """A light gray box that stands in for a screenshot that is not in the images folder yet."""

    def __init__(self, file_name, width=CONTENT_WIDTH, height=1.4 * inch):
        super().__init__()
        self.file_name, self.width, self.height = file_name, width, height

    def draw(self):
        c = self.canv
        c.setFillColor(TILE)
        c.setStrokeColor(colors.HexColor("#aeaeb2"))
        c.setDash(4, 3)
        c.roundRect(0, 0, self.width, self.height, 10, fill=1, stroke=1)
        c.setFillColor(MUTED)
        c.setFont(MEDIUM, 11.5)
        c.drawCentredString(self.width / 2, self.height / 2 - 4, "Photo coming soon: " + self.file_name)


def screenshot(file_name, caption_text):
    """Return the picture (scaled to fit) with a thin border and its caption.
    If the file is missing, return the gray "Photo coming soon" box instead."""
    path = os.path.join(IMAGES, file_name)
    if not os.path.exists(path):
        picture = PhotoComingSoon(file_name)
    else:
        img_w, img_h = ImageReader(path).getSize()
        # shrink to fit the width AND the height, and never draw it bigger than it looked on screen
        scale = min(CONTENT_WIDTH / img_w, MAX_IMAGE_HEIGHT / img_h, RETINA_SCALE)
        img = Image(path, width=img_w * scale, height=img_h * scale)
        picture = Table([[img]], style=TableStyle([                   # a table with one cell = a frame
            ("BOX", (0, 0), (-1, -1), 0.75, LINE),
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
    return [Spacer(1, 4), picture, Paragraph(rich(caption_text), caption)]


def callout(html, background=TILE):
    """A rounded light gray box, used for tips."""
    t = Table([[Paragraph(html, body)]], colWidths=[CONTENT_WIDTH])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), background),
        ("ROUNDEDCORNERS", [10, 10, 10, 10]),
        ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def step_block(number, step, heading=None):
    """One step: a bold title, the text, and maybe a screenshot. Kept together on one page.
    If a heading is given (like "Part 3"), it stays on the same page as this step."""
    pieces = [heading] if heading else []
    pieces += [
        Paragraph('<font color="#0066cc">Step %d</font>   %s' % (number, escape(step["title"])), step_title),
        Paragraph(rich(step["text"]), body),
    ]
    if step.get("image"):
        pieces += screenshot(step["image"], step["caption"])
    if step.get("image2"):   # some steps have a second picture
        pieces += screenshot(step["image2"], step["caption2"])
    return KeepTogether(pieces)


def limit_cards():
    """The 4 limits as a 2 by 2 grid of small cards."""
    cells = [[Paragraph(escape(t), card_title), Paragraph(rich(d), card_text)] for t, d in RESULTS["limits"]]
    grid = Table([cells[0:2], cells[2:4]], colWidths=[CONTENT_WIDTH / 2] * 2)
    grid.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TILE),
        ("ROUNDEDCORNERS", [10, 10, 10, 10]),
        ("LINEAFTER", (0, 0), (0, -1), 6, colors.white),   # white gap between the two columns
        ("LINEBELOW", (0, 0), (-1, 0), 6, colors.white),   # white gap between the two rows
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return grid


# =====================================================================
# 4. PAGE DECORATION: title at the top and "Page X of Y" at the bottom
# =====================================================================

class NumberedCanvas(canvas.Canvas):
    """Waits until all pages exist, so each page can say 'Page 2 of 5'."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_pages = []

    def showPage(self):
        self._saved_pages.append(dict(self.__dict__))   # remember the page, draw it later
        self._startPage()

    def save(self):
        total = len(self._saved_pages)
        for state in self._saved_pages:
            self.__dict__.update(state)
            self.draw_header_and_footer(total)
            super().showPage()
        super().save()

    def draw_header_and_footer(self, total):
        width, height = letter
        # top: the guide title and a thin line
        self.setFont(FONT, 8.5)
        self.setFillColor(MUTED)
        self.drawString(MARGIN, height - 0.55 * inch, TITLE)
        self.drawRightString(width - MARGIN - 12, height - 0.55 * inch, BYLINE)
        self.setStrokeColor(LINE)
        self.setLineWidth(0.6)
        self.line(MARGIN, height - 0.62 * inch, width - MARGIN, height - 0.62 * inch)
        # small orange dot, like the Streak eye
        self.setFillColor(ORANGE)
        self.circle(width - MARGIN - 3, height - 0.52 * inch, 3, fill=1, stroke=0)
        # bottom: page number in the middle
        self.setFont(FONT, 9)
        self.setFillColor(MUTED)
        self.drawCentredString(width / 2, 0.5 * inch, "Page %d of %d" % (self._pageNumber, total))


# =====================================================================
# 5. BUILD THE PDF: put all the pieces in order, then save
# =====================================================================

def build():
    story = []   # "story" = the list of pieces, top to bottom

    # Title and intro
    story.append(Paragraph(escape(TITLE), title_style))
    story.append(Paragraph(escape(BYLINE), byline_style))
    story.append(Paragraph(rich(INTRO), intro_style))

    # Before you start
    story.append(Paragraph("Before You Start", h1))
    story.append(Paragraph(escape(BEFORE_YOU_START["lead"]), body))
    for need in BEFORE_YOU_START["needs"]:
        story.append(Paragraph(rich(need), bullet, bulletText="•"))
    story.append(Spacer(1, 8))
    story.append(callout("<b>How it works:</b> " + rich(BEFORE_YOU_START["how_it_works"])))

    # Parts 1, 2, 3 with their steps
    for part in PARTS:
        heading = Paragraph(escape(part["title"]), h1)
        for number, step in enumerate(part["steps"], start=1):
            story.append(step_block(number, step, heading if number == 1 else None))

    # What the results mean
    story.append(KeepTogether([
        Paragraph("What the Results Mean", h1),
        Paragraph(rich(RESULTS["lead"]), body),
        Spacer(1, 4),
        limit_cards(),
    ]))
    story.append(Spacer(1, 10))
    story.append(callout(rich(RESULTS["fair_use"])))

    # Quick fixes
    fixes = [Paragraph("Quick Fixes", h1)]
    for problem, fix in QUICK_FIXES:
        fixes.append(Paragraph("<b>%s:</b> %s" % (escape(problem), rich(fix)), bullet, bulletText="•"))
    story.append(KeepTogether(fixes))

    # Source
    story.append(Spacer(1, 14))
    story.append(Paragraph(rich(SOURCE), small))

    # Make the document: US Letter, margins, then lay out the story on pages
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=0.95 * inch, bottomMargin=0.85 * inch,
        title=TITLE, author="Nikhil Shah",
    )
    doc.build(story, canvasmaker=NumberedCanvas)
    print("Saved", OUTPUT)


if __name__ == "__main__":
    build()
