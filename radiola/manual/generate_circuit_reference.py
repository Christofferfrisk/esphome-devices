"""Generate the Radiola circuit wiring-reference section.

The circuit pages intentionally use connector-style callouts rather than a
literal wire-per-net drawing.  The firmware configuration remains the source
of truth; DRV8825 control GPIOs are explicitly marked provisional.
"""
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

OUT = Path(__file__).with_name("Radiola_Circuit_Wiring_Reference_v18.pdf")
W, H = A4
INK = HexColor("#202938")
MUTED = HexColor("#687386")
TEAL = HexColor("#148F83")
GREEN = HexColor("#16B85A")
BLUE = HexColor("#DCE8F4")
PEACH = HexColor("#F5E4D8")
RED = HexColor("#E64B4B")
AMBER = HexColor("#BE7600")
PALE_GREEN = HexColor("#E9F8EC")
PALE_AMBER = HexColor("#FFF3D1")
LINE = HexColor("#CBD3DB")


def text(c, s, x, y, size=10, color=INK, bold=False, align="left"):
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.setFillColor(color)
    width = stringWidth(s, "Helvetica-Bold" if bold else "Helvetica", size)
    if align == "center":
        x -= width / 2
    elif align == "right":
        x -= width
    c.drawString(x, y, s)


def line(c, x1, y1, x2, y2, color=INK, width=1.2, dash=None):
    c.setStrokeColor(color); c.setLineWidth(width)
    c.setDash(dash or [])
    c.line(x1, y1, x2, y2)
    c.setDash()


def box(c, x, y, w, h, title, subtitle="", fill=white, border=INK, title_size=13, subtitle_size=8.5):
    c.setFillColor(fill); c.setStrokeColor(border); c.setLineWidth(1.3)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=1)
    title_y = y + h - (18 if h <= 45 else 24)
    text(c, title, x + w / 2, title_y, title_size, INK, True, "center")
    if subtitle:
        subtitle_y = y + (8 if h <= 45 else h - 42)
        text(c, subtitle, x + w / 2, subtitle_y, subtitle_size, MUTED, False, "center")


def pill(c, x, y, label, color=TEAL, fill=None):
    fill = fill or white
    c.setFillColor(fill); c.setStrokeColor(color); c.setLineWidth(1.1)
    w = max(46, stringWidth(label, "Helvetica-Bold", 8.5) + 18)
    c.roundRect(x, y, w, 20, 7, fill=1, stroke=1)
    text(c, label, x + w / 2, y + 6, 8.5, color, True, "center")
    return w


def title(c, number, heading, sub):
    text(c, "RADIOLA - CIRCUIT WIRING REFERENCE", 42, H - 40, 8, MUTED, True)
    text(c, f"{number}. {heading}", 42, H - 73, 23, INK, True)
    text(c, sub, 42, H - 92, 10.5, MUTED)
    line(c, 42, H - 103, W - 42, H - 103, TEAL, 1.5)


def footer(c, page):
    line(c, 42, 38, W - 42, 38, LINE, .7)
    text(c, "Radiola / ESP32 / wiring reference", 42, 25, 7.5, MUTED)
    text(c, f"Manual page {page + 7} - verify wiring before applying power", W - 42, 25, 7.5, MUTED, False, "right")


def connector(c, x, y, pin, description, side="left", color=TEAL):
    w = pill(c, x, y, pin, color, PALE_GREEN if color == GREEN else white)
    tx = x + w + 8 if side == "left" else x - 8
    align = "left" if side == "left" else "right"
    text(c, description, tx, y + 6, 8.4, MUTED, False, align)
    return w


def resistor(c, x1, y1, x2, y2, label="", color=INK):
    """Compact zig-zag resistor on a horizontal or vertical net."""
    c.setStrokeColor(color); c.setLineWidth(1.25)
    if abs(x2 - x1) >= abs(y2 - y1):
        mid = (x1 + x2) / 2; pts = [(x1,y1),(mid-18,y1),(mid-12,y1+7),(mid-6,y1-7),(mid,y1+7),(mid+6,y1-7),(mid+12,y1+7),(mid+18,y1),(x2,y2)]
        for a,b in zip(pts, pts[1:]): c.line(*a,*b)
        text(c, label, mid, y1+11, 7.5, MUTED, False, "center")
    else:
        mid = (y1 + y2) / 2; pts = [(x1,y1),(x1,mid+18),(x1+7,mid+12),(x1-7,mid+6),(x1+7,mid),(x1-7,mid-6),(x1+7,mid-12),(x1,mid-18),(x2,y2)]
        for a,b in zip(pts, pts[1:]): c.line(*a,*b)
        text(c, label, x1+12, mid-3, 7.5, MUTED)


