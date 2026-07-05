import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def dang_ky_font():

    if "DejaVu" in pdfmetrics.getRegisteredFontNames():
        return

    base = os.path.dirname(os.path.dirname(__file__))

    pdfmetrics.registerFont(
        TTFont(
            "DejaVu",
            os.path.join(base, "fonts", "DejaVuSans.ttf")
        )
    )

    pdfmetrics.registerFont(
        TTFont(
            "DejaVu-Bold",
            os.path.join(base, "fonts", "DejaVuSans-Bold.ttf")
        )
    )