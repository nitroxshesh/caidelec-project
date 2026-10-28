from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


BASE = Path(r"C:\Users\user\Documents\pfe project")
OUT = BASE / "uml_diagrams"
OUT.mkdir(exist_ok=True)

BLUE = "#2E6EBE"
RED = "#E50914"
INK = "#111827"
MUTED = "#6B7280"
FILL = "#F8FBFF"
LIGHT = "#EEF5FF"
PALE_RED = "#FDEDEE"
GREEN = "#15803D"


def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


F_TITLE = font(38, True)
F_H = font(24, True)
F = font(22)
F_S = font(18)
F_XS = font(16)


def center_text(draw, box, text, fnt, fill=INK, spacing=6):
    x1, y1, x2, y2 = box
    lines = []
    for raw in text.split("\n"):
        words = raw.split()
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            w = draw.textbbox((0, 0), trial, font=fnt)[2]
            if w <= (x2 - x1 - 28):
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
    heights = [draw.textbbox((0, 0), l, font=fnt)[3] for l in lines]
    total = sum(heights) + spacing * max(0, len(lines) - 1)
    y = y1 + (y2 - y1 - total) / 2
    for line, h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=fnt)
        x = x1 + (x2 - x1 - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += h + spacing


def round_box(draw, box, text, outline=BLUE, fill=FILL, fnt=F, radius=24, width=4):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)
    center_text(draw, box, text, fnt)


def ellipse(draw, box, text, outline=BLUE, fill="#FFFFFF", fnt=F_S, width=3):
    draw.ellipse(box, outline=outline, fill=fill, width=width)
    center_text(draw, box, text, fnt)