def ground(c, x, y):
    line(c, x, y, x, y-5, INK, 1)
    line(c, x-8, y-5, x+8, y-5, INK, 1)
    line(c, x-5, y-8, x+5, y-8, INK, 1)
    line(c, x-2, y-11, x+2, y-11, INK, 1)


def led(c, x, y, label="LED"):
    c.setStrokeColor(INK); c.setLineWidth(1.2); c.circle(x, y, 10, fill=0)
    line(c, x-10, y, x+10, y, INK); line(c, x+2, y-7, x+2, y+7, INK)
    line(c, x+8, y+9, x+15, y+16, INK); line(c, x+15, y+16, x+11, y+15, INK); line(c, x+15, y+16, x+14, y+12, INK)
    text(c, label, x, y-22, 7.5, MUTED, False, "center")


def mosfet(c, x, y, label="Q"):
    c.setStrokeColor(INK); c.setLineWidth(1.2); c.rect(x-14, y-20, 28, 40, fill=0, stroke=1)
    line(c, x, y+20, x, y+8); line(c, x, y-8, x, y-20); line(c, x-14, y, x-28, y)
    text(c, "D", x+7, y+10, 6.5, MUTED); text(c, "S", x+7, y-16, 6.5, MUTED); text(c, "G", x-11, y+4, 6.5, MUTED)
    text(c, label, x, y-33, 7.5, INK, True, "center")


def table(c, x, y, widths, headers, rows, row_h=20):
    total = sum(widths)
    c.setFillColor(TEAL); c.rect(x, y - row_h, total, row_h, fill=1, stroke=0)
    cx = x
    for h, w in zip(headers, widths):
        text(c, h, cx + 7, y - 14, 8, white, True); cx += w
    for r, row in enumerate(rows):
        yy = y - (r + 2) * row_h
        c.setFillColor(HexColor("#F4F7F8") if r % 2 == 0 else white)
        c.rect(x, yy, total, row_h, fill=1, stroke=0)
        cx = x
        for val, w in zip(row, widths):
            text(c, val, cx + 7, yy + 6, 7.5, INK); cx += w


def page_overview(c):
    title(c, 1, "System wiring at a glance", "Follow named connectors; power rails and signal roles use a consistent colour key.")
    # A compact ESP32-centred summary. Detailed connections follow on pages 9-11.
    box(c, 245, 580, 105, 45, "ESP32", "GPIO hub", BLUE, INK, 11, 7)
    box(c, 105, 580, 95, 45, "Always-on", "I2C sensing", PALE_GREEN, GREEN, 10, 7)
    box(c, 395, 580, 95, 45, "Switched", "audio / LEDs", PALE_AMBER, AMBER, 10, 7)
    box(c, 160, 475, 95, 45, "Dial drive", "DRV8825 / NEMA17", PEACH, AMBER, 10, 6.5)
    box(c, 340, 475, 95, 45, "EM80", "heater / HV", PALE_AMBER, AMBER, 10, 7)
    line(c, 200, 602.5, 245, 602.5, GREEN, 1.0)
    line(c, 350, 602.5, 395, 602.5, AMBER, 1.0)
    line(c, 270, 580, 270, 550, AMBER, 1.0); line(c, 270, 550, 207.5, 550, AMBER, 1.0); line(c, 207.5, 550, 207.5, 520, AMBER, 1.0)
    line(c, 325, 580, 325, 550, AMBER, 1.0); line(c, 325, 550, 387.5, 550, AMBER, 1.0); line(c, 387.5, 550, 387.5, 520, AMBER, 1.0)
    text(c, "I2C", 222, 609, 7, GREEN, True, "center")
    text(c, "UART / PWM", 372, 609, 7, AMBER, True, "center")
    text(c, "STEP / DIR / EN*", 207.5, 557, 7, AMBER, True, "center")
    text(c, "GPIO A / B", 387.5, 557, 7, AMBER, True, "center")
    text(c, "* DRV8825 pins are firmware placeholders - confirm physical wiring.", 70, 430, 8, RED, True)
    table(c, 70, 400, [100, 170, 240], ["Role", "Colour", "Meaning"], [
        ("Power", "Red +5 V / amber HV", "Supply rails; connect only to the labelled rail"),
        ("ESP / signal", "Green / charcoal", "GPIO, I2C, UART and control connections"),
        ("Ground", "Charcoal", "All low-voltage modules share common GND"),
    ])
    footer(c, 1); c.showPage()


