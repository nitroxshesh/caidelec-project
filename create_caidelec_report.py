from pathlib import Path
from datetime import date

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont


BASE = Path(r"C:\Users\user\Documents\pfe project")
OUT = BASE / "Rapport-Stage-CAIDELEC.docx"
ASSET_DIR = BASE / "rapport_assets"
LOGO = Path(r"C:\Users\user\caidelec-frontend\src\assets\caidelec-logo.jpeg")

BLUE = "2E6EBE"
RED = "E50914"
TEAL = "2F8A9B"
LIGHT_BLUE = "D9EAF7"
PALE_YELLOW = "F6E59A"
GRAY = "E6E6E6"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_border(cell, **kwargs):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        if edge in kwargs:
            edge_data = kwargs.get(edge)
            tag = "w:{}".format(edge)
            element = borders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                borders.append(element)
            for key in ["sz", "val", "color", "space"]:
                if key in edge_data:
                    element.set(qn("w:{}".format(key)), str(edge_data[key]))


def add_outer_border(section):
    sect_pr = section._sectPr
    pg_borders = OxmlElement("w:pgBorders")
    pg_borders.set(qn("w:offsetFrom"), "page")
    for edge in ("top", "left", "bottom", "right"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "double")
        tag.set(qn("w:sz"), "8")
        tag.set(qn("w:space"), "16")
        tag.set(qn("w:color"), "000000")
        pg_borders.append(tag)
    sect_pr.append(pg_borders)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def style_run(run, size=None, bold=False, italic=False, color=None, font="Times New Roman"):
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:ascii"), font)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), font)
    run.bold = bold
    run.italic = italic
    if size:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def add_paragraph(doc, text="", align=None, first_line=True, spacing_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(spacing_after)
    if first_line:
        p.paragraph_format.first_line_indent = Cm(0.7)
    if align:
        p.alignment = align
    r = p.add_run(text)
    style_run(r, 12)
    return p


def add_title(doc, text, level=1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if level == 1 else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10 if level == 1 else 6)
    p.paragraph_format.space_after = Pt(12 if level == 1 else 6)
    r = p.add_run(text)
    if level == 1:
        style_run(r, 20, bold=True)
    elif level == 2:
        style_run(r, 15, bold=True, color=BLUE)
    else:
        style_run(r, 13, bold=True)
    return p


def add_chapter(doc, number, title):
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(120)
    r = p.add_run(f"Chapitre {number}")
    style_run(r, 24, bold=True, color=BLUE)
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_before = Pt(18)
    r2 = p2.add_run(title)
    style_run(r2, 20, bold=True)
    doc.add_page_break()


def add_table(doc, headers, rows, widths=None, header_fill=LIGHT_BLUE):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    hdr = table.rows[0]
    set_repeat_table_header(hdr)
    for i, header in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = header
        set_cell_shading(cell, header_fill)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                style_run(run, 10, bold=True)
        set_cell_border(cell, top={"val": "single", "sz": "8", "color": "000000"}, bottom={"val": "single", "sz": "8", "color": "000000"}, left={"val": "single", "sz": "8", "color": "000000"}, right={"val": "single", "sz": "8", "color": "000000"})
    for row_data in rows:
        row = table.add_row()
        for i, value in enumerate(row_data):
            cell = row.cells[i]
            cell.text = str(value)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(2)
                for run in p.runs:
                    style_run(run, 9.5)
            set_cell_border(cell, top={"val": "single", "sz": "4", "color": "808080"}, bottom={"val": "single", "sz": "4", "color": "808080"}, left={"val": "single", "sz": "4", "color": "808080"}, right={"val": "single", "sz": "4", "color": "808080"})
    if widths:
        for row in table.rows:
            for idx, width in enumerate(widths):
                row.cells[idx].width = Cm(width)
    doc.add_paragraph()
    return table


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    style_run(r, 10, italic=True, color="555555")


def get_font(size=24, bold=False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def draw_box(draw, xy, text, fill, outline, font, text_fill="#111111"):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=18, fill=fill, outline=outline, width=3)
    lines = []
    for part in text.split("\n"):
        words = part.split()
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if draw.textbbox((0, 0), test, font=font)[2] - draw.textbbox((0, 0), test, font=font)[0] < (x2 - x1 - 26):
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    total_h = len(lines) * (font.size + 5)
    y = y1 + ((y2 - y1) - total_h) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        draw.text((x1 + ((x2 - x1) - (bbox[2] - bbox[0])) / 2, y), line, font=font, fill=text_fill)
        y += font.size + 5


def create_diagrams():
    ASSET_DIR.mkdir(exist_ok=True)
    title_font = get_font(28, True)
    font = get_font(22)
    small = get_font(18)

    img = Image.new("RGB", (1600, 700), "white")
    d = ImageDraw.Draw(img)
    boxes = [
        (80, 250, 360, 410, "Utilisateur\nAdmin / Employe"),
        (470, 250, 750, 410, "Frontend\nReact Vite"),
        (860, 250, 1140, 410, "Backend\nFastAPI"),
        (1250, 250, 1520, 410, "Base de donnees\nSQLite"),
    ]
    d.text((560, 60), "Architecture generale de la solution", font=title_font, fill="#111111")
    for x1, y1, x2, y2, text in boxes:
        draw_box(d, (x1, y1, x2, y2), text, "#F7FBFF", f"#{BLUE}", font)
    for x in [360, 750, 1140]:
        d.line((x + 20, 330, x + 90, 330), fill=f"#{RED}", width=5)
        d.polygon([(x + 90, 330), (x + 72, 318), (x + 72, 342)], fill=f"#{RED}")
    d.text((845, 505), "JWT, API REST, CRUD, controle des roles", font=small, fill="#444444")
    arch_path = ASSET_DIR / "architecture.png"
    img.save(arch_path)

    img = Image.new("RGB", (1600, 900), "white")
    d = ImageDraw.Draw(img)
    d.text((560, 45), "Diagramme de cas d'utilisation", font=title_font, fill="#111111")
    draw_box(d, (75, 185, 315, 285), "Admin", "#FDEDEE", f"#{RED}", font)
    draw_box(d, (75, 610, 315, 710), "Employe", "#FDEDEE", f"#{RED}", font)
    use_cases = [
        (500, 130, 930, 210, "Consulter le tableau de bord"),
        (500, 230, 930, 310, "Gerer les employes"),
        (500, 330, 930, 410, "Planifier les interventions"),
        (500, 430, 930, 510, "Verifier les interventions"),
        (500, 530, 930, 610, "Observer les frais"),
        (500, 650, 930, 730, "Consulter ses interventions"),
        (500, 750, 930, 830, "Declarer ses frais avec justificatif"),
    ]
    for case in use_cases:
        draw_box(d, case[:4], case[4], "#F8FBFF", f"#{BLUE}", small)
    for target_y in [170, 270, 370, 470, 570]:
        d.line((315, 235, 500, target_y), fill="#555555", width=2)
    for target_y in [690, 790]:
        d.line((315, 660, 500, target_y), fill="#555555", width=2)
    use_case_path = ASSET_DIR / "use_cases.png"
    img.save(use_case_path)

    img = Image.new("RGB", (1700, 900), "white")
    d = ImageDraw.Draw(img)
    d.text((640, 40), "Diagramme de classes simplifie", font=title_font, fill="#111111")
    classes = [
        (80, 170, 430, 430, "User\nid, username, email\nrole, employee_id\nexpense_limit"),
        (560, 170, 910, 430, "Employee\nid, full_name\nrole, phone"),
        (1040, 170, 1420, 430, "Intervention\nid, chantier\nnature_travaux\nstart_date, end_date\nstatus, observation"),
        (1040, 560, 1420, 800, "Expense\nid, intervention_id\ntransport, repas, autre\nreceipt_photo, status"),
    ]
    for x1, y1, x2, y2, text in classes:
        draw_box(d, (x1, y1, x2, y2), text, "#FFFFFF", f"#{BLUE}", small)
    d.line((430, 300, 560, 300), fill=f"#{RED}", width=4)
    d.text((465, 270), "0..1", font=small, fill="#333333")
    d.line((910, 300, 1040, 300), fill=f"#{RED}", width=4)
    d.text((950, 270), "1..*", font=small, fill="#333333")
    d.line((1230, 430, 1230, 560), fill=f"#{RED}", width=4)
    d.text((1240, 490), "1..*", font=small, fill="#333333")
    class_path = ASSET_DIR / "classes.png"
    img.save(class_path)

    img = Image.new("RGB", (1700, 900), "white")
    d = ImageDraw.Draw(img)
    d.text((555, 45), "Sequence : declaration et verification des frais", font=title_font, fill="#111111")
    actors = [("Employe", 160), ("Frontend", 520), ("API FastAPI", 880), ("Base SQLite", 1240)]
    for name, x in actors:
        draw_box(d, (x - 120, 130, x + 120, 210), name, "#F8FBFF", f"#{BLUE}", small)
        d.line((x, 210, x, 810), fill="#888888", width=2)
    steps = [
        (160, 520, 280, "Remplir formulaire + photo"),
        (520, 880, 370, "POST /expenses"),
        (880, 1240, 460, "Verifier intervention/employe"),
        (1240, 880, 550, "Resultat"),
        (880, 520, 640, "201 Created ou 403"),
        (520, 160, 730, "Afficher confirmation"),
    ]
    for x1, x2, y, label in steps:
        d.line((x1, y, x2, y), fill=f"#{RED}", width=4)
        direction = 1 if x2 > x1 else -1
        d.polygon([(x2, y), (x2 - 18 * direction, y - 10), (x2 - 18 * direction, y + 10)], fill=f"#{RED}")
        d.text((min(x1, x2) + 18, y - 35), label, font=small, fill="#222222")
    seq_path = ASSET_DIR / "sequence_expenses.png"
    img.save(seq_path)

    return arch_path, use_case_path, class_path, seq_path


def setup_document():
    doc = Document()
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    section.top_margin = Cm(1.6)
    section.bottom_margin = Cm(1.6)
    section.left_margin = Cm(1.8)
    section.right_margin = Cm(1.8)
    add_outer_border(section)
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    normal.font.size = Pt(12)
    return doc


def add_header_footer(doc):
    for section in doc.sections:
        header = section.header
        if header.paragraphs:
            p = header.paragraphs[0]
        else:
            p = header.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if LOGO.exists():
            run = p.add_run()
            run.add_picture(str(LOGO), width=Cm(3.0))
        footer = section.footer
        table = footer.add_table(rows=1, cols=3, width=Inches(7.0))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.rows[0].cells[0].text = "CAIDELEC"
        table.rows[0].cells[1].text = "Rapport de stage / PFE"
        table.rows[0].cells[2].text = "2025/2026"
        for cell in table.rows[0].cells:
            for par in cell.paragraphs:
                par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in par.runs:
                    style_run(run, 8, color="555555")


def add_cover(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if LOGO.exists():
        p.add_run().add_picture(str(LOGO), width=Cm(9.2))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(28)
    r = p.add_run("Projet de fin d'etudes")
    style_run(r, 20, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Memoire presente en vue de l'obtention du diplome")
    style_run(r, 13)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Licence / Genie des Systemes d'Information")
    style_run(r, 13)

    doc.add_paragraph()
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.rows[0].cells[0]
    cell.width = Cm(15)
    set_cell_border(cell, top={"val": "single", "sz": "14", "color": "000000"}, bottom={"val": "single", "sz": "14", "color": "000000"}, left={"val": "single", "sz": "14", "color": "000000"}, right={"val": "single", "sz": "14", "color": "000000"})
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("Systeme de gestion de la planification des interventions quotidiennes\net des frais de leurs deplacements")
    style_run(r, 20, bold=True)

    doc.add_paragraph()
    info = doc.add_table(rows=4, cols=2)
    info.alignment = WD_TABLE_ALIGNMENT.CENTER
    rows = [
        ("Realise par :", "[Nom et prenom]"),
        ("Encadrant academique :", "[Nom de l'encadrant]"),
        ("Encadrant professionnel :", "[Nom de l'encadrant]"),
        ("Organisme d'accueil :", "CAIDELEC - Travaux et equipements electriques"),
    ]
    for i, (left, right) in enumerate(rows):
        info.rows[i].cells[0].text = left
        info.rows[i].cells[1].text = right
        for j, cell in enumerate(info.rows[i].cells):
            for par in cell.paragraphs:
                for run in par.runs:
                    style_run(run, 11, bold=(j == 0))
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Annee universitaire : 2025/2026")
    style_run(r, 12, bold=True)
    doc.add_page_break()


def add_front_matter(doc):
    add_title(doc, "Dedicace")
    for line in [
        "A mes parents, pour leur soutien, leurs sacrifices et leurs encouragements constants.",
        "A ma famille, pour sa confiance et son accompagnement tout au long de mon parcours.",
        "A mes enseignants et encadrants, pour leurs conseils et leur disponibilite.",
        "A toutes les personnes qui ont contribue, de pres ou de loin, a la realisation de ce travail.",
    ]:
        add_paragraph(doc, line, WD_ALIGN_PARAGRAPH.CENTER, first_line=False, spacing_after=14)
    doc.add_page_break()

    add_title(doc, "Remerciements")
    paragraphs = [
        "Je tiens a exprimer ma profonde gratitude a toutes les personnes qui ont contribue a la realisation de ce projet de fin d'etudes. Leurs conseils, leur disponibilite et leur confiance ont permis de transformer une idee fonctionnelle en une application concrete et exploitable.",
        "Je remercie particulierement mon encadrant academique pour son suivi, ses remarques et son accompagnement methodologique. Je remercie egalement l'encadrant professionnel et l'equipe de CAIDELEC pour les informations metier fournies concernant la planification quotidienne des interventions, le suivi des techniciens et la gestion des frais de deplacement.",
        "Mes remerciements s'adressent enfin a ma famille, mes amis et mes camarades pour leur soutien moral, leurs encouragements et leur presence durant les differentes etapes de ce travail.",
    ]
    for para in paragraphs:
        add_paragraph(doc, para, first_line=False)
    doc.add_page_break()

    add_title(doc, "Resume")
    add_paragraph(doc, "Ce rapport presente la conception et la realisation d'une application web de gestion de la planification des interventions quotidiennes et des frais de deplacement pour CAIDELEC. L'objectif principal du projet consiste a centraliser les informations liees aux employes, aux chantiers, aux affectations journalieres, aux justificatifs de frais et a leur verification par l'administration.")
    add_paragraph(doc, "La solution developpee repose sur une architecture web moderne composee d'un backend FastAPI, d'une base de donnees SQLite geree avec SQLAlchemy, d'une authentification par jeton JWT et d'une interface frontend React Vite. Le systeme distingue deux profils principaux : l'administrateur, qui supervise les donnees et verifie les frais, et l'employe, qui consulte ses interventions et declare ses propres frais avec preuve justificative.")
    add_paragraph(doc, "Le projet propose egalement un tableau de bord, un calendrier professionnel des interventions, une page de details journaliers, ainsi qu'un export Excel au format des affectations journalieres. Ces fonctionnalites permettent de reduire les erreurs de suivi, de faciliter la verification et d'ameliorer la tracabilite des operations terrain.")
    p = doc.add_paragraph()
    r = p.add_run("Mots-cles : ")
    style_run(r, 12, bold=True, color=BLUE)
    r = p.add_run("CAIDELEC, interventions, frais de deplacement, FastAPI, React, JWT, SQLite, export Excel, verification.")
    style_run(r, 12)
    doc.add_page_break()

    add_title(doc, "Abstract")
    add_paragraph(doc, "This report presents the design and implementation of a web application for managing daily intervention planning and travel expenses at CAIDELEC. The platform centralizes employees, work sites, daily assignments, expense receipts and administrative verification.")
    add_paragraph(doc, "The solution is based on FastAPI, SQLAlchemy, SQLite, JWT authentication and a React Vite frontend. It provides two main roles: administrator, who supervises the system and verifies expenses, and employee, who consults assigned interventions and submits personal travel expenses with supporting proof.")
    add_paragraph(doc, "The application includes a dashboard, a professional intervention calendar, daily intervention detail pages and Excel export. These features improve traceability, reduce manual errors and support better operational follow-up.")
    p = doc.add_paragraph()
    r = p.add_run("Keywords: ")
    style_run(r, 12, bold=True, color=BLUE)
    r = p.add_run("CAIDELEC, intervention planning, travel expenses, FastAPI, React, JWT, SQLite, Excel export.")
    style_run(r, 12)
    doc.add_page_break()

    add_title(doc, "Table des matieres")
    toc = [
        "Introduction generale",
        "Chapitre 1 : Contexte general et cahier des charges",
        "Chapitre 2 : Analyse et conception",
        "Chapitre 3 : Realisation technique",
        "Chapitre 4 : Tests, validation et perspectives",
        "Conclusion generale",
        "Bibliographie et webographie",
        "Annexes",
    ]
    for item in toc:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(1.2)
        r = p.add_run(item)
        style_run(r, 12)
    doc.add_page_break()


def add_intro(doc):
    add_title(doc, "Introduction generale")
    for para in [
        "La gestion quotidienne des interventions terrain constitue un enjeu important pour les entreprises de travaux electriques. Chaque jour, des equipes sont affectees a differents chantiers, avec des informations qui doivent etre communiquees rapidement : le chantier concerne, la nature des travaux, les intervenants, l'etat d'avancement, les observations et les frais associes aux deplacements.",
        "Dans un fonctionnement manuel, ces informations sont souvent dispersees entre feuilles Excel, messages, appels telephoniques et documents papier. Cette dispersion rend le suivi difficile, limite la tracabilite et complique la verification des frais declares par les employes.",
        "Le present projet a pour objectif de proposer une solution web simple, professionnelle et adaptee aux besoins de CAIDELEC. L'application permet de planifier les interventions, suivre leur avancement, consulter un calendrier, generer des exports Excel conformes au format interne et verifier les frais de deplacement avec justificatif.",
        "Ce rapport decrit les differentes etapes de realisation du projet : l'analyse du besoin, la conception fonctionnelle et technique, la mise en oeuvre avec FastAPI et React, puis les tests et les perspectives d'amelioration.",
    ]:
        add_paragraph(doc, para)


def add_chapter1(doc):
    add_chapter(doc, 1, "Contexte general et cahier des charges")
    add_title(doc, "1.1 Presentation de l'organisme d'accueil", 2)
    add_paragraph(doc, "CAIDELEC est une entreprise specialisee dans les travaux et equipements electriques. Son activite implique des interventions regulieres sur differents chantiers, avec mobilisation d'employes, de techniciens et de moyens de deplacement. Le suivi operationnel necessite une organisation claire afin de connaitre les affectations du jour, les travaux en cours et les frais engages.")
    add_paragraph(doc, "Le logo et l'identite visuelle de CAIDELEC, bases principalement sur le bleu et le rouge, ont ete pris en compte dans l'interface afin de donner a la solution une apparence coherente avec l'image de l'entreprise.")

    add_title(doc, "1.2 Problematique", 2)
    add_paragraph(doc, "La problematique principale peut etre formulee ainsi : comment mettre en place une application simple permettant de planifier les interventions quotidiennes, d'assurer leur suivi par l'administration et de verifier les frais de deplacement declares par les employes ?")
    add_paragraph(doc, "Cette problematique inclut plusieurs difficultes : la centralisation des donnees, la separation des droits d'acces, la verification des frais, l'edition d'un planning journalier lisible et l'obtention rapide d'indicateurs sur l'activite.")

    add_title(doc, "1.3 Objectifs du projet", 2)
    add_table(doc, ["Objectif", "Description"], [
        ("Centraliser les donnees", "Regrouper les employes, interventions et frais dans une base de donnees unique."),
        ("Planifier les interventions", "Permettre a l'administrateur de creer et organiser les affectations par date."),
        ("Suivre les employes", "Associer chaque intervention a un employe et creer automatiquement son compte utilisateur."),
        ("Controler les frais", "Autoriser uniquement l'employe concerne a declarer ses frais, avec justificatif photo."),
        ("Superviser l'activite", "Mettre a disposition un dashboard, un calendrier et des tableaux de consultation."),
        ("Exporter les affectations", "Generer un fichier Excel professionnel au format des affectations journalieres."),
    ], widths=[5, 11])

    add_title(doc, "1.4 Cahier des charges fonctionnel", 2)
    add_table(doc, ["Module", "Fonctionnalites attendues"], [
        ("Authentification", "Connexion securisee par nom d'utilisateur et mot de passe, generation d'un jeton JWT, endpoint de recuperation du profil courant."),
        ("Employes", "Ajout, consultation, modification et suppression des employes par l'administrateur, avec creation possible du compte utilisateur lie."),
        ("Interventions", "Creation des interventions avec chantier, nature des travaux, dates debut/fin, statut et observation."),
        ("Frais", "Declaration des frais par l'employe uniquement pour ses propres interventions, avec limite individuelle et justificatif."),
        ("Verification", "Consultation par l'administrateur des frais et des interventions afin de valider ou observer les declarations."),
        ("Dashboard", "Statistiques, calendrier, acces rapide aux donnees et vue professionnelle pour la presentation."),
        ("Export Excel", "Generation d'un tableau d'affectations journalieres reprenant le logo, la date, les chantiers, les intervenants et les observations."),
    ], widths=[4, 12])

    add_title(doc, "1.5 Contraintes techniques", 2)
    add_table(doc, ["Contrainte", "Choix retenu"], [
        ("Simplicite de deploiement", "Utilisation de SQLite pendant la phase de developpement."),
        ("API claire", "Backend organise autour de routes REST FastAPI."),
        ("Interface moderne", "Frontend React Vite avec navigation par roles."),
        ("Securite", "JWT, mots de passe haches, controle des permissions cote backend."),
        ("Maintenance", "Code limite aux modules necessaires sans complexite inutile."),
    ], widths=[5, 11])


def add_chapter2(doc, diagrams):
    add_chapter(doc, 2, "Analyse et conception")
    add_title(doc, "2.1 Acteurs du systeme", 2)
    add_table(doc, ["Acteur", "Role dans le systeme"], [
        ("Administrateur", "Gere les employes, planifie les interventions, consulte le dashboard, observe les frais et verifie les informations declarees."),
        ("Employe", "Consulte uniquement ses interventions, declare ses frais de deplacement et joint une preuve justificative."),
    ], widths=[4, 12])

    add_title(doc, "2.2 Diagramme de cas d'utilisation", 2)
    doc.add_picture(str(diagrams[1]), width=Cm(16))
    add_caption(doc, "Figure 1 : Cas d'utilisation principaux de l'application CAIDELEC")
    add_paragraph(doc, "Le diagramme montre la separation entre les actions d'administration et les actions reservees a l'employe. L'administrateur supervise le systeme, tandis que l'employe intervient sur ses propres donnees afin de garantir la confidentialite et la coherence des operations.")

    add_title(doc, "2.3 Regles de gestion", 2)
    add_table(doc, ["Code", "Regle"], [
        ("RG01", "Un utilisateur possede un role unique : admin ou employe."),
        ("RG02", "Un compte employe doit etre lie a une fiche employe par employee_id."),
        ("RG03", "Un employe ne peut consulter que ses propres interventions."),
        ("RG04", "Un employe ne peut declarer des frais que pour une intervention qui lui appartient."),
        ("RG05", "L'administrateur observe les frais mais ne les cree pas, ne les modifie pas et ne les supprime pas."),
        ("RG06", "La date de fin d'une intervention doit etre superieure ou egale a la date de debut."),
        ("RG07", "Un justificatif photo peut etre associe aux frais pour permettre la verification."),
        ("RG08", "Une limite de frais peut etre definie pour chaque utilisateur employe."),
    ], widths=[3, 13])

    add_title(doc, "2.4 Diagramme de classes", 2)
    doc.add_picture(str(diagrams[2]), width=Cm(16))
    add_caption(doc, "Figure 2 : Diagramme de classes simplifie")
    add_paragraph(doc, "La conception repose sur quatre entites principales. User represente le compte de connexion, Employee represente la fiche metier de l'employe, Intervention contient les informations de planification et Expense regroupe les frais lies a une intervention.")

    add_title(doc, "2.5 Modele relationnel", 2)
    add_table(doc, ["Table", "Champs principaux", "Relations"], [
        ("users", "id, username, email, hashed_password, role, employee_id, expense_limit", "employee_id reference employees.id"),
        ("employees", "id, full_name, role, phone", "Un employe peut avoir plusieurs interventions"),
        ("interventions", "id, employee_id, chantier, nature_travaux, observation, start_date, end_date, status", "employee_id reference employees.id"),
        ("expenses", "id, intervention_id, transport, repas, autre, receipt_photo, status", "intervention_id reference interventions.id"),
    ], widths=[3, 7, 6])

    add_title(doc, "2.6 Sequence de declaration des frais", 2)
    doc.add_picture(str(diagrams[3]), width=Cm(16))
    add_caption(doc, "Figure 3 : Sequence de declaration et verification des frais")
    add_paragraph(doc, "Lorsqu'un employe declare des frais, le backend verifie d'abord que l'intervention choisie appartient bien a cet employe. Cette verification est essentielle pour eviter qu'un utilisateur ajoute des frais sur une intervention qui ne lui est pas assignee.")


def add_chapter3(doc, diagrams):
    add_chapter(doc, 3, "Realisation technique")
    add_title(doc, "3.1 Architecture generale", 2)
    doc.add_picture(str(diagrams[0]), width=Cm(16))
    add_caption(doc, "Figure 4 : Architecture technique de l'application")
    add_paragraph(doc, "L'application CAIDELEC suit une architecture client-serveur. Le frontend React Vite assure l'affichage et l'interaction utilisateur. Le backend FastAPI expose les endpoints REST, applique les regles de securite et communique avec la base SQLite a travers SQLAlchemy.")

    add_title(doc, "3.2 Technologies utilisees", 2)
    add_table(doc, ["Composant", "Technologie", "Role"], [
        ("Backend", "FastAPI", "Creation de l'API REST, validation des routes et gestion des reponses."),
        ("ORM", "SQLAlchemy", "Mapping entre les classes Python et les tables SQLite."),
        ("Base de donnees", "SQLite", "Stockage local simple pour la phase de developpement."),
        ("Securite", "JWT + Passlib", "Authentification, hachage des mots de passe et identification de l'utilisateur connecte."),
        ("Frontend", "React Vite", "Interface utilisateur rapide et modulaire."),
        ("HTTP", "Axios", "Communication entre React et l'API FastAPI."),
        ("Navigation", "React Router", "Pages par module et protection selon les roles."),
        ("Export", "ExcelJS ou librairie equivalente", "Generation de fichiers Excel professionnels."),
    ], widths=[4, 4, 8])

    add_title(doc, "3.3 Backend FastAPI", 2)
    for para in [
        "Le backend est organise autour de modules correspondant aux besoins metier : authentification, employes, interventions et frais. Chaque route applique les permissions necessaires afin d'eviter qu'un utilisateur accede a des donnees qui ne lui appartiennent pas.",
        "L'endpoint d'authentification permet de connecter un utilisateur et de generer un token JWT. L'endpoint /auth/me retourne l'identite de l'utilisateur courant, notamment son role et son employee_id, ce qui permet au frontend d'adapter l'interface.",
        "Les routes employees sont reservees a l'administrateur. Lors de la creation d'un employe, un compte utilisateur peut etre cree et lie a la fiche employe. Cette fonctionnalite evite la double saisie et rend l'acces de l'employe plus rapide.",
    ]:
        add_paragraph(doc, para)
    add_table(doc, ["Endpoint", "Methode", "Permission", "Description"], [
        ("/auth/login", "POST", "Public", "Connexion et recuperation du token."),
        ("/auth/me", "GET", "Utilisateur connecte", "Retourne id, username, email, role et employee_id."),
        ("/employees", "GET/POST/PUT/DELETE", "Admin", "Gestion des employes."),
        ("/interventions", "GET", "Admin/Employe", "Admin voit tout, employe voit ses interventions."),
        ("/interventions", "POST/PUT/DELETE", "Admin", "Planification et modification des interventions."),
        ("/expenses", "GET", "Admin/Employe", "Admin observe tout, employe voit ses frais."),
        ("/expenses", "POST/PUT/DELETE", "Employe", "Gestion des frais personnels uniquement."),
    ], widths=[4, 3, 4, 6])

    add_title(doc, "3.4 Frontend React", 2)
    for para in [
        "Le frontend propose une interface professionnelle inspiree des couleurs du logo CAIDELEC. Les pages sont volontairement minimalistes pour une presentation PFE : titre clair, formulaires, tableaux, boutons et navigation. Les textes explicatifs superflus ont ete retires afin de garder une interface propre.",
        "La navigation est adaptee au role de l'utilisateur. L'administrateur accede au dashboard, aux employes, aux interventions et a l'observation des frais. L'employe accede a ses interventions et a ses propres frais.",
        "Le mode clair/sombre est accessible par une petite icone, ce qui permet d'ajuster l'apparence sans alourdir l'interface.",
    ]:
        add_paragraph(doc, para)

    add_title(doc, "3.5 Gestion des interventions", 2)
    add_paragraph(doc, "Une intervention contient le chantier, la nature des travaux, les dates de debut et de fin, le statut et les observations. Le passage d'une seule date a start_date/end_date permet de representer des travaux sur plusieurs jours.")
    add_table(doc, ["Champ", "Description"], [
        ("chantier", "Nom du chantier ou du site d'intervention."),
        ("nature_travaux", "Type de travaux realises : electricite, maintenance, pose, raccordement, etc."),
        ("start_date", "Date de debut de l'intervention."),
        ("end_date", "Date de fin, obligatoirement superieure ou egale a la date de debut."),
        ("status", "Etat de l'intervention : planned, en cours, terminee, verifiee selon le workflow retenu."),
        ("observation", "Informations complementaires utiles au suivi."),
    ], widths=[5, 11])

    add_title(doc, "3.6 Gestion des frais et verification", 2)
    add_paragraph(doc, "Le module frais est construit autour d'un principe de controle : seul l'employe affecte a l'intervention peut creer des frais pour cette intervention. L'administrateur conserve une vue globale en mode observation afin de verifier les montants, les statuts et les justificatifs.")
    add_paragraph(doc, "L'ajout d'une photo justificative permet de comparer la declaration avec une preuve concrete, par exemple un ticket de carburant, une facture de transport ou un recu de repas. Cette preuve facilite la validation et limite les erreurs de saisie.")

    add_title(doc, "3.7 Export Excel des affectations journalieres", 2)
    add_paragraph(doc, "L'application integre un export Excel au format des affectations journalieres utilise par l'entreprise. Le fichier reprend le logo CAIDELEC, la date, les chantiers, la nature des travaux, les intervenants, les contacts, l'accompagnement administratif et les observations.")
    add_table(doc, ["Colonne Excel", "Contenu"], [
        ("CHANTIER", "Nom du chantier ou client concerne."),
        ("NATURE DES TRAVAUX", "Description synthetique des travaux."),
        ("INTERVENANTS", "Employe affecte ou equipe."),
        ("CONTACTS INTERVENANTS", "Telephone de l'employe si disponible."),
        ("ACCOMPAGNEMENT ADMINISTRATIF", "Informations de coordination."),
        ("OBSERVATIONS", "Remarques de suivi."),
    ], widths=[5, 11], header_fill=PALE_YELLOW)


def add_chapter4(doc):
    add_chapter(doc, 4, "Tests, validation et perspectives")
    add_title(doc, "4.1 Strategie de test", 2)
    add_paragraph(doc, "Les tests ont ete organises autour des scenarios metier essentiels. L'objectif etait de verifier que chaque role accede uniquement aux fonctionnalites autorisees et que les donnees sensibles, notamment les frais, restent correctement controlees.")
    add_table(doc, ["Scenario", "Etapes", "Resultat attendu"], [
        ("Connexion administrateur", "Saisir les identifiants admin puis ouvrir le dashboard.", "Le dashboard, les employes, les interventions et les frais sont accessibles."),
        ("Creation employe", "Ajouter une fiche employe et creer le compte associe.", "L'employe est ajoute et un compte utilisateur lie est disponible."),
        ("Planification intervention", "Creer une intervention avec start_date et end_date.", "L'intervention apparait dans la liste et dans le calendrier."),
        ("Connexion employe", "Se connecter avec le compte employe cree.", "L'utilisateur voit uniquement ses propres interventions."),
        ("Declaration frais", "Choisir une intervention assignee, saisir les montants et ajouter une photo.", "Les frais sont crees et associes a l'intervention correcte."),
        ("Protection frais", "Essayer de declarer des frais sur une intervention d'un autre employe.", "Le backend retourne une erreur 403 Forbidden."),
        ("Observation admin", "Ouvrir la page frais avec un compte admin.", "Tous les frais sont visibles sans bouton de creation, modification ou suppression."),
        ("Export Excel", "Exporter les affectations d'une date.", "Un fichier Excel professionnel est genere avec le logo et les colonnes attendues."),
    ], widths=[4, 8, 6])

    add_title(doc, "4.2 Validation des permissions", 2)
    add_table(doc, ["Fonctionnalite", "Admin", "Employe"], [
        ("Consulter le dashboard", "Oui", "Selon besoin, vue limitee"),
        ("Gerer les employes", "Oui", "Non"),
        ("Planifier les interventions", "Oui", "Non"),
        ("Consulter toutes les interventions", "Oui", "Non"),
        ("Consulter ses interventions", "Oui", "Oui"),
        ("Creer des frais", "Non", "Oui, pour ses interventions"),
        ("Modifier/Supprimer des frais", "Non", "Oui, uniquement ses frais"),
        ("Observer tous les frais", "Oui", "Non"),
    ], widths=[6, 5, 5])

    add_title(doc, "4.3 Difficultes rencontrees", 2)
    for para in [
        "La premiere difficulte a concerne l'evolution du modele de donnees, notamment le remplacement du champ date par start_date et end_date. Cette modification necessite une coherence entre le modele SQLAlchemy, les schemas Pydantic, les routes backend et les formulaires frontend.",
        "La deuxieme difficulte a concerne la simplification des roles. Le passage de plusieurs roles a deux roles principaux a demande de revoir les permissions afin que l'administrateur conserve la supervision tout en laissant la saisie des frais a l'employe.",
        "La troisieme difficulte a ete l'adaptation de l'interface aux attentes de presentation : design professionnel, couleurs proches du logo, mode clair/sombre discret, calendrier lisible et suppression des textes explicatifs inutiles.",
    ]:
        add_paragraph(doc, para)

    add_title(doc, "4.4 Perspectives d'amelioration", 2)
    add_table(doc, ["Amelioration", "Interet"], [
        ("Migration vers PostgreSQL", "Rendre l'application plus robuste pour une utilisation multi-utilisateur en production."),
        ("Notifications", "Informer les employes des nouvelles interventions et des changements de statut."),
        ("Validation avancee des justificatifs", "Ajouter un controle plus precis des photos ou documents associes aux frais."),
        ("Historique detaille", "Tracer toutes les modifications effectuees par les utilisateurs."),
        ("Application mobile", "Faciliter la declaration des frais et la consultation des interventions sur chantier."),
        ("Rapports analytiques", "Produire des statistiques sur les frais par employe, chantier ou periode."),
    ], widths=[6, 10])


def add_conclusion_and_annexes(doc):
    doc.add_page_break()
    add_title(doc, "Conclusion generale")
    for para in [
        "Ce projet a permis de concevoir et de realiser une application web adaptee aux besoins de CAIDELEC pour la gestion quotidienne des interventions et des frais de deplacement. La solution centralise les donnees, organise les affectations, limite les erreurs de suivi et facilite la verification administrative.",
        "Sur le plan technique, l'utilisation de FastAPI, React Vite, SQLAlchemy, SQLite et JWT a permis de construire une application simple, claire et evolutive. Le controle des roles constitue un element essentiel du projet : l'administrateur supervise, tandis que l'employe agit uniquement sur ses propres interventions et frais.",
        "Les fonctionnalites realisees, notamment le calendrier, les details journaliers, le justificatif photo et l'export Excel, rapprochent la solution des besoins reels du terrain. Le projet peut etre enrichi par la suite par des notifications, une base de donnees plus robuste et des rapports analytiques avances.",
    ]:
        add_paragraph(doc, para)

    doc.add_page_break()
    add_title(doc, "Bibliographie et webographie")
    add_table(doc, ["Reference", "Description"], [
        ("Documentation FastAPI", "Reference pour la creation d'API REST en Python."),
        ("Documentation SQLAlchemy", "Reference pour l'ORM et la gestion des modeles relationnels."),
        ("Documentation React", "Reference pour la creation de composants frontend."),
        ("Documentation Vite", "Reference pour l'environnement de developpement frontend."),
        ("Documentation JWT", "Reference pour l'authentification par token."),
        ("Supports internes CAIDELEC", "Format des affectations journalieres et besoins metier communiques durant le projet."),
    ], widths=[6, 10])

    doc.add_page_break()
    add_title(doc, "Annexes")
    add_title(doc, "Annexe A : Guide rapide d'utilisation", 2)
    add_table(doc, ["Profil", "Actions principales"], [
        ("Administrateur", "Se connecter, consulter le dashboard, gerer les employes, planifier les interventions, consulter le calendrier, exporter les affectations et observer les frais."),
        ("Employe", "Se connecter, consulter ses interventions, declarer ses frais, ajouter un justificatif et suivre l'etat de ses declarations."),
    ], widths=[4, 12])
    add_title(doc, "Annexe B : Exemple de workflow", 2)
    add_table(doc, ["Etape", "Action"], [
        ("1", "L'administrateur ajoute un employe et cree le compte associe."),
        ("2", "L'administrateur planifie une intervention avec dates et nature des travaux."),
        ("3", "L'employe se connecte et consulte l'intervention qui lui est affectee."),
        ("4", "Apres le deplacement, l'employe declare ses frais et ajoute une photo justificative."),
        ("5", "L'administrateur observe les frais et verifie les informations."),
        ("6", "Le planning journalier peut etre exporte au format Excel."),
    ], widths=[3, 13])


def main():
    diagrams = create_diagrams()
    doc = setup_document()
    add_cover(doc)
    add_header_footer(doc)
    add_front_matter(doc)
    add_intro(doc)
    add_chapter1(doc)
    add_chapter2(doc, diagrams)
    add_chapter3(doc, diagrams)
    add_chapter4(doc)
    add_conclusion_and_annexes(doc)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
