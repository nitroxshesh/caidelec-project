from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    ListFlowable,
    ListItem,
)


BASE = Path(r"C:\Users\user\Documents\pfe project")
PROJECT = BASE / "latex_caidelec_final"
ASSETS = PROJECT / "assets"
OUT = BASE / "Rapport-PFE-CAIDELEC-LaTeX-preview.pdf"


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontSize=22, leading=28, alignment=TA_CENTER, textColor=colors.HexColor("#1F66B9"), spaceAfter=18))
styles.add(ParagraphStyle(name="Chapter", parent=styles["Heading1"], fontSize=18, leading=22, textColor=colors.HexColor("#1F66B9"), spaceBefore=14, spaceAfter=10))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontSize=14, leading=18, textColor=colors.HexColor("#1F66B9"), spaceBefore=10, spaceAfter=6))
styles.add(ParagraphStyle(name="BodyJustify", parent=styles["BodyText"], fontSize=10.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=6))
styles.add(ParagraphStyle(name="Caption", parent=styles["BodyText"], fontSize=9, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#1F4E79"), spaceAfter=10))


def p(text):
    return Paragraph(text, styles["BodyJustify"])


def h1(text):
    return Paragraph(text, styles["Chapter"])


def h2(text):
    return Paragraph(text, styles["Section"])


def bullet(items):
    return ListFlowable(
        [ListItem(Paragraph(item, styles["BodyJustify"]), leftIndent=12) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=18,
    )


def table(headers, rows, widths):
    data = [[Paragraph(f"<b>{x}</b>", styles["BodyText"]) for x in headers]]
    data += [[Paragraph(str(x), styles["BodyText"]) for x in row] for row in rows]
    tbl = Table(data, colWidths=widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9D9D9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return tbl


def img(path, width):
    im = Image(str(path))
    ratio = im.imageHeight / im.imageWidth
    im.drawWidth = width
    im.drawHeight = width * ratio
    return im


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(2.2 * cm, 1.2 * cm, "Rapport de projet de fin d'etudes")
    canvas.drawRightString(19 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


story = []

cover_table = Table(
    [[img(ASSETS / "uic_logo.png", 7 * cm), img(ASSETS / "caidelec_logo.jpeg", 7 * cm)]],
    colWidths=[8 * cm, 8 * cm],
)
cover_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
story += [
    cover_table,
    Spacer(1, 1.2 * cm),
    Paragraph("PROJET DE FIN D'ETUDES", styles["CoverTitle"]),
    Paragraph("Système de gestion de la planification des interventions quotidiennes et des frais de leurs déplacements", styles["CoverTitle"]),
    Spacer(1, 0.8 * cm),
    table(
        ["Element", "Information"],
        [
            ("Réalisé par", "Yassir Kemmissa"),
            ("Organisme d'accueil", "CAIDELEC"),
            ("Université", "Université Internationale de Casablanca"),
            ("Année universitaire", "2025-2026"),
        ],
        [5 * cm, 9 * cm],
    ),
    PageBreak(),
]

front_sections = [
    ("Dédicace", "Je dédie ce travail à mes parents, à ma famille, à mes enseignants et à toutes les personnes qui m'ont accompagné durant mon parcours."),
    ("Remerciements", "Je remercie mon encadrant académique, l'équipe de CAIDELEC et toutes les personnes qui ont contribué à la réalisation de ce projet."),
    ("Résumé", "Ce rapport présente une application web de gestion des interventions quotidiennes et des frais de déplacement. La version finale ajoute un module Rapports et Statistiques avec filtrage par période et export CSV."),
    ("Abstract", "This report presents a web application for managing daily interventions and travel expenses. The final version adds a reporting module with period filters and CSV export."),
]
for title, text in front_sections:
    story += [h1(title), p(text), PageBreak()]

chapters = [
    ("Introduction générale", [
        "Le projet CAIDELEC vise à centraliser la planification des interventions quotidiennes, le suivi des employés et le contrôle des frais de déplacement.",
        "La version finale conserve la structure de la première version du rapport et ajoute la fonctionnalité Rapports et Statistiques dans l'analyse, la conception et les tests.",
    ]),
    ("Cadre général du projet", [
        "CAIDELEC est une entreprise spécialisée dans les travaux et équipements électriques. Son activité nécessite une organisation rigoureuse des chantiers, des équipes et des déplacements.",
        "Le périmètre couvre l'authentification, les employés, les interventions, les frais, le calendrier, les exports et les rapports.",
    ]),
    ("Étude préalable et cahier des charges", [
        "Le suivi manuel rend la consultation lente et limite la traçabilité des frais. La solution proposée centralise les données et clarifie les responsabilités.",
        "La nouvelle fonctionnalité répond au besoin de pilotage : elle transforme les données enregistrées en indicateurs exploitables.",
    ]),
    ("Analyse fonctionnelle", [
        "Le système distingue deux acteurs : l'administrateur et l'employé. L'administrateur gère et observe l'ensemble des données. L'employé consulte seulement ses interventions, ses frais et ses rapports.",
        "Le module Rapports permet de filtrer les interventions et frais par période, de regrouper les montants et d'exporter un fichier CSV.",
    ]),
]

for title, paragraphs in chapters:
    story.append(h1(title))
    for text in paragraphs:
        story.append(p(text))
    story.append(Spacer(1, 0.2 * cm))

story += [
    h2("Matrice des autorisations"),
    table(
        ["Fonction", "Admin", "Employé"],
        [
            ("Gérer les employés", "Oui", "Non"),
            ("Planifier les interventions", "Oui", "Non"),
            ("Créer des frais", "Non", "Oui, sur ses interventions"),
            ("Observer les frais", "Tous", "Les siens"),
            ("Consulter les rapports", "Globaux", "Personnels"),
            ("Exporter CSV", "Oui", "Oui, sur son périmètre"),
        ],
        [7 * cm, 3 * cm, 5 * cm],
    ),
    PageBreak(),
    h1("Conception et architecture"),
    p("Les diagrammes UML suivants sont fournis avec leurs fichiers StarUML dans le dossier du projet LaTeX."),
]

figures = [
    ("01_use_case_caidelec.png", "Diagramme de cas d'utilisation avec module Rapports"),
    ("02_class_caidelec.png", "Diagramme de classes corrigé"),
    ("03_sequence_rapports_caidelec.png", "Séquence de consultation des rapports et export CSV"),
    ("04_activity_caidelec.png", "Diagramme d'activité avec rapports statistiques"),
]
for name, cap in figures:
    story += [img(ASSETS / name, 16 * cm), Paragraph(cap, styles["Caption"]), PageBreak()]

story += [
    h1("Réalisation de l'application"),
    p("Le backend FastAPI expose les modules d'authentification, employés, interventions, frais et rapports. Le frontend React adapte la navigation selon le rôle connecté."),
    img(ASSETS / "login_screen.jpg", 15 * cm),
    Paragraph("Écran d'authentification", styles["Caption"]),
    img(ASSETS / "dashboard_screen.jpg", 15 * cm),
    Paragraph("Tableau de bord avec calendrier", styles["Caption"]),
    PageBreak(),
    h1("Validation et résultats"),
    table(
        ["Test", "Résultat attendu", "Statut"],
        [
            ("Connexion admin", "Accès aux modules d'administration", "Validé"),
            ("Création employé", "Compte lié généré", "Validé"),
            ("Déclaration frais", "Frais lié à une intervention personnelle", "Validé"),
            ("Rapports admin", "Statistiques globales", "Validé"),
            ("Rapports employé", "Statistiques personnelles", "Validé"),
            ("Export CSV", "Fichier exploitable", "Validé"),
        ],
        [5 * cm, 7 * cm, 2.5 * cm],
    ),
    h1("Conclusion générale"),
    p("La version finale de CAIDELEC répond au besoin de planification et de suivi des frais. L'ajout du module Rapports et Statistiques renforce la cohérence du projet et apporte une fonctionnalité supplémentaire claire pour la soutenance."),
]

doc = SimpleDocTemplate(
    str(OUT),
    pagesize=A4,
    rightMargin=2 * cm,
    leftMargin=2 * cm,
    topMargin=2 * cm,
    bottomMargin=2 * cm,
)
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(OUT)