def page_controls(c):
    title(c, 2, "Controls, sensing and audio", "Current low-voltage wiring, grouped by function with no shared signal crossings.")

    # Controller at the top; sensing and audio occupy independent lanes.
    box(c, 237, 650, 120, 48, "ESP32-WROOM", "current firmware pin map", BLUE, INK, 11, 7)
    text(c, "I2C SENSING", 42, 620, 8.5, TEAL, True)
    line(c, 42, 611, 355, 611, LINE, .7)
    text(c, "AUDIO", 390, 620, 8.5, AMBER, True)
    line(c, 390, 611, 553, 611, LINE, .7)

    # Clean I2C trunk with three short, aligned drops.
    line(c, 75, 570, 350, 570, GREEN, 1.2)
    line(c, 75, 548, 350, 548, GREEN, 1.2)
    text(c, "SDA  GPIO21", 68, 567, 7, GREEN, True, "right")
    text(c, "SCL  GPIO22", 68, 545, 7, GREEN, True, "right")
    line(c, 270, 650, 270, 570, GREEN, 1.0)
    line(c, 292, 650, 292, 548, GREEN, 1.0)

    # One bus pull-up pair, always to 3.3 V.
    text(c, "+3.3 V", 338, 602, 7, GREEN, True, "center")
    line(c, 325, 592, 350, 592, GREEN, 1.0)
    resistor(c, 330, 592, 330, 570, "", GREEN)
    resistor(c, 345, 592, 345, 548, "", GREEN)
    text(c, "2 x 4.7k", 356, 579, 6.3, MUTED)

    modules = [
        (60, "AS5600", "3.3 V / 0x36", "dial encoder"),
        (165, "ADS1115", "5 V / 0x48", "volume on A1"),
        (270, "PN532", "3.3 V / 0x24", "NFC reader"),
    ]
    for x, name, supply, role in modules:
        box(c, x, 474, 88, 48, name, supply, PALE_GREEN, GREEN, 9.5, 6.2)
        line(c, x + 26, 522, x + 26, 570, GREEN, .9)
        line(c, x + 62, 522, x + 62, 548, GREEN, .9)
        text(c, role, x + 44, 462, 6.7, MUTED, False, "center")

    c.setFillColor(HexColor("#F4F7F8"))
    c.setStrokeColor(LINE)
    c.roundRect(50, 430, 312, 22, 4, fill=1, stroke=1)
    text(c, "Single 3.3 V pull-up pair only; remove I2C pull-ups tied to 5 V.", 206, 438, 6.8, INK, False, "center")

    # UART is a compact point-to-point connection, separate from I2C.
    box(c, 410, 515, 118, 58, "DFPlayer Mini", "switched +5 V / UART 9600", PALE_AMBER, AMBER, 10, 6.4)
    line(c, 357, 680, 545, 680, AMBER, 1.0)
    line(c, 545, 680, 545, 553, AMBER, 1.0)
    line(c, 528, 553, 545, 553, AMBER, 1.0)
    line(c, 357, 662, 558, 662, AMBER, 1.0)
    line(c, 558, 662, 558, 535, AMBER, 1.0)
    line(c, 528, 535, 558, 535, AMBER, 1.0)
    c.setFillColor(white)
    c.rect(365, 673, 82, 12, fill=1, stroke=0)
    c.rect(365, 655, 82, 12, fill=1, stroke=0)
    text(c, "GPIO17 TX -> RX", 371, 676, 6.7, AMBER, True)
    text(c, "GPIO16 RX <- TX", 371, 658, 6.7, AMBER, True)
    line(c, 447, 515, 447, 485, INK, .9)
    line(c, 491, 515, 491, 485, INK, .9)
    text(c, "SPK1", 447, 492, 6, MUTED, False, "center")
    text(c, "SPK2", 491, 492, 6, MUTED, False, "center")
    c.setStrokeColor(INK)
    c.setLineWidth(1)
    c.circle(469, 472, 8, fill=0, stroke=1)
    line(c, 447, 485, 463, 478, INK, .9)
    line(c, 491, 485, 475, 478, INK, .9)
    text(c, "speaker", 469, 453, 6.5, MUTED, False, "center")

    # Only the three current physical inputs. GPIO12 and GPIO23 are now
    # dial STEP/DIR and intentionally do not appear on this controls sheet.
    text(c, "FRONT-PANEL INPUTS", 42, 390, 8.5, TEAL, True)
    line(c, 42, 381, W - 42, 381, LINE, .7)
    controls = [
        (85, 18, "Radio mode", "latching key"),
        (250, 19, "LP mode", "latching key"),
        (415, 4, "Standby", "contact plate"),
    ]
    for x, pin, heading, detail in controls:
        box(c, x, 293, 105, 58, heading, detail, BLUE, INK, 9.5, 6.4)
        text(c, f"GPIO{pin}", x + 52.5, 365, 7.5, GREEN, True, "center")
        line(c, x + 52.5, 360, x + 52.5, 351, GREEN, 1.0)
        line(c, x + 52.5, 293, x + 52.5, 274, INK, 1.0)
        ground(c, x + 52.5, 274)
    text(c, "Inputs use ESP32 internal pull-ups. An active contact closes the GPIO to GND.", W / 2, 250, 7.6, MUTED, False, "center")

    table(c, 42, 220, [105, 108, 168, 129], ["Module / input", "Power", "Interface", "Operational note"], [
        ("AS5600", "always-on 3.3 V", "I2C 0x36", "tracked in standby"),
        ("ADS1115", "always-on 5 V", "I2C 0x48 / A1", "I2C stays 3.3 V-safe"),
        ("PN532", "3.3 V", "I2C 0x24", "reader in I2C mode"),
        ("DFPlayer Mini", "switched +5 V", "UART 9600", "TX/RX crossed"),
        ("Radio / LP / standby", "ESP32 pull-ups", "GPIO18 / 19 / 4", "contacts close to GND"),
    ], row_h=15)
    footer(c, 2); c.showPage()