def arrow(draw, start, end, color=INK, width=3):
    draw.line((start, end), fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 14
    p1 = (x2 - size * math.cos(angle - 0.45), y2 - size * math.sin(angle - 0.45))
    p2 = (x2 - size * math.cos(angle + 0.45), y2 - size * math.sin(angle + 0.45))
    draw.polygon([end, p1, p2], fill=color)


def actor(draw, x, y, label):
    draw.ellipse((x - 22, y, x + 22, y + 44), outline=INK, width=3)
    draw.line((x, y + 44, x, y + 120), fill=INK, width=3)
    draw.line((x - 55, y + 72, x + 55, y + 72), fill=INK, width=3)
    draw.line((x, y + 120, x - 50, y + 190), fill=INK, width=3)
    draw.line((x, y + 120, x + 50, y + 190), fill=INK, width=3)
    bbox = draw.textbbox((0, 0), label, font=F)
    draw.text((x - (bbox[2] - bbox[0]) / 2, y + 202), label, font=F, fill=INK)


def draw_use_case():
    img = Image.new("RGB", (2600, 1550), "white")
    d = ImageDraw.Draw(img)
    d.text((940, 45), "Diagramme de cas d'utilisation - CAIDELEC", font=F_TITLE, fill=INK)
    round_box(d, (420, 140, 2440, 1420), "Systeme CAIDELEC", outline=BLUE, fill="#FFFFFF", fnt=F_H, radius=20)
    d.line((450, 760, 2410, 760), fill="#CBD5E1", width=3)
    d.text((480, 180), "Espace administrateur", font=F_H, fill=BLUE)
    d.text((480, 800), "Espace employe", font=F_H, fill=BLUE)
    actor(d, 170, 410, "Administrateur")
    actor(d, 170, 1030, "Employe")

    admin_cases = [
        ("Se connecter", 720, 330),
        ("Dashboard", 1180, 330),
        ("Gerer employes", 1640, 330),
        ("Planifier interventions", 2100, 330),
        ("Creer compte employe", 1640, 470),
        ("Calendrier", 720, 640),
        ("Export Excel", 1180, 640),
        ("Observer frais", 1640, 640),
        ("Verifier frais", 2100, 640),
    ]
    emp_cases = [
        ("Se connecter", 720, 990),
        ("Mes interventions", 1180, 990),
        ("Declarer frais", 1640, 990),
        ("Justificatif photo", 2100, 990),
        ("Mes frais", 1180, 1230),
    ]
    for text, x, y in admin_cases:
        box = (x - 170, y - 55, x + 170, y + 55)
        ellipse(d, box, text)
    for text, x, y in emp_cases:
        box = (x - 170, y - 55, x + 170, y + 55)
        ellipse(d, box, text)

    for text, x, y in admin_cases:
        if text != "Creer compte employe":
            d.line((250, 505, x - 170, y), fill="#374151", width=2)
    for text, x, y in emp_cases:
        d.line((250, 1125, x - 170, y), fill="#374151", width=2)
    # Include relationships are dashed and directional.
    y_pos = 385
    while y_pos < 415:
        d.line((1640, y_pos, 1640, min(y_pos + 12, 415)), fill=RED, width=3)
        y_pos += 34
    d.text((1670, 410), "<<include>>", font=F_XS, fill=RED)
    d.polygon([(1640, 415), (1628, 392), (1652, 392)], fill=RED)
    x_pos = 1810
    while x_pos < 1930:
        d.line((x_pos, 990, min(x_pos + 18, 1930), 990), fill=RED, width=3)
        x_pos += 34
    d.text((1835, 1012), "<<include>>", font=F_XS, fill=RED)
    d.polygon([(1930, 990), (1908, 978), (1908, 1002)], fill=RED)
    img.save(OUT / "01_use_case_caidelec.png")


def class_box(draw, x, y, w, h, name, attrs, methods=None):
    draw.rectangle((x, y, x + w, y + h), outline=BLUE, fill="#FFFFFF", width=4)
    draw.rectangle((x, y, x + w, y + 52), outline=BLUE, fill=LIGHT, width=4)
    center_text(draw, (x, y, x + w, y + 52), name, F_H)
    draw.line((x, y + 52, x + w, y + 52), fill=BLUE, width=3)
    yy = y + 68
    for a in attrs:
        draw.text((x + 20, yy), a, font=F_S, fill=INK)
        yy += 30
    if methods:
        draw.line((x, yy + 10, x + w, yy + 10), fill=BLUE, width=2)
        yy += 24
        for m in methods:
            draw.text((x + 20, yy), m, font=F_S, fill=MUTED)
            yy += 30
    return (x, y, x + w, y + h)


def draw_class():
    img = Image.new("RGB", (2500, 1500), "white")
    d = ImageDraw.Draw(img)
    d.text((890, 45), "Diagramme de classes - CAIDELEC", font=F_TITLE, fill=INK)
    user = class_box(d, 140, 210, 520, 430, "User", [
        "+ id: int", "+ username: string", "+ email: string", "+ hashed_password: string",
        "+ role: enum(admin, employe)", "+ employee_id: int?", "+ expense_limit: float?"
    ], ["+ login()", "+ getCurrentUser()"])
    employee = class_box(d, 980, 210, 520, 350, "Employee", [
        "+ id: int", "+ full_name: string", "+ role: string", "+ phone: string"
    ], ["+ createAccount()", "+ updateProfile()"])
    intervention = class_box(d, 1780, 210, 560, 480, "Intervention", [
        "+ id: int", "+ employee_id: int", "+ chantier: string", "+ nature_travaux: string",
        "+ observation: text", "+ start_date: date", "+ end_date: date", "+ status: string"
    ], ["+ validateDates()", "+ changeStatus()"])
    expense = class_box(d, 1780, 890, 560, 400, "Expense", [
        "+ id: int", "+ intervention_id: int", "+ transport: float", "+ repas: float",
        "+ autre: float", "+ receipt_photo: string", "+ status: string"
    ], ["+ total()", "+ attachReceipt()", "+ verifyLimit()"])

    arrow(d, (660, 390), (980, 390), color=RED, width=4)
    d.text((750, 350), "0..1 lie a 1", font=F_S, fill=INK)
    arrow(d, (1500, 390), (1780, 390), color=RED, width=4)
    d.text((1580, 350), "1 possede 0..*", font=F_S, fill=INK)
    arrow(d, (2060, 690), (2060, 890), color=RED, width=4)
    d.text((2080, 765), "1 contient 0..*", font=F_S, fill=INK)

    note = (150, 980, 1450, 1260)
    round_box(d, note, "Regles principales\n- Un employe voit uniquement ses interventions et ses frais.\n- Admin observe les frais sans creation/modification/suppression.\n- Un frais est accepte seulement si l'intervention appartient a l'employe.", outline=GREEN, fill="#F0FDF4", fnt=F)
    img.save(OUT / "02_class_caidelec.png")


def lifeline(draw, x, y, label):
    round_box(draw, (x - 160, y, x + 160, y + 70), label, outline=BLUE, fill=LIGHT, fnt=F)
    draw.line((x, y + 70, x, 1320), fill="#9CA3AF", width=2)


def message(draw, x1, x2, y, text, dashed=False, color=INK):
    if dashed:
        seg = 18
        pos = min(x1, x2)
        end = max(x1, x2)
        while pos < end:
            draw.line((pos, y, min(pos + seg, end), y), fill=color, width=3)
            pos += seg * 2
    else:
        draw.line((x1, y, x2, y), fill=color, width=3)
    direction = 1 if x2 > x1 else -1
    draw.polygon([(x2, y), (x2 - 18 * direction, y - 10), (x2 - 18 * direction, y + 10)], fill=color)
    draw.text((min(x1, x2) + 20, y - 34), text, font=F_XS, fill=color)


def draw_sequence():
    img = Image.new("RGB", (2600, 1500), "white")
    d = ImageDraw.Draw(img)
    d.text((710, 45), "Diagramme de sequence - Declaration et verification des frais", font=F_TITLE, fill=INK)
    xs = [210, 650, 1090, 1530, 1970, 2390]
    labels = ["Employe", "Frontend React", "API FastAPI", "Service Frais", "SQLite", "Admin"]
    for x, label in zip(xs, labels):
        lifeline(d, x, 150, label)
    y = 300
    steps = [
        (210, 650, "Saisir frais + justificatif", False),
        (650, 1090, "POST /expenses", False),
        (1090, 1530, "verifier droits", False),
        (1530, 1970, "chercher intervention", False),
        (1970, 1530, "employee_id", True),
        (1530, 1530, "controler appartenance", False),
        (1530, 1970, "enregistrer frais", False),
        (1970, 1530, "frais cree", True),
        (1530, 1090, "201 Created", True),
        (1090, 650, "confirmation", True),
        (650, 210, "frais en attente", True),
        (2390, 650, "Consulter frais", False),
        (650, 1090, "GET /expenses", False),
        (1090, 1970, "charger frais", False),
        (1970, 1090, "liste frais", True),
        (1090, 650, "donnees frais", True),
        (650, 2390, "afficher justificatif", True),
    ]
    for item in steps:
        if item[0] == item[1]:
            x = item[0]
            d.arc((x - 90, y - 20, x + 90, y + 70), 270, 90, fill=GREEN, width=3)
            d.text((x + 95, y), item[2], font=F_XS, fill=GREEN)
        else:
            message(d, item[0], item[1], y, item[2], dashed=item[3])
        y += 66
    round_box(d, (1210, 650, 1680, 740), "alt\nsi intervention != employe\nretour 403 Forbidden", outline=RED, fill=PALE_RED, fnt=F_XS)
    img.save(OUT / "03_sequence_frais_caidelec.png")


def diamond(draw, cx, cy, text):
    pts = [(cx, cy - 70), (cx + 150, cy), (cx, cy + 70), (cx - 150, cy)]
    draw.polygon(pts, outline=BLUE, fill="#FFFFFF")
    draw.line(pts + [pts[0]], fill=BLUE, width=3)
    center_text(draw, (cx - 120, cy - 45, cx + 120, cy + 45), text, F_XS)


def draw_activity():
    img = Image.new("RGB", (1800, 2400), "white")
    d = ImageDraw.Draw(img)
    d.text((470, 45), "Diagramme d'activite - Parcours utilisateur CAIDELEC", font=F_TITLE, fill=INK)
    x = 900
    d.ellipse((x - 30, 140, x + 30, 200), fill=INK)
    last = (x, 200)
    activities = [
        ("Ouvrir application", 260),
        ("Saisir identifiants", 390),
        ("Verifier login", 520),
    ]
    for txt, y in activities:
        arrow(d, last, (x, y - 50))
        round_box(d, (x - 260, y - 50, x + 260, y + 50), txt, fnt=F)
        last = (x, y + 50)
    arrow(d, last, (x, 670))
    diamond(d, x, 740, "Identifiants valides ?")
    message(d, x - 150, 420, 740, "non", color=RED)
    round_box(d, (160, 690, 420, 790), "Afficher erreur", outline=RED, fill=PALE_RED, fnt=F)
    arrow(d, (420, 740), (640, 390), color=RED)
    arrow(d, (x, 810), (x, 910))
    diamond(d, x, 980, "Role admin ?")

    admin_x = 500
    emp_x = 1300
    arrow(d, (750, 980), (admin_x, 1080), color=GREEN)
    d.text((630, 1010), "oui", font=F_S, fill=GREEN)
    arrow(d, (1050, 980), (emp_x, 1080), color=BLUE)
    d.text((1130, 1010), "non", font=F_S, fill=BLUE)

    admin_steps = ["Afficher dashboard", "Gerer employes", "Planifier interventions", "Observer / verifier frais", "Exporter Excel"]
    y = 1080
    prev = (admin_x, y - 40)
    for s in admin_steps:
        round_box(d, (admin_x - 250, y, admin_x + 250, y + 85), s, fnt=F_XS)
        arrow(d, prev, (admin_x, y))
        prev = (admin_x, y + 85)
        y += 145

    emp_steps = ["Afficher espace employe", "Consulter mes interventions", "Declarer frais", "Ajouter justificatif photo", "Consulter mes frais"]
    y = 1080
    prev = (emp_x, y - 40)
    for s in emp_steps:
        round_box(d, (emp_x - 250, y, emp_x + 250, y + 85), s, fnt=F_XS)
        arrow(d, prev, (emp_x, y))
        prev = (emp_x, y + 85)
        y += 145
    end_y = 1950
    arrow(d, prev, (emp_x, end_y))
    arrow(d, (admin_x, 1080 + len(admin_steps) * 145 - 60), (admin_x, end_y))
    d.ellipse((x - 42, end_y + 70, x + 42, end_y + 154), outline=INK, width=4)
    d.ellipse((x - 25, end_y + 87, x + 25, end_y + 137), fill=INK)
    arrow(d, (admin_x, end_y), (x - 42, end_y + 112))
    arrow(d, (emp_x, end_y), (x + 42, end_y + 112))
    img.save(OUT / "04_activity_caidelec.png")


PUML = {
    "01_use_case_caidelec.puml": """@startuml
left to right direction
actor "Administrateur" as Admin
actor "Employe" as Emp
rectangle "Systeme CAIDELEC" {
  usecase "Se connecter" as UC1
  usecase "Consulter dashboard" as UC2
  usecase "Gerer employes" as UC3
  usecase "Planifier interventions" as UC4
  usecase "Consulter calendrier" as UC5
  usecase "Exporter Excel" as UC6
  usecase "Observer frais" as UC7
  usecase "Verifier frais" as UC8
  usecase "Mes interventions" as UC9
  usecase "Declarer frais" as UC10
  usecase "Justificatif photo" as UC11
  usecase "Mes frais" as UC12
}
Admin --> UC1
Admin --> UC2
Admin --> UC3
Admin --> UC4
Admin --> UC5
Admin --> UC6
Admin --> UC7
Admin --> UC8
Emp --> UC1
Emp --> UC9
Emp --> UC10
Emp --> UC11
Emp --> UC12
UC10 .> UC11 : <<include>>
@enduml
""",
    "02_class_caidelec.puml": """@startuml
class User {
  +id: int
  +username: string
  +email: string
  +hashed_password: string
  +role: admin|employe
  +employee_id: int?
  +expense_limit: float?
}
class Employee {
  +id: int
  +full_name: string
  +role: string
  +phone: string
}
class Intervention {
  +id: int
  +employee_id: int
  +chantier: string
  +nature_travaux: string
  +observation: text
  +start_date: date
  +end_date: date
  +status: string
}
class Expense {
  +id: int
  +intervention_id: int
  +transport: float
  +repas: float
  +autre: float
  +receipt_photo: string
  +status: string
}
User "0..1" --> "1" Employee
Employee "1" --> "0..*" Intervention
Intervention "1" --> "0..*" Expense
@enduml
""",
    "03_sequence_frais_caidelec.puml": """@startuml
actor Employe
participant "Frontend React" as Front
participant "Backend FastAPI" as API
database "SQLite" as DB
Employe -> Front : Remplir frais + photo
Front -> API : POST /expenses
API -> DB : Verifier intervention
DB --> API : intervention.employee_id
alt intervention appartient a l'employe
  API -> DB : Enregistrer frais
  DB --> API : Frais cree
  API --> Front : 201 Created
  Front --> Employe : Confirmation
else non autorise
  API --> Front : 403 Forbidden
  Front --> Employe : Afficher erreur
end
@enduml
""",
    "04_activity_caidelec.puml": """@startuml
start
:Ouvrir application;
:Saisir identifiants;
if (Identifiants valides ?) then (oui)
  :Recuperer role;
  if (Role admin ?) then (oui)
    :Afficher dashboard;
    :Gerer employes;
    :Planifier interventions;
    :Observer et verifier frais;
    :Exporter Excel;
  else (employe)
    :Afficher espace employe;
    :Consulter mes interventions;
    :Declarer frais;
    :Ajouter justificatif photo;
    :Consulter mes frais;
  endif
else (non)
  :Afficher erreur login;
endif
stop
@enduml
""",
}


def write_guides():
    for name, content in PUML.items():
        (OUT / name).write_text(content, encoding="utf-8")
    guide = """# CAIDELEC - Etapes StarUML

## 1. Diagramme de cas d'utilisation
1. Creer un Use Case Diagram.
2. Ajouter deux actors : Administrateur et Employe.
3. Ajouter un subject/rectangle : Systeme CAIDELEC.
4. Ajouter les use cases admin : Se connecter, Consulter dashboard, Gerer employes, Planifier interventions, Consulter calendrier, Exporter Excel, Observer frais, Verifier frais.
5. Ajouter les use cases employe : Se connecter, Mes interventions, Declarer frais, Justificatif photo, Mes frais.
6. Relier Admin vers les use cases admin avec Association.
7. Relier Employe vers les use cases employe avec Association.
8. Ajouter une dependance include de Declarer frais vers Justificatif photo.
9. Mettre le diagramme en paysage : acteurs a gauche, cas d'utilisation en deux lignes.

## 2. Diagramme de classes
1. Creer un Class Diagram.
2. Ajouter les classes User, Employee, Intervention et Expense.
3. Ajouter les attributs exactement comme dans l'image ou le fichier PlantUML.
4. Relation User vers Employee : 0..1 vers 1.
5. Relation Employee vers Intervention : 1 vers 0..*.
6. Relation Intervention vers Expense : 1 vers 0..*.
7. Ajouter une note de regles : Admin observe les frais, Employe gere uniquement ses frais.

## 3. Diagramme de sequence
1. Creer un Sequence Diagram.
2. Ajouter lifelines : Employe, Frontend React, Backend FastAPI, Service Frais, SQLite.
3. Ajouter le scenario : saisie frais + photo, POST /expenses, verification intervention, sauvegarde ou refus 403.
4. Ajouter fragment alt : intervention appartient a l'employe / intervention non autorisee.
5. Garder les messages courts pour que le diagramme reste lisible.

## 4. Diagramme d'activite
1. Creer un Activity Diagram.
2. Ajouter start, login, verification identifiants.
3. Ajouter decision role admin.
4. Branche admin : dashboard, employes, interventions, verifier frais, export Excel.
5. Branche employe : mes interventions, declarer frais, justificatif photo, mes frais.
6. Ajouter final node.
"""
    (OUT / "StarUML-Etapes-CAIDELEC.md").write_text(guide, encoding="utf-8")


def main():
    draw_use_case()
    draw_class()
    draw_sequence()
    draw_activity()
    write_guides()
    print(OUT)


if __name__ == "__main__":
    main()
