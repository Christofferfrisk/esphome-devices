"""Insert the revised main-board circuit pages into the Radiola build manual.

The original main-board circuit sheets are PDF pages 8 and 9 (zero-based
indices 7 and 8).  The EM80 pages that follow them remain untouched.
"""
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas


ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(__file__).with_name("Radiola_Manual_Base.pdf")
REFERENCE = Path(__file__).with_name("Radiola_Circuit_Wiring_Reference_v18.pdf")
OUTPUT = ROOT / "Radiola_Build_Schema.pdf"


def contents_page():
    """Return a replacement contents PDF page matching the manual's calm style."""
    width, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    canvas.setFillColor(HexColor("#FBF8EE"))
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    brown = HexColor("#9B7B42")
    ink = HexColor("#292722")
    muted = HexColor("#786F62")

    canvas.setFillColor(ink)
    canvas.setFont("Helvetica-Bold", 21)
    canvas.drawString(52, height - 72, "Contents")
    canvas.setStrokeColor(brown)
    canvas.setLineWidth(1.2)
    canvas.line(52, height - 86, width - 52, height - 86)

    entries = [
        ("System block diagram", "3", False),
        ("1.  Overview", "4", False),
        ("2.  Subsystems", "4", False),
        ("3.  Wiring schema", "6", False),
        ("4.  Power budget (5V logic rail)", "6", False),
        ("5.  Firmware behavior summary", "7", False),
        ("6.  Main board circuit wiring reference", "8", False),
        ("     System wiring at a glance", "8", True),
        ("     Controls, sensing and audio", "9", True),
        ("     Power rail, LEDs and standby", "10", True),
        ("     Dial motor and encoder", "11", True),
        ("Appendix - EM80 magic eye reference", "12", False),
        ("     Pin layout and wiring reference", "12", True),
        ("     How the EM80 works", "13", True),
        ("     Complete circuit schematic", "14", True),
        ("Build reference", "15", False),
    ]
    y = height - 120
    for label, page, child in entries:
        size = 8.6 if child else 9.4
        font = "Helvetica" if child else "Helvetica-Bold"
        canvas.setFont(font, size)
        canvas.setFillColor(muted if child else ink)
        canvas.drawString(56, y, label)
        canvas.setStrokeColor(HexColor("#D8D0C1"))
        canvas.setLineWidth(.45)
        start = 56 + stringWidth(label, font, size) + 10
        end = width - 79
        if start < end:
            canvas.setDash(1, 2)
            canvas.line(start, y + 2, end, y + 2)
            canvas.setDash()
        canvas.setFillColor(muted if child else ink)
        canvas.drawRightString(width - 56, y, page)
        y -= 25 if not child else 20

    canvas.setFillColor(muted)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(width / 2, 28, "Radiola operation & service manual")
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def system_block_page():
    """Return a clean hub-and-spoke system diagram with orthogonal routing."""
    width, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    ink = HexColor("#292722")
    muted = HexColor("#6F6A61")
    gold = HexColor("#9B7B42")
    green = HexColor("#1A9B73")
    amber = HexColor("#B87400")
    red = HexColor("#D94B4B")
    blue_fill = HexColor("#DCE8F4")
    green_fill = HexColor("#E5EFDF")
    amber_fill = HexColor("#FFF3D1")
    peach_fill = HexColor("#F5E4D8")
    pink_fill = HexColor("#EFD8DE")
    cream_fill = HexColor("#F6F0E4")

    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(0, 0, width, height, fill=1, stroke=0)
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica-Bold", 17)
    canvas.drawString(28, height - 34, "Radiola - system block diagram")
    canvas.setFillColor(muted)
    canvas.setFont("Helvetica", 8.5)
    canvas.drawString(28, height - 49, "ESP32 / ESPHome internet radio - motorized dial, NFC, magic eye, Home Assistant")
    canvas.setStrokeColor(gold)
    canvas.setLineWidth(1.1)
    canvas.line(28, height - 56, width - 28, height - 56)

    # Compact colour key.
    legend = [
        (blue_fill, "Logic / GPIO"),
        (green_fill, "Always-on / network"),
        (peach_fill, "External motor supply"),
        (pink_fill, "EM80 / isolated HV"),
    ]
    lx = 28
    for fill, label in legend:
        canvas.setFillColor(fill)
        canvas.setStrokeColor(ink)
        canvas.setLineWidth(.45)
        canvas.rect(lx, height - 75, 9, 7, fill=1, stroke=1)
        canvas.setFillColor(muted)
        canvas.setFont("Helvetica", 6.5)
        canvas.drawString(lx + 13, height - 74, label)
        lx += 128

    def draw_box(x, y, box_width, box_height, heading, lines, fill, border=ink):
        canvas.setFillColor(fill)
        canvas.setStrokeColor(border)
        canvas.setLineWidth(.8)
        canvas.roundRect(x, y, box_width, box_height, 4.5, fill=1, stroke=1)
        canvas.setFillColor(ink)
        canvas.setFont("Helvetica-Bold", 8.2)
        canvas.drawCentredString(x + box_width / 2, y + box_height - 15, heading)
        canvas.setFillColor(muted)
        canvas.setFont("Helvetica", 6.2)
        baseline = y + box_height - 28
        for value in lines:
            canvas.drawCentredString(x + box_width / 2, baseline, value)
            baseline -= 9

    def route(points, colour=ink, line_width=.9):
        canvas.setStrokeColor(colour)
        canvas.setLineWidth(line_width)
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            canvas.line(x1, y1, x2, y2)

    def route_label(label, x, y, colour=muted):
        canvas.setFillColor(HexColor("#FFFFFF"))
        label_width = stringWidth(label, "Helvetica-Bold", 6.0)
        canvas.rect(x - label_width / 2 - 3, y - 2, label_width + 6, 9, fill=1, stroke=0)
        canvas.setFillColor(colour)
        canvas.setFont("Helvetica-Bold", 6.0)
        canvas.drawCentredString(x, y, label)

    # Three aligned rows around the ESP32 hub.
    draw_box(70, 655, 110, 44, "Power supplies", ["5V logic rail", "external 12V"], blue_fill)
    draw_box(242.5, 655, 110, 44, "Always-on I2C", ["AS5600 / ADS1115", "PN532"], green_fill, green)
    draw_box(415, 655, 110, 44, "Network services", ["HA / Sonos", "dashboard"], green_fill, green)

    draw_box(70, 510, 110, 54, "Front panel", ["buttons / standby", "mechanical interlock"], blue_fill)
    draw_box(230, 510, 135, 54, "ESP32-WROOM", ["ESPHome firmware", "192.168.31.177"], blue_fill)
    draw_box(415, 510, 110, 54, "Audio", ["DFPlayer Mini", "speaker / effects"], amber_fill, amber)

    draw_box(70, 365, 110, 48, "EM80 magic eye", ["relay + 6.3V heater", "GPIO A / B control"], pink_fill)
    draw_box(242.5, 365, 110, 48, "Dial drive", ["DRV8825 + NEMA17", "external 12V"], peach_fill, amber)
    draw_box(415, 365, 110, 48, "Power rail + LEDs", ["GPIO14 switch", "5x LEDC outputs"], cream_fill, amber)

    # Top row. Each route owns a separate lane and terminates at a box edge.
    route([(125, 655), (125, 610), (245, 610), (245, 564)], red)
    route_label("5V", 184, 613, red)
    route([(297.5, 655), (297.5, 564)], green, 1.05)
    route_label("I2C", 313, 604, green)
    route([(470, 655), (470, 610), (350, 610), (350, 564)], green)
    route_label("WiFi / API", 411, 613, green)

    # Middle row.
    route([(180, 537), (230, 537)], ink)
    route_label("GPIO", 205, 540)
    route([(365, 537), (415, 537)], amber)
    route_label("UART", 390, 540, amber)

    # Bottom row. Separate left, centre and right lanes prevent crossings.
    route([(245, 510), (245, 455), (125, 455), (125, 413)], ink)
    route_label("GPIO A / B", 184, 458)
    route([(297.5, 510), (297.5, 413)], amber, 1.05)
    route_label("STEP / DIR / EN", 330, 454, amber)
    route([(350, 510), (350, 470), (470, 470), (470, 413)], amber)
    route_label("GPIO14 + PWM", 410, 473, amber)

    # Notes use the remaining lower page without crowding the diagram.
    canvas.setStrokeColor(gold)
    canvas.setLineWidth(.8)
    canvas.line(28, 325, width - 28, 325)
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica-Bold", 9.5)
    canvas.drawString(28, 309, "Design notes")
    notes = [
        "AS5600 remains on the always-on rail so dial position is tracked in standby.",
        "External 12V feeds the motor and the EM80 relay; LM2596 regulates the heater to 6.3V.",
        "GPIO14 drives the PMOS rail through a 2N7000 level shifter; do not PWM this output.",
        "DRV8825 GPIO13/5/15 assignments remain provisional until physical wiring is confirmed.",
    ]
    canvas.setFont("Helvetica", 7.2)
    y = 291
    for note in notes:
        canvas.setFillColor(gold)
        canvas.drawString(28, y, "-")
        canvas.setFillColor(muted)
        canvas.drawString(40, y, note)
        y -= 18

    canvas.setFillColor(muted)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(width / 2, 25, "Radiola operation & service manual - page 3")
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def em80_schematic_correction():
    """Overlay the MAX1771 input and shutdown nets on the existing EM80 sheet."""
    _, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    red = HexColor("#E24B4A")
    signal = HexColor("#202938")

    # IN+ (x=507.4) is supplied by the existing +5 V rail ending at x=481.9.
    canvas.setStrokeColor(red)
    canvas.setLineWidth(1.8)
    canvas.line(481.9, height - 147.4, 507.4, height - 147.4)

    # Remove the misleading red stub formerly drawn above SHDN (x=530.1).
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(526.5, height - 166.5, 8, 21, fill=1, stroke=0)

    # MAX1771 SHDN is active-high; route it to the module's ground net for
    # normal operation.  The path stays outside the module body.
    canvas.setStrokeColor(signal)
    canvas.setLineWidth(1.25)
    canvas.line(530.1, height - 164.4, 575.0, height - 164.4)
    canvas.line(575.0, height - 164.4, 575.0, height - 226.8)
    canvas.line(575.0, height - 226.8, 524.4, height - 226.8)

    # Keep the boost output annotation inside the printable area.
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(578, height - 214, 17, 34, fill=1, stroke=0)
    canvas.setStrokeColor(HexColor("#B66F00"))
    canvas.setLineWidth(1.25)
    canvas.line(564, height - 198, 588, height - 198)
    canvas.setFillColor(HexColor("#B66F00"))
    canvas.setFont("Helvetica", 5.5)
    canvas.drawRightString(590, height - 191, "HV OUT")
    canvas.drawRightString(590, height - 207, "~80V")

    # The PWM path uses a gate resistor, not an RC filter.
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(275, height - 475, 35, 13, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#687386"))
    canvas.setFont("Helvetica", 5)
    canvas.drawString(278, height - 471.5, "Gate R")

    canvas.setFillColor(HexColor("#E24B4A"))
    canvas.setFont("Helvetica", 5.5)
    canvas.drawString(46, height - 159, "5V heater supply (tube nominal: 6.3V)")
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def em80_complete_schematic_page():
    """Return a compact EM80 sheet using relay-switched 12V power."""
    width, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    ink = HexColor("#202938")
    muted = HexColor("#687386")
    teal = HexColor("#148F83")
    green = HexColor("#16B85A")
    red = HexColor("#E64B4B")
    amber = HexColor("#BE7600")
    pale_green = HexColor("#E9F8EC")
    pale_amber = HexColor("#FFF3D1")
    blue = HexColor("#DCE8F4")
    line_grey = HexColor("#CBD3DB")
    white = HexColor("#FFFFFF")

    def txt(value, x, y, size=8, color=ink, bold=False, align="left"):
        font = "Helvetica-Bold" if bold else "Helvetica"
        canvas.setFont(font, size)
        canvas.setFillColor(color)
        if align == "center":
            canvas.drawCentredString(x, y, value)
        elif align == "right":
            canvas.drawRightString(x, y, value)
        else:
            canvas.drawString(x, y, value)

    def wire(x1, y1, x2, y2, color=ink, stroke=1.1):
        canvas.setStrokeColor(color)
        canvas.setLineWidth(stroke)
        canvas.line(x1, y1, x2, y2)

    def component(x, y, w, h, name, detail="", fill=white, border=teal):
        canvas.setFillColor(fill)
        canvas.setStrokeColor(border)
        canvas.setLineWidth(1.15)
        canvas.roundRect(x, y, w, h, 7, fill=1, stroke=1)
        txt(name, x + w / 2, y + h - 15, 8.5, ink, True, "center")
        if detail:
            txt(detail, x + w / 2, y + 8, 6.1, muted, False, "center")

    def resistor_v(x, y_top, y_bottom, label, color=ink):
        mid = (y_top + y_bottom) / 2
        pts = [(x, y_top), (x, mid + 18), (x + 6, mid + 12),
               (x - 6, mid + 6), (x + 6, mid), (x - 6, mid - 6),
               (x + 6, mid - 12), (x, mid - 18), (x, y_bottom)]
        for first, second in zip(pts, pts[1:]):
            wire(first[0], first[1], second[0], second[1], color, 1.05)
        txt(label, x + 10, mid - 2, 6.5, muted)

    def resistor_h(x_left, x_right, y, label, color=ink):
        mid = (x_left + x_right) / 2
        pts = [(x_left, y), (mid - 12, y), (mid - 8, y + 4),
               (mid - 4, y - 4), (mid, y + 4), (mid + 4, y - 4),
               (mid + 8, y + 4), (mid + 12, y), (x_right, y)]
        for first, second in zip(pts, pts[1:]):
            wire(first[0], first[1], second[0], second[1], color, 1.05)
        txt(label, mid, y + 9, 6.2, muted, False, "center")

    def ground(x, y):
        wire(x, y, x, y - 5)
        wire(x - 8, y - 5, x + 8, y - 5)
        wire(x - 5, y - 8, x + 5, y - 8)
        wire(x - 2, y - 11, x + 2, y - 11)

    txt("Complete Circuit Schematic", width / 2, height - 62, 19, ink, True, "center")
    txt("ESP32 Radiola - relay power, regulated heater, shadow and HV wiring", width / 2, height - 82, 9.5, muted, False, "center")
    wire(56, height - 95, width - 56, height - 95, teal, 1.3)

    txt("RELAY POWER CONTROL", 150, 690, 8.5, teal, True, "center")
    component(42, 620, 92, 38, "12V supply", "+ to COM; - to GND", pale_amber, amber)

    # Relay module with every terminal named at its connection point.
    canvas.setFillColor(blue)
    canvas.setStrokeColor(ink)
    canvas.setLineWidth(1.15)
    canvas.roundRect(164, 600, 116, 78, 7, fill=1, stroke=1)
    txt("Relay module", 222, 653, 8.5, ink, True, "center")
    txt("+", 240, 667, 6.5, red, True, "center")
    txt("COM*", 170, 640, 5.8, red, True)
    txt("S", 170, 618, 6.2, green, True)
    txt("NO", 274, 640, 5.8, red, True, "right")
    txt("NC", 274, 618, 5.8, muted, True, "right")
    txt("-", 216, 605, 7.0, ink, True, "center")
    wire(134, 639, 164, 639, red, 1.8)
    wire(280, 639, 520, 639, red, 1.8)
    wire(280, 620, 292, 620, muted, .9)
    wire(289, 617, 295, 623, muted, .9)
    wire(289, 623, 295, 617, muted, .9)
    txt("unused", 292, 608, 5.4, muted, False, "center")
    txt("+12V_SW", 305, 647, 6.5, red, True, "center")

    # Relay-module power and both low-voltage return paths are explicit. The
    # relay contact switches only +12V; it does not provide a GND output.
    wire(240, 678, 240, 686, red, 1.1)
    txt("+5V logic", 240, 691, 6.2, red, True, "center")
    wire(88, 620, 88, 600, ink)
    wire(88, 600, 32, 600, ink)
    wire(216, 600, 216, 530, ink)
    wire(216, 530, 32, 530, ink)
    wire(32, 600, 32, 342, ink)
    wire(32, 342, 42, 342, ink)

    component(48, 545, 82, 38, "GPIO A", "EM80 power", pale_green, green)
    wire(130, 564, 148, 564, green)
    wire(148, 564, 148, 620, green)
    wire(148, 620, 164, 620, green)

    txt("GND - common low-voltage return", width / 2, 326, 8, ink, True, "center")
    wire(42, 342, width - 42, 342, ink, 1.8)

    # The switched 12V rail feeds both the HV module and the heater buck.
    txt("HEATER SUPPLY", 317, 600, 7.8, teal, True, "center")
    component(265, 535, 104, 54, "LM2596 buck", "12V -> adjusted 6.3V", pale_amber, amber)
    wire(317, 639, 317, 589, red, 1.3)
    component(257, 458, 60, 28, "Pin 5", "heater +", pale_green)
    wire(285, 535, 285, 486, red, 1.2)
    resistor_v(287, 458, 405, "EM80 heater", red)
    component(257, 377, 60, 28, "Pin 4", "heater -", pale_green)
    wire(287, 377, 287, 342, ink)
    wire(346, 535, 390, 535, ink)
    wire(390, 535, 390, 342, ink)
    txt("OUT-", 351, 524, 5.8, muted, True)

    # Pin 1 self-bias and optocoupler clamp.  PC817 output orientation is
    # deliberate: collector at 0 V, emitter at the negative-going grid.
    txt("SHADOW CONTROL", 137, 515, 8.5, teal, True, "center")
    component(173, 475, 62, 28, "Pin 1", "control grid", pale_green)
    component(133, 383, 102, 72, "Q2 PC817", "negative-grid clamp", pale_amber, amber)
    txt("LED A / K", 158, 417, 6.0, ink, True, "center")
    txt("E -> Pin 1", 208, 427, 6.0, ink, True, "center")
    txt("C -> GND", 208, 407, 6.0, ink, True, "center")
    wire(204, 475, 204, 455, ink)
    wire(208, 383, 208, 342, ink)
    component(43, 405, 70, 36, "GPIO B", "PWM ~5kHz", pale_green, green)
    resistor_h(113, 133, 423, "470R", green)
    wire(204, 475, 242, 475, ink)
    resistor_v(242, 475, 370, "1M+")
    wire(242, 370, 242, 342, ink)

    # MAX1771 module and tube HV connections.
    txt("HV AND TUBE", 486, 615, 7.8, teal, True, "center")
    component(429, 535, 104, 64, "MAX1771", "12V input; output ~80V", pale_amber, amber)
    wire(481, 639, 481, 599, red, 1.3)
    txt("IN+", 463, 603, 5.8, muted, True, "center")
    wire(447, 535, 415, 535, ink)
    wire(415, 535, 415, 342, ink)
    txt("SHDN -> GND", 471, 525, 5.8, muted, True, "right")
    wire(505, 535, 530, 535, ink)
    wire(530, 535, 530, 342, ink)
    txt("module GND", 500, 525, 5.8, muted)
    wire(533, 566, 548, 566, amber, 1.4)
    wire(548, 620, 548, 430, amber, 1.4)
    wire(548, 566, 548, 620, amber, 1.4)
    txt("HV ~80 V", 544, 513, 6.2, amber, True, "right")
    component(440, 474, 68, 30, "Pin 9", "target", pale_green)
    wire(508, 489, 548, 489, amber, 1.1)
    component(430, 402, 78, 34, "Pins 7 + 3", "tied together", pale_green)
    wire(508, 419, 520, 419, amber)
    resistor_v(520, 470, 419, "200k", amber)
    wire(520, 470, 548, 470, amber)
    component(430, 352, 68, 28, "Pin 2", "cathode", pale_green)
    wire(464, 352, 464, 342, ink)

    # Input decoupling on the switched rail.
    wire(402, 639, 402, 616, red)
    wire(392, 616, 412, 616, ink)
    wire(392, 611, 412, 611, ink)
    wire(402, 611, 402, 342, ink)
    txt("100uF 50V", 402, 590, 5.8, muted, False, "center")

    # Compact build notes make the unusual optocoupler polarity unmistakable.
    canvas.setFillColor(HexColor("#F4F7F8"))
    canvas.setStrokeColor(line_grey)
    canvas.roundRect(55, 274, width - 110, 42, 6, fill=1, stroke=1)
    txt("Important Q2 orientation", 68, 300, 8, ink, True)
    txt("PC817 collector -> GND; emitter -> Pin 1. When its LED is off, the 1M resistor permits negative grid self-bias.", 68, 286, 7, muted)
    txt("Relay markings: S=GPIO A, +=5V, -=GND; COM* is the unmarked centre terminal between NC and NO.", 68, 276, 6.5, muted)

    headers = ["Section", "Connection", "Required note"]
    widths = [105, 185, 195]
    rows = [
        ("Power", "+12V -> relay COM*; NO -> +12V_SW", "S=GPIO A; +=5V; -=GND"),
        ("Heater", "+12V_SW -> LM2596 -> Pins 5 / 4", "Adjust and meter 6.3V before fitting tube"),
        ("Shadow", "Pin 1 -> 1M + PC817 emitter", "GPIO B drives opto LED through 470R"),
        ("HV", "Pin 9 direct; Pins 7+3 via 200k", "Adjust MAX1771 output to about 80 V"),
        ("MAX1771", "IN+ -> +12V_SW; SHDN -> GND", "100uF decoupling at module input"),
    ]
    x, y, row_h = 55, 252, 21
    canvas.setFillColor(teal)
    canvas.rect(x, y - row_h, sum(widths), row_h, fill=1, stroke=0)
    cx = x
    for heading, col_w in zip(headers, widths):
        txt(heading, cx + 7, y - 14, 7.5, white, True)
        cx += col_w
    for row_index, row in enumerate(rows):
        yy = y - (row_index + 2) * row_h
        canvas.setFillColor(HexColor("#F4F7F8") if row_index % 2 == 0 else white)
        canvas.rect(x, yy, sum(widths), row_h, fill=1, stroke=0)
        cx = x
        for value, col_w in zip(row, widths):
            txt(value, cx + 7, yy + 7, 6.4, ink)
            cx += col_w

    txt("HIGH VOLTAGE", 55, 91, 9, red, True)
    txt("Disconnect power, discharge the HV output and verify 0 V before touching the circuit.", 55, 76, 7.5, muted)
    wire(55, 38, width - 55, 38, line_grey, .7)
    txt("Radiola / EM80 / corrected compact schematic", 55, 25, 7, muted)
    txt("Manual page 14", width - 55, 25, 7, muted, False, "right")
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def em80_pin_q2_overlay():
    """Update the EM80 pin-reference page for PC817 and 6.3V buck wiring."""
    width, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(230, height - 614, 245, 20, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#202938"))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(235, height - 608.5, "PC817 emitter + 1M to GND")

    # Diagram callouts beside heater pins 4 and 5.
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(365, height - 480, 150, 16, fill=1, stroke=0)
    canvas.rect(274, height - 511, 150, 16, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#202938"))
    canvas.setFont("Helvetica", 6.2)
    canvas.drawString(375, height - 474.5, "-> LM2596 OUT- / GND")
    canvas.drawString(285, height - 505.5, "-> LM2596 6.3V+")

    # Pin table connection cells.
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(225, height - 686, 290, 36, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#202938"))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(235, height - 664.5, "LM2596 OUT- / common GND")
    canvas.drawString(235, height - 683, "LM2596 6.3V+")

    # The reference circuit is adjusted to about 80V, not the module maximum.
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(228, height - 760, 105, 15, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#202938"))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(235, height - 756, "HV+ direct (~80V)")
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def em80_operation_q2_overlay():
    """Replace the MOSFET explanation with the optocoupler clamp behavior."""
    width, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(68, height - 497, width - 120, 42, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#202938"))
    canvas.setFont("Helvetica", 8.4)
    canvas.drawString(71, height - 469, "When the Q2 optocoupler turns on, its output transistor clamps Pin 1 close to GND,")
    canvas.drawString(71, height - 480.5, "overriding the self-bias and forcing the grid toward 0 V. PWM duty controls how")
    canvas.drawString(71, height - 492, "long the clamp is active, varying the average grid voltage and shadow.")
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def em80_build_q2_overlay():
    """Rebuild the parts and connection tables for relay-powered EM80 wiring."""
    width, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    ink = HexColor("#202938")
    muted = HexColor("#687386")
    teal = HexColor("#148F83")
    white = HexColor("#FFFFFF")
    pale = HexColor("#F4F7F8")

    def table(title, x, top_y, widths, headers, rows, row_h=17):
        canvas.setFillColor(ink)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(x, top_y, title)
        y = top_y - 11
        canvas.setFillColor(teal)
        canvas.rect(x, y - row_h, sum(widths), row_h, fill=1, stroke=0)
        cx = x
        for heading, col_w in zip(headers, widths):
            canvas.setFillColor(white)
            canvas.setFont("Helvetica-Bold", 6.8)
            canvas.drawString(cx + 6, y - 11.5, heading)
            cx += col_w
        for row_index, row in enumerate(rows):
            yy = y - (row_index + 2) * row_h
            canvas.setFillColor(pale if row_index % 2 == 0 else white)
            canvas.rect(x, yy, sum(widths), row_h, fill=1, stroke=0)
            cx = x
            for value, col_w in zip(row, widths):
                canvas.setFillColor(ink)
                canvas.setFont("Helvetica", 6.1)
                canvas.drawString(cx + 6, yy + 5.7, value)
                cx += col_w
        return y - (len(rows) + 1) * row_h

    # Cover the original tables completely before rebuilding them.
    canvas.setFillColor(white)
    canvas.rect(48, 190, width - 96, 540, fill=1, stroke=0)
    x = 57
    widths = [105, 130, 35, 225]
    headers = ["Component", "Value / Type", "Qty", "Notes"]
    rows = [
        ("EM80 (6BR5)", "Magic eye tube", "1", "Noval 9-pin base"),
        ("LM2596 module", "Adjustable buck", "1", "Set to 6.3V before fitting tube"),
        ("Relay module", "S / + / - input", "1", "NC / COM* / NO; COM* is unmarked"),
        ("PC817", "Optocoupler", "1", "Q2 shadow clamp; C->GND, E->Pin 1"),
        ("MAX1771 module", "5-12V to HV DC", "1", "Powered from switched 12V; set ~80V"),
        ("Resistor", "200k", "1", "Triode load resistor"),
        ("Resistor", "1M or more", "1+", "Grid self-bias"),
        ("Resistor", "470R", "1", "PC817 LED current limiting"),
        ("Capacitor", "100uF 50V", "1", "Switched 12V input decoupling"),
        ("Noval socket", "B9A 9-pin", "1", "For the EM80 tube"),
    ]
    table("Parts List", x, 690, widths, headers, rows, 16.5)

    connection_widths = [90, 125, 280]
    connection_headers = ["Source", "Function", "Connection"]
    connection_rows = [
        ("GPIO A", "Digital output", "Relay module S terminal"),
        ("GPIO B", "PWM ~5kHz", "PC817 LED through 470R (shadow control)"),
        ("+12V", "External supply", "Unmarked centre (COM*); NO becomes +12V_SW"),
        ("GND", "Common return", "ESP32, relay -, LM2596 and MAX1771 grounds"),
    ]
    table("Control and Power Connections", x, 468, connection_widths, connection_headers, connection_rows, 18)

    tube_rows = [
        ("Pin 1", "Grid (yellow)", "PC817 emitter + 1M junction"),
        ("Pin 2", "Cathode (black)", "Common GND"),
        ("Pin 4", "Heater - (black)", "LM2596 OUT- / common GND"),
        ("Pin 5", "Heater + (blue)", "LM2596 OUT+ adjusted to 6.3V"),
        ("Pin 7", "Triode (red)", "200k to HV+; jumper Pin 3 to Pin 7"),
        ("Pin 9", "Target", "HV+ direct from MAX1771"),
    ]
    table("Breadboard to Tube Socket (6 wires)", x, 350, connection_widths, connection_headers, tube_rows, 18)

    # Correct the first safety bullet while preserving the remaining source list.
    canvas.setFillColor(HexColor("#FFF4F4"))
    canvas.rect(66, height - 722, 455, 14, fill=1, stroke=0)
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(68, height - 718.8, "- The HV module may exceed 200V; this build is adjusted to roughly 80V.")
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def em80_build_reference_correction():
    """Remove the incorrect statement that GPIO A drives MAX1771 SHDN."""
    _, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(228, height - 408, 145, 12, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#202938"))
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(232, height - 406.5, "Q1 gate (heater on/off)")

    # Correct the PWM path wording: the drawing contains a 10k gate resistor,
    # not a complete RC filter.
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(305, height - 288, 185, 13, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#202938"))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(309, height - 284.5, "Q1 pull-down + Q2 gate resistor")
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(228, height - 429, 195, 13, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#202938"))
    canvas.drawString(232, height - 426, "Q2 gate via 10k resistor (shadow control)")

    # State both the module capability and this build's configured voltage.
    canvas.setFillColor(HexColor("#FFF4F4"))
    canvas.rect(66, height - 722, 450, 13, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#202938"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(68, height - 718.8, "- The HV module can output about 200V DC; this build is adjusted to roughly 80V.")
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def power_budget_em80_row():
    """Make the relay-switched 12V EM80 branch explicit in the power table."""
    _, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    white = HexColor("#FFFFFF")
    ink = HexColor("#292722")

    # Replace the low-impact miscellaneous row with the EM80's real supply
    # budget.  It remains excluded from the 5 V logic-rail total below.
    canvas.setFillColor(white)
    canvas.rect(66, height - 726, 455, 15, fill=1, stroke=0)
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica", 7.5)
    y = height - 721.5
    canvas.drawString(69, y, "EM80 magic eye*")
    canvas.drawString(211, y, "~0.3 A @12V")
    canvas.drawString(279, y, "0.5 A")
    canvas.drawString(347, y, "Relay-switched 12V - excluded from total")

    # The DRV8825 carrier and NEMA17 are powered by a separate 12 V rail.
    # Control inputs are 3.3 V signals and do not constitute a 5 V load.
    canvas.setFillColor(white)
    canvas.rect(66, height - 690, 455, 15, fill=1, stroke=0)
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica", 7.5)
    y = height - 685.4
    canvas.drawString(69, y, "NEMA17 via DRV8825*")
    canvas.drawString(211, y, "external 12V")
    canvas.drawString(279, y, "Vref-limited")
    canvas.drawString(347, y, "Separate motor supply - excluded")

    # Keep the ADC visually and electrically distinct from the motor row.
    canvas.setFillColor(HexColor("#F4F7F8"))
    canvas.rect(66, height - 708, 455, 15, fill=1, stroke=0)
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica", 7.5)
    y = height - 703.4
    canvas.drawString(69, y, "ADS1115 (5V VDD)")
    canvas.drawString(211, y, "0.15 mA")
    canvas.drawString(279, y, "0.26 mA")
    canvas.drawString(347, y, "5V rail; I2C must remain 3.3V-safe")

    # Restore the table grid erased by the row overlays.
    canvas.setStrokeColor(HexColor("#8C8C86"))
    canvas.setLineWidth(.35)
    for x in (66, 206, 274, 343, 535):
        canvas.line(x, height - 726, x, height - 675)
    for yy in (height - 726, height - 708, height - 690, height - 672):
        canvas.line(66, yy, 535, yy)

    # Replace the old conditional footnote with an unambiguous supply rule.
    canvas.setFillColor(white)
    canvas.rect(45, height - 782, 505, 28, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#6F6A61"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(48, height - 767.7, "* External 12V feeds NEMA17/DRV8825 and the separately switched EM80 branch.")
    canvas.drawString(48, height - 778.7, "The LM2596 regulates the EM80 heater to 6.3V; external loads are excluded from the 5V total.")
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def system_page_correction():
    """Standardize the magic-eye heater wording on the system page."""
    _, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    # Subtitle inside the pale EM80 box.
    canvas.setFillColor(HexColor("#EFD8DE"))
    canvas.rect(66, height - 565, 98, 29, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#6F6A61"))
    canvas.setFont("Helvetica", 5.8)
    canvas.drawCentredString(115, height - 543, "tuning-proximity indicator")
    canvas.drawCentredString(115, height - 551, "relay + 6.3V heater")
    canvas.drawCentredString(115, height - 559, "PC817 shadow control")

    # The rail switch now includes a 2N7000 level-shifter stage.
    canvas.setFillColor(HexColor("#DCE8F4"))
    canvas.rect(329, height - 351, 72, 22, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#6F6A61"))
    canvas.setFont("Helvetica", 6.0)
    canvas.drawCentredString(365, height - 338, "GPIO14 -> 2N7000")
    canvas.drawCentredString(365, height - 347, "PMOS load switch")
    # Replace only the inconsistent voltage token in the design note.
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(228, height - 641, 70, 12, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#6F6A61"))
    canvas.setFont("Helvetica", 7.0)
    canvas.drawString(230, height - 638.5, "relay-switched EM80 branch is")
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def subsystem_page_correction():
    """Rewrite the EM80 paragraph and use the lower page for a supply map."""
    width, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    ink = HexColor("#292722")
    muted = HexColor("#6F6A61")
    teal = HexColor("#148F83")

    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(45, height - 149, 505, 84, fill=1, stroke=0)
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica", 9.3)
    lines = [
        "A vacuum magic eye tube (EM80/6BR5) whose shadow narrows as the dial approaches a station,",
        "driven from the same tuning-distance signal used for the static swim effect. GPIO A controls a",
        "3.3V-compatible relay module which switches 12V to both the MAX1771 and an LM2596 buck.",
        "The buck is adjusted to 6.3V for the heater. GPIO B drives a PC817 at about 5 kHz to vary",
        "the shadow. Anode/target voltage comes from the MAX1771 configured for roughly 80V. Full wiring",
        "and safety notes are reproduced in the reference schematic at the end of this document.",
    ]
    y = height - 78
    for line_text in lines:
        canvas.drawString(48, y, line_text)
        y -= 13

    canvas.setFont("Helvetica-Bold", 13)
    canvas.drawString(48, 500, "Power domains at a glance")
    canvas.setStrokeColor(teal)
    canvas.setLineWidth(1)
    canvas.line(48, 490, width - 48, 490)
    boxes = [
        (48, "Always-on logic", "5V rail", "ESP32, AS5600, ADS1115"),
        (218, "Switched 5V", "GPIO14 load switch", "DFPlayer Mini and LEDs"),
        (388, "External supplies", "12V motor + EM80", "6.3V heater via LM2596"),
    ]
    for x, heading, supply, detail in boxes:
        canvas.setFillColor(HexColor("#F4F7F8"))
        canvas.setStrokeColor(HexColor("#CBD3DB"))
        canvas.roundRect(x, 405, 150, 68, 7, fill=1, stroke=1)
        canvas.setFillColor(ink)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawCentredString(x + 75, 451, heading)
        canvas.setFillColor(teal)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawCentredString(x + 75, 435, supply)
        canvas.setFillColor(muted)
        canvas.setFont("Helvetica", 7)
        canvas.drawCentredString(x + 75, 419, detail)
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def wiring_schema_correction():
    """Make the rail-switch polarity and DRV8825 boot behavior accurate."""
    _, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    ink = HexColor("#292722")
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(203, height - 297, 332, 18, fill=1, stroke=0)
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(207, height - 293.5, "2N7000 gate (PMOS level shift)")
    canvas.drawString(398, height - 293.5, "GPIO HIGH enables; never PWM")
    canvas.setStrokeColor(HexColor("#777777"))
    canvas.setLineWidth(.35)
    canvas.line(203, height - 297, 535, height - 297)
    canvas.line(203, height - 279, 535, height - 279)
    canvas.line(203, height - 297, 203, height - 279)
    canvas.line(393, height - 297, 393, height - 279)
    canvas.line(535, height - 297, 535, height - 279)

    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(393, height - 458, 142, 22, fill=1, stroke=0)
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica", 7.2)
    canvas.drawString(398, height - 445, "*provisional; add 10k EN pull-up")
    canvas.drawString(398, height - 454, "to 3.3V for coils-off boot")
    canvas.setStrokeColor(HexColor("#777777"))
    canvas.setLineWidth(.35)
    canvas.line(393, height - 458, 535, height - 458)
    canvas.line(393, height - 436, 535, height - 436)
    canvas.line(393, height - 458, 393, height - 436)
    canvas.line(535, height - 458, 535, height - 436)

    # Replace the obsolete EM80 MOSFET rows with the relay and PC817 controls.
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(55, height - 500, 485, 41, fill=1, stroke=0)
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica", 7.2)
    canvas.drawString(71, height - 475, "GPIO A (TBD)")
    canvas.drawString(128, height - 475, "Digital out")
    canvas.drawString(207, height - 475, "EM80 relay module S")
    canvas.drawString(398, height - 475, "3.3V-compatible input")
    canvas.drawString(71, height - 493, "GPIO B (TBD)")
    canvas.drawString(128, height - 493, "PWM ~5kHz")
    canvas.drawString(207, height - 493, "PC817 LED via 470R")
    canvas.drawString(398, height - 493, "C->GND; E->Pin 1")
    canvas.setStrokeColor(HexColor("#777777"))
    canvas.setLineWidth(.35)
    for x in (66, 123, 203, 393, 535):
        canvas.line(x, height - 499, x, height - 460)
    for yy in (height - 499, height - 481, height - 463):
        canvas.line(66, yy, 535, yy)
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def firmware_page_balance():
    """Document automatic standby and retain a compact pre-power checklist."""
    _, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    ink = HexColor("#292722")
    teal = HexColor("#148F83")
    muted = HexColor("#6F6A61")

    canvas.setFillColor(ink)
    canvas.setFont("Helvetica-Bold", 13)
    canvas.drawString(48, 425, "Automatic standby")
    canvas.setStrokeColor(teal)
    canvas.setLineWidth(1)
    canvas.line(48, 415, 547, 415)

    canvas.setFillColor(HexColor("#F4F7F8"))
    canvas.setStrokeColor(HexColor("#CBD3DB"))
    canvas.roundRect(48, 335, 499, 64, 6, fill=1, stroke=1)
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(62, 383, "Timeout")
    canvas.setFont("Helvetica", 8.2)
    canvas.drawString(126, 383, "After 3 minutes without physical interaction, the Radiola enters standby.")
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(62, 366, "Sequence")
    canvas.setFont("Helvetica", 8.2)
    canvas.drawString(126, 366, "Shutdown sound, LED fade, Sonos stop, dial park, motor release, rail off.")
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(62, 349, "Reset / wake")
    canvas.setFont("Helvetica", 8.2)
    canvas.drawString(126, 349, "Dial, volume, Radio/LP buttons, or NFC activity reset the timer and wake it.")

    canvas.setFillColor(muted)
    canvas.setFont("Helvetica-Oblique", 7.6)
    canvas.drawString(
        50, 319,
        "Motor-driven snap and park movements do not count as activity. The physical standby plate remains authoritative."
    )

    canvas.setFillColor(ink)
    canvas.setFont("Helvetica-Bold", 13)
    canvas.drawString(48, 287, "Pre-power checklist")
    canvas.setStrokeColor(teal)
    canvas.setLineWidth(1)
    canvas.line(48, 277, 547, 277)
    checks = [
        "I2C pull-ups go to 3.3V only; remove any ADS1115 pull-ups tied to its 5V VDD.",
        "DRV8825 VMOT is on the external 12V supply with 100uF at the carrier.",
        "DRV8825 EN has a 10k pull-up to 3.3V so the coils remain off during ESP32 boot.",
        "Verify the GPIO14 level-shifted PMOS rail is off before enabling connected loads.",
        "Discharge and meter the EM80 HV output before touching or changing the circuit.",
    ]
    y = 252
    canvas.setFont("Helvetica", 8.1)
    for item in checks:
        canvas.setFillColor(teal)
        canvas.rect(52, y + 1, 5, 5, fill=0, stroke=1)
        canvas.setFillColor(muted)
        canvas.drawString(66, y, item)
        y -= 22
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def em80_pin_page_note():
    """State the regulated heater supply beside the pin table."""
    _, height = A4
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    canvas.setFillColor(HexColor("#FFFFFF"))
    canvas.rect(65, 65, 480, 20, fill=1, stroke=0)
    canvas.setFillColor(HexColor("#6F6A61"))
    canvas.setFont("Helvetica-Oblique", 7.5)
    canvas.drawString(72, 73, "The LM2596 supplies the EM80/6BR5 heater with a regulated 6.3V across Pins 5 and 4.")
    canvas.save()
    buffer.seek(0)
    return PdfReader(buffer).pages[0]


def main():
    manual = PdfReader(str(SOURCE))
    circuits = PdfReader(str(REFERENCE))
    writer = PdfWriter()
    updated_contents = contents_page()
    replacement_em80_schematic = em80_complete_schematic_page()
    power_budget_overlay = power_budget_em80_row()
    replacement_system_page = system_block_page()
    subsystem_overlay = subsystem_page_correction()
    wiring_overlay = wiring_schema_correction()
    firmware_overlay = firmware_page_balance()
    em80_pin_overlay = em80_pin_page_note()
    em80_pin_q2 = em80_pin_q2_overlay()
    em80_operation_q2 = em80_operation_q2_overlay()
    em80_build_q2 = em80_build_q2_overlay()

    for index, page in enumerate(manual.pages):
        if index == 1:
            writer.add_page(updated_contents)
            continue
        if index == 2:
            writer.add_page(replacement_system_page)
            continue
        if index == 7:
            for circuit_page in circuits.pages:
                writer.add_page(circuit_page)
        if index not in (7, 8):
            if index == 4:
                page.merge_page(subsystem_overlay)
            if index == 5:
                page.merge_page(wiring_overlay)
                page.merge_page(power_budget_overlay)
            if index == 6:
                page.merge_page(firmware_overlay)
            if index == 9:
                page.merge_page(em80_pin_overlay)
                page.merge_page(em80_pin_q2)
            if index == 10:
                page.merge_page(em80_operation_q2)
            if index == 11:
                writer.add_page(replacement_em80_schematic)
                continue
            if index == 12:
                page.merge_page(em80_build_q2)
            writer.add_page(page)

    writer.add_metadata({
        "/Title": "Radiola - Operation & Service Manual",
        "/Subject": "Updated main-board circuit wiring reference",
    })
    with OUTPUT.open("wb") as output_file:
        writer.write(output_file)
    print(OUTPUT)


if __name__ == "__main__":
    main()