def page_outputs(c):
    title(c, 3, "Power rail, LEDs and standby", "A compact connected schematic for the switched rail and one repeated LED driver stage.")
    text(c, "+5 V", 60, 650, 10, RED, True); line(c, 90, 645, 500, 645, RED, 2.4)
    # Q1 is a high-side P-MOSFET. Q2 level-shifts the 3.3 V GPIO so Q1's gate
    # can reach the full 5 V source potential when off.
    mosfet(c, 335, 605, "Q1 P-MOS"); line(c,335,645,335,625,RED); line(c,335,585,335,545,RED); text(c,"+5V_SW",345,553,8,RED,True)
    resistor(c, 290, 645, 290, 605, "")
    text(c, "10k pull-up", 276, 624, 7.2, MUTED, False, "right")
    line(c, 290, 605, 307, 605, INK, 1.3)
    line(c, 290, 605, 290, 575, INK, 1.3)
    mosfet(c, 290, 545, "Q2 2N7000")
    line(c, 290, 575, 290, 565, INK, 1.3)
    line(c, 290, 525, 290, 505, INK, 1.3); ground(c, 290, 505)
    resistor(c, 90, 545, 245, 545, "1k series"); text(c,"GPIO14",52,541,8,GREEN,True)
    line(c, 245, 545, 262, 545, GREEN, 1.3)
    resistor(c, 245, 545, 245, 505, "")
    text(c, "10k pull-down", 232, 521, 7.2, MUTED, False, "right")
    ground(c, 245, 505)
    text(c, "GPIO14 HIGH turns Q2 on, pulls Q1 gate LOW and enables +5V_SW; GPIO LOW leaves the rail OFF.", 60, 481, 8.2, MUTED)
    text(c, "LED low-side driver - repeat this stage x5", 60, 455, 13, INK, True)
    line(c, 200, 420, 390, 420, RED, 1.2); text(c,"+5V_SW",160,417,7.5,RED,True)
    resistor(c,290,420,290,390,"220R"); led(c,290,375,"LED"); line(c,290,365,290,340); mosfet(c,290,320,"N-MOS"); line(c,290,300,290,280); ground(c,290,280)
    line(c,160,320,262,320,GREEN,1.0); text(c,"GPIO PWM",152,317,7,GREEN,True,"right")
    resistor(c,220,320,220,285,""); ground(c,220,285); text(c,"10k",207,300,6.8,MUTED,False,"right")
    text(c, "LED1 GPIO27 / LED2 GPIO25 / LED3 GPIO32 / LED4 GPIO33 / LED5 GPIO26", 297, 252, 7.5, MUTED, False, "center")
    text(c, "Each channel gets its own 220R resistor, N-MOS stage and 10k gate pull-down.", 297, 238, 7.5, MUTED, False, "center")
    table(c, 42, 215, [150, 140, 220], ["Circuit", "ESP32 control", "Required note"], [
        ("Switched rail", "GPIO14", "HIGH enables via Q2 level shifter; never PWM"),
        ("LED channels 1-5", "GPIO27 / 25 / 32 / 33 / 26", "One MOSFET stage per LED"),
        ("Standby plate", "GPIO4", "Plate to GND = active; open = standby"),
    ])
    footer(c, 3); c.showPage()


def page_dial(c):
    title(c, 4, "Dial motor and encoder", "Keep motor power separate from ESP32 logic; confirm the driver's ground arrangement.")
    # Compact signal-flow layout. Every wire terminates on its component box.
    box(c, 65, 610, 80, 36, "AS5600", "always-on 3.3 V", PALE_GREEN, GREEN, 9, 6.2)
    box(c, 215, 608, 90, 40, "ESP32", "position control", BLUE, INK, 10, 6.5)
    box(c, 390, 570, 90, 90, "DRV8825", "STEP / DIR / EN*", PEACH, AMBER, 10.5, 6.5)
    box(c, 390, 440, 90, 38, "NEMA17", "dial pointer", PEACH, AMBER, 10, 6.2)
    line(c, 145, 635, 215, 635, GREEN, 1.0); text(c, "SDA GPIO21", 180, 639, 6.5, GREEN, True, "center")
    line(c, 145, 621, 215, 621, GREEN, 1.0); text(c, "SCL GPIO22", 180, 609, 6.5, GREEN, True, "center")
    for yy, lab in [(600,"STEP"),(620,"DIR"),(640,"EN*")]:
        line(c, 305, yy, 390, yy, AMBER, 1.0)
        text(c, lab, 347, yy + 4, 6.8, AMBER, True, "center")
    # EN defaults inactive at boot through an external pull-up.
    resistor(c, 365, 640, 365, 680, "10k", GREEN)
    line(c, 353, 680, 435, 680, GREEN, 1.0)
    text(c, "+3.3 V", 365, 689, 6.8, GREEN, True, "center")
    # Four motor phases run vertically without crossing the motor body.
    for i, lab in enumerate(["A1","A2","B1","B2"]):
        xx = 405 + i * 20
        line(c, xx, 570, xx, 478, AMBER, 1.0)
        text(c, lab, xx - 4, 500, 6.8, AMBER, True, "right")
    # Motor power is a dedicated 12 V rail. The standard carrier accepts 3.3 V
    # logic inputs and has no separate VDD logic-supply pin.
    line(c, 480, 640, 545, 640, RED, 1.2); text(c, "+12 V MOTOR", 512, 650, 6.8, RED, True, "center"); text(c, "VMOT", 486, 644, 6.3, INK, True)
    line(c, 480, 615, 545, 615, INK, 1.0); ground(c, 545, 615); text(c, "GND", 545, 594, 6.3, INK, True, "center")
    line(c, 525, 640, 525, 630, INK, 1); line(c, 518, 630, 532, 630, INK, 1.1); line(c, 518, 626, 532, 626, INK, 1.1); line(c, 525, 626, 525, 615, INK, 1)
    text(c, "100uF", 535, 625, 6.2, MUTED)
    line(c, 435, 660, 435, 680, GREEN, 1.0); text(c, "nSLEEP + nRESET -> 3.3 V", 435, 689, 6.5, GREEN, True, "center")
    table(c, 42, 380, [100, 145, 265], ["DRV8825 pin", "Firmware mapping", "Build requirement"], [
        ("STEP", "GPIO13*", "Provisional - verify before flashing"),
        ("DIR", "GPIO5*", "Provisional - verify before flashing"),
        ("EN (active low)", "GPIO15*", "Add 10k pull-up to 3.3 V for coils-off boot"),
        ("VMOT / GND", "external 12 V", "100 uF electrolytic directly at the driver"),
        ("Logic inputs", "3.3 V signals", "No VDD pin; ESP32 and driver share GND"),
        ("nSLEEP / nRESET", "tie high together", "Required for STEP pulses to operate"),
    ], row_h=18)
    text(c, "Safety", 42, 215, 11, RED, True)
    text(c, "Set the DRV8825 current limit conservatively. Never connect or disconnect the motor while powered.", 42, 198, 8.8, MUTED)
    footer(c, 4); c.showPage()


def main():
    c = Canvas(str(OUT), pagesize=A4)
    c.setTitle("Radiola Circuit Wiring Reference")
    page_overview(c); page_controls(c); page_outputs(c); page_dial(c)
    c.save()
    print(OUT)


if __name__ == "__main__":
    main()
