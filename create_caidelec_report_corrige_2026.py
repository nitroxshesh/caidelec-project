from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


BASE = Path(r"C:\Users\user\Documents\pfe project")
OUT = BASE / "Rapport-PFE-CAIDELEC-corrige-2026.docx"
LOGO = Path(r"C:\Users\user\caidelec-frontend\src\assets\caidelec-logo.jpeg")
ASSETS = BASE / "rapport_assets"

BLUE = "2E6EBE"
LIGHT_BLUE = "D9EAF7"
PALE_RED = "FDEDEE"
PALE_GRAY = "F4F6F9"


def set_run_font(run, size=12, bold=False, italic=False, color="000000", font="Times New Roman"):
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:ascii"), font)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), font)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


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


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_border(cell, color="808080", sz="4"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), sz)
        element.set(qn("w:color"), color)


def setup_document():
    doc = Document()
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    section.top_margin = Cm(1.7)
    section.bottom_margin = Cm(1.7)
    section.left_margin = Cm(1.8)
    section.right_margin = Cm(1.8)
    section.header_distance = Cm(0.8)
    section.footer_distance = Cm(0.8)
    add_outer_border(section)
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    style._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    style.font.size = Pt(12)
    return doc


def add_header_footer(doc):
    section = doc.sections[0]
    header = section.header
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if LOGO.exists():
        p.add_run().add_picture(str(LOGO), width=Cm(2.8))

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
                set_run_font(run, size=8, color="555555")


def page_break(doc):
    doc.add_page_break()


def title(doc, text, level=1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if level == 1 else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(0 if level == 1 else 6)
    p.paragraph_format.space_after = Pt(10 if level == 1 else 6)
    r = p.add_run(text)
    if level == 1:
        set_run_font(r, 20, True)
    elif level == 2:
        set_run_font(r, 15, True, color=BLUE)
    else:
        set_run_font(r, 13, True, color="1F4D78")


def para(doc, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, after=8):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.first_line_indent = Cm(0.7)
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(after)
    r = p.add_run(text)
    set_run_font(r, 12)


def bullet(doc, text):
    p = doc.add_paragraph(style=None)
    p.paragraph_format.left_indent = Cm(1.0)
    p.paragraph_format.first_line_indent = Cm(-0.4)
    p.paragraph_format.space_after = Pt(5)
    r = p.add_run("- ")
    set_run_font(r, 12, True, color=BLUE)
    r = p.add_run(text)
    set_run_font(r, 12)


def table(doc, headers, rows):
    tbl = doc.add_table(rows=1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = tbl.rows[0].cells[i]
        cell.text = h
        set_cell_shading(cell, LIGHT_BLUE)
        set_cell_border(cell, "000000", "8")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                set_run_font(run, 10, True)
    for row_data in rows:
        cells = tbl.add_row().cells
        for i, value in enumerate(row_data):
            cells[i].text = str(value)
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_border(cells[i])
            for p in cells[i].paragraphs:
                p.paragraph_format.space_after = Pt(1)
                for run in p.runs:
                    set_run_font(run, 9.5)
    doc.add_paragraph()


def reserved_page(doc, name, details):
    title(doc, name)
    para(doc, "Cette page est volontairement reservee afin d'ajouter le diagramme correspondant dans Word, StarUML, Draw.io, PlantUML ou un autre outil UML.", after=10)
    para(doc, details, after=10)
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.text = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    set_cell_shading(cell, PALE_GRAY)
    set_cell_border(cell, BLUE, "12")
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Espace reserve au diagramme")
    set_run_font(r, 14, True, color=BLUE)


def diagram_page(doc, name, details, image_path):
    title(doc, name)
    para(doc, details, after=10)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if image_path.exists():
        p.add_run().add_picture(str(image_path), width=Cm(16.2))
    else:
        reserved_page(doc, name, details)


def cover(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if LOGO.exists():
        p.add_run().add_picture(str(LOGO), width=Cm(9.5))
    p.paragraph_format.space_after = Pt(24)

    title(doc, "Projet de fin d'etudes")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(p.add_run("Memoire presente en vue de l'obtention du diplome"), 13)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(p.add_run("Licence / Genie des Systemes d'Information"), 13)

    doc.add_paragraph()
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    set_cell_border(cell, "000000", "14")
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(14)
    set_run_font(p.add_run("Systeme de gestion de la planification des\ninterventions quotidiennes et des frais de leurs deplacements"), 20, True)

    doc.add_paragraph()
    info = [
        ("Realise par :", "[Nom et prenom]"),
        ("Encadrant academique :", "[Nom de l'encadrant]"),
        ("Encadrant professionnel :", "[Nom de l'encadrant]"),
        ("Organisme d'accueil :", "CAIDELEC - Travaux et equipements electriques"),
    ]
    tbl = doc.add_table(rows=len(info), cols=2)
    for i, (a, b) in enumerate(info):
        tbl.rows[i].cells[0].text = a
        tbl.rows[i].cells[1].text = b
        for j, cell in enumerate(tbl.rows[i].cells):
            for p in cell.paragraphs:
                for run in p.runs:
                    set_run_font(run, 11, bold=(j == 0))
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(p.add_run("Annee universitaire : 2025/2026"), 12, True)


def simple_page(doc, heading, paragraphs=None, bullets=None, rows=None):
    title(doc, heading)
    for text in paragraphs or []:
        para(doc, text)
    front_matter = {
        "Dedicace",
        "Remerciements",
        "Resume",
        "Abstract",
        "Liste des abreviations",
        "Table des matieres",
        "Bibliographie et webographie",
    }
    if paragraphs and heading not in front_matter and not heading.startswith("Chapitre"):
        para(
            doc,
            "Dans une approche de projet de fin d'etudes, cette analyse permet de justifier les choix retenus et de montrer que la solution n'est pas seulement technique, mais aussi adaptee au contexte reel de l'entreprise.",
        )
        para(
            doc,
            "Le principe directeur reste la simplicite : chaque fonctionnalite doit correspondre a un besoin concret, rester comprehensible pour l'utilisateur final et pouvoir etre presentee facilement devant un jury.",
        )
        para(
            doc,
            "Cette partie peut etre completee par des captures d'ecran de l'application afin d'illustrer le fonctionnement reel des pages React et les controles effectues par le backend FastAPI.",
        )
    for text in bullets or []:
        bullet(doc, text)
    if rows:
        table(doc, rows[0], rows[1])


COMMON_PROJECT = "La plateforme CAIDELEC vise a centraliser la planification des interventions quotidiennes, le suivi des employes et la verification des frais de deplacement. Elle repose sur une interface web simple, un backend securise et une base de donnees relationnelle adaptee a la phase de developpement."


def build_pages():
    pages = []
    pages.append(("Dedicace", [
        "A mes parents, pour leur soutien, leurs sacrifices et leurs encouragements constants durant toutes les etapes de ma formation.",
        "A ma famille, pour sa confiance, sa patience et son accompagnement moral.",
        "A mes enseignants et encadrants, pour leurs conseils, leur disponibilite et leur exigence constructive.",
        "A toutes les personnes qui ont contribue, de pres ou de loin, a l'aboutissement de ce travail.",
    ], None, None))
    pages.append(("Remerciements", [
        "Je tiens a exprimer ma gratitude a toutes les personnes qui ont participe a la realisation de ce projet de fin d'etudes. Leurs conseils et leurs remarques ont permis d'orienter le travail vers une solution claire et exploitable.",
        "Je remercie mon encadrant academique pour son accompagnement methodologique, ainsi que l'encadrant professionnel et l'equipe de CAIDELEC pour les informations metier liees aux interventions, aux chantiers et aux frais.",
        "Je remercie egalement ma famille et mes camarades pour leur soutien moral et leur presence tout au long de cette periode de stage.",
    ], None, None))
    pages.append(("Resume", [
        COMMON_PROJECT,
        "Le systeme distingue deux profils essentiels : l'administrateur, qui supervise les donnees, planifie les interventions et observe les frais, et l'employe, qui consulte ses propres interventions et declare ses frais avec justificatif.",
        "La version corrigee ajoute un module de rapports et statistiques. Ce module permet de filtrer les donnees par periode, de calculer les totaux des frais, de comparer les depenses par employe et par intervention, puis d'exporter un rapport CSV.",
        "La solution integre un tableau de bord, un calendrier professionnel, une gestion des droits par role, un export Excel des affectations journalieres, une verification des frais par preuve photo et un module de reporting.",
        "Mots-cles : CAIDELEC, interventions, frais de deplacement, FastAPI, React, JWT, SQLite, Excel, reporting.",
    ], None, None))
    pages.append(("Abstract", [
        "This report presents the design and implementation of a web application for managing daily intervention planning and travel expenses at CAIDELEC.",
        "The application is based on FastAPI, SQLAlchemy, SQLite, JWT authentication and a React Vite frontend. It separates administrator supervision from employee self-service features.",
        "The corrected version adds a reporting module with date filters, totals, grouped expense indicators and CSV export.",
        "The platform improves operational follow-up through dashboards, calendar views, daily intervention details, Excel export, expense verification with supporting evidence and reporting.",
        "Keywords: CAIDELEC, intervention planning, travel expenses, FastAPI, React, JWT, SQLite, reporting.",
    ], None, None))
    pages.append(("Liste des abreviations", [], None, (["Abreviation", "Signification"], [
        ("API", "Application Programming Interface"),
        ("CRUD", "Create, Read, Update, Delete"),
        ("JWT", "JSON Web Token"),
        ("ORM", "Object Relational Mapping"),
        ("PFE", "Projet de fin d'etudes"),
        ("UI", "User Interface"),
        ("UX", "User Experience"),
    ])))
    pages.append(("Table des matieres", [
        "Introduction generale",
        "Chapitre 1 : Contexte general et cahier des charges",
        "Chapitre 2 : Analyse et conception",
        "Chapitre 3 : Realisation technique",
        "Chapitre 4 : Tests et validation",
        "Chapitre 5 : Bilan et perspectives",
        "Conclusion generale",
        "Bibliographie et annexes",
    ], None, None))
    pages.append(("Introduction generale", [
        "Les entreprises de travaux electriques gerent quotidiennement des equipes, des chantiers, des affectations et des frais de deplacement. Lorsque ces informations sont suivies manuellement, la communication devient plus lente et la verification demande davantage d'efforts.",
        "Dans ce contexte, CAIDELEC a besoin d'un outil capable de regrouper les donnees importantes, d'organiser les interventions par date et de donner une visibilite claire a l'administration.",
        "Le present rapport expose la demarche suivie pour analyser le besoin, concevoir l'application, realiser les modules techniques et valider les fonctionnalites principales.",
    ], None, None))

    chapter_specs = [
        ("Chapitre 1 : Contexte general et cahier des charges", [
            ("Presentation de l'organisme d'accueil", "CAIDELEC est une entreprise specialisee dans les travaux et equipements electriques. Son activite necessite une organisation quotidienne des ressources humaines et des interventions sur terrain."),
            ("Activite metier de CAIDELEC", "Les interventions peuvent concerner des chantiers differents, avec des employes, des techniciens, des natures de travaux variees et des deplacements qui doivent etre suivis."),
            ("Contexte du stage", "Le stage s'inscrit dans une logique d'amelioration du suivi operationnel. L'objectif est de transformer un besoin terrain en application web simple et presentable."),
            ("Problematique generale", "La question centrale est la suivante : comment assurer une planification quotidienne fiable, une consultation rapide des affectations et une verification correcte des frais ?"),
            ("Limites du suivi manuel", "Le suivi manuel peut provoquer des oublis, des doublons, une difficulte de recherche et une absence de tracabilite precise sur les frais et les justificatifs."),
            ("Objectifs fonctionnels", "Les objectifs sont de gerer les employes, planifier les interventions, afficher un calendrier, declarer les frais, verifier les justificatifs et exporter les affectations."),
            ("Objectifs techniques", "La solution doit rester simple a lancer, compatible avec SQLite, securisee par authentification JWT et facile a maintenir pour une presentation PFE."),
            ("Perimetre du projet", "Le projet couvre les modules authentification, employes, interventions, frais, dashboard, calendrier, details journaliers, export Excel et rapports statistiques."),
            ("Exclusions du perimetre", "Le module conges n'est pas retenu dans cette version, afin de concentrer le projet sur les interventions et les frais de deplacement."),
            ("Fonctionnalite ajoutee apres soutenance", "Afin de renforcer le contenu du PFE, la version corrigee ajoute un module Rapports. Ce module donne une lecture analytique des interventions et des frais par periode."),
            ("Synthese du besoin", "Le besoin principal est une plateforme claire qui remplace les suivis disperses par une source d'information unique, securisee et exploitable pour le suivi."),
        ]),
        ("Chapitre 2 : Analyse et conception", [
            ("Identification des acteurs", "Deux acteurs structurent la solution : l'administrateur et l'employe. Cette simplification rend les autorisations plus lisibles et plus faciles a verifier."),
            ("Role de l'administrateur", "L'administrateur gere les employes, cree les interventions, consulte le dashboard, observe les frais et verifie les informations declarees."),
            ("Role de l'employe", "L'employe se connecte a son espace, consulte les interventions qui lui sont affectees et declare ses frais uniquement pour ses propres interventions."),
            ("Regles de gestion principales", "Les regles de gestion protegent les donnees : un employe ne peut pas ajouter de frais sur une intervention qui ne lui appartient pas."),
            ("Cas d'utilisation", "Les cas d'utilisation regroupent la connexion, la gestion des employes, la planification, la consultation, la declaration des frais, la verification et la consultation des rapports."),
            ("Modele conceptuel des donnees", "Le modele repose sur les entites User, Employee, Intervention et Expense. Ces entites couvrent l'identite, la fiche employe, l'affectation et les frais."),
            ("Relations entre les entites", "Un utilisateur employe est lie a une fiche employee_id. Un employe peut avoir plusieurs interventions, et une intervention peut avoir plusieurs frais."),
            ("Conception de la securite", "La securite est basee sur le role stocke dans le token ou recupere par /auth/me. Le backend reste responsable de la verification finale."),
            ("Conception de l'interface", "L'interface est minimaliste, professionnelle et proche des couleurs du logo CAIDELEC, avec navigation adaptee au role connecte."),
            ("Conception du calendrier", "Le calendrier affiche les dates d'intervention, met en evidence les journees planifiees et permet d'acceder aux details d'une date."),
            ("Conception du module rapports", "Le module rapports filtre les interventions par periode, calcule les frais associes et separe les resultats selon le role connecte. L'administrateur voit l'ensemble des donnees, tandis que l'employe ne voit que son perimetre."),
        ]),
        ("Chapitre 3 : Realisation technique", [
            ("Architecture globale", "L'architecture suit un modele client-serveur : React Vite pour le frontend, FastAPI pour le backend et SQLite pour la persistance."),
            ("Backend FastAPI", "FastAPI permet de construire des routes REST rapides, lisibles et faciles a tester. Les schemas Pydantic assurent la validation des donnees."),
            ("Gestion SQLAlchemy", "SQLAlchemy permet de representer les tables sous forme de classes Python et facilite les operations CRUD sur les donnees."),
            ("Authentification JWT", "L'utilisateur se connecte avec ses identifiants. Le backend retourne un jeton JWT utilise par le frontend dans les appels suivants."),
            ("Endpoint /auth/me", "Cet endpoint retourne l'utilisateur courant avec id, username, email, role et employee_id. Il permet a l'interface d'adapter l'affichage."),
            ("Module employes", "Le module employes permet de creer les fiches, de renseigner le telephone, le role metier et de lier un compte utilisateur si necessaire."),
            ("Creation de compte employe", "Lors de l'ajout d'un employe, un compte utilisateur peut etre cree automatiquement avec le role employe et un employee_id associe."),
            ("Module interventions", "Une intervention contient le chantier, la nature des travaux, start_date, end_date, status et observation. Cette structure gere les travaux sur plusieurs jours."),
            ("Module frais", "Le module frais permet a l'employe de declarer transport, repas, autre montant et justificatif photo, avec controle de propriete de l'intervention."),
            ("Limite de frais", "Une limite individuelle peut etre definie par utilisateur afin de controler le montant maximum des frais declares."),
            ("Dashboard", "Le dashboard regroupe les statistiques et le calendrier. Il donne a l'administrateur une vue synthetique de l'activite."),
            ("Export Excel", "L'export Excel reprend le format des affectations journalieres avec logo, chantier, nature des travaux, intervenants et observations."),
            ("Module rapports et statistiques", "Le backend expose /reports/summary. Le frontend affiche les indicateurs par periode, les frais par employe, les frais par intervention et un export CSV exploitable."),
            ("Controle d'acces des rapports", "Le module rapports reutilise JWT et require_roles. Les resultats sont filtres selon le role afin d'eviter toute consultation non autorisee."),
        ]),
        ("Chapitre 4 : Tests et validation", [
            ("Strategie de test", "Les tests ciblent les workflows les plus importants : connexion, roles, creation d'employe, intervention, frais et export."),
            ("Test de connexion admin", "Le compte admin doit ouvrir le dashboard, consulter les donnees et acceder aux modules d'administration sans pouvoir creer de frais."),
            ("Test de creation employe", "Apres creation d'une fiche employe, le compte lie doit permettre une connexion avec le role employe et l'employee_id correspondant."),
            ("Test de planification", "Une intervention creee avec start_date et end_date doit apparaitre dans la liste et dans le calendrier."),
            ("Test de consultation employe", "Un employe connecte ne doit voir que les interventions qui lui sont affectees."),
            ("Test de frais valide", "Un employe peut declarer des frais pour une intervention qui lui appartient et ajouter une photo justificative."),
            ("Test de frais interdit", "Si l'employe choisit une intervention qui ne lui appartient pas, le backend doit refuser l'action avec une erreur 403."),
            ("Test observation admin", "L'administrateur doit voir tous les frais en lecture seule, sans formulaire d'ajout ni actions de modification ou suppression."),
            ("Test export Excel", "Le fichier genere doit reprendre le logo et les colonnes professionnelles demandees pour les affectations journalieres."),
            ("Test du module rapports", "Le rapport doit afficher les totaux d'une periode, les frais par employe, les frais par intervention et produire un fichier CSV lisible."),
            ("Test de limitation par role", "Un employe connecte doit obtenir uniquement ses propres statistiques, alors que l'administrateur peut consulter les statistiques globales."),
            ("Validation finale", "La validation finale consiste a verifier que l'application repond au besoin initial sans complexite inutile."),
        ]),
        ("Chapitre 5 : Bilan et perspectives", [
            ("Bilan fonctionnel", "La solution couvre les besoins prioritaires : planification, suivi des employes, declaration des frais et observation administrative."),
            ("Bilan technique", "Le choix FastAPI et React offre une base claire, moderne et suffisante pour une application de stage/PFE."),
            ("Difficultes rencontrees", "Les principales difficultes concernent l'evolution du modele de donnees, le controle des roles et l'adaptation du design aux attentes professionnelles."),
            ("Apports du projet", "Le projet renforce les competences en analyse, conception, developpement full-stack, securite applicative et presentation d'une solution metier."),
            ("Limites actuelles", "SQLite reste adapte au developpement mais une base plus robuste serait preferable en production multi-utilisateur."),
            ("Amelioration securite", "Les prochaines versions pourraient renforcer la politique de mot de passe, l'historique des actions et la journalisation des validations."),
            ("Amelioration mobile", "Une interface mobile ou progressive web app faciliterait la saisie des frais directement depuis le chantier."),
            ("Notifications", "Des notifications pourraient avertir les employes lorsqu'une intervention leur est affectee ou modifiee."),
            ("Statistiques avancees", "La version corrigee integre deja un premier module de statistiques. Les prochaines evolutions pourraient ajouter des graphiques plus detailles et des exports PDF."),
            ("Preparation production", "Le passage en production demanderait une migration vers PostgreSQL, une configuration serveur et une politique de sauvegarde."),
        ]),
    ]

    for chapter, sections in chapter_specs:
        pages.append((chapter, [
            "Ce chapitre developpe les elements essentiels de cette partie du rapport. Il presente les notions, choix et decisions qui structurent la solution CAIDELEC.",
            COMMON_PROJECT,
        ], None, None))
        for section, text in sections:
            pages.append((section, [
                text,
                "Cette partie contribue a rendre le projet coherent avec les besoins exprimes. Elle montre comment l'application transforme une contrainte metier en fonctionnalite concrete et exploitable.",
                "Le choix de garder une solution simple permet de faciliter la demonstration, la maintenance et les evolutions futures sans surcharger le systeme.",
            ], None, None))

    pages.extend([
        ("Diagrammes UML", [
            "Les pages suivantes presentent les diagrammes principaux du projet. Ils couvrent les acteurs, les classes metier, les sequences critiques et l'architecture generale.",
            "Ces diagrammes facilitent la lecture du rapport et permettent de relier les besoins fonctionnels a la realisation technique.",
        ], None, None),
        ("Conclusion generale", [
            "Le projet CAIDELEC constitue une reponse concrete au besoin de suivi des interventions quotidiennes et des frais de deplacement. Il permet de centraliser les informations et d'ameliorer la tracabilite.",
            "La solution met en place une separation claire entre l'administrateur et l'employe. Cette separation limite les erreurs et garantit que chaque utilisateur agit uniquement dans son perimetre.",
            "La version corrigee renforce le projet avec un module de rapports et statistiques. Cette fonctionnalite ajoute une valeur de pilotage, car elle permet de suivre les frais et interventions par periode.",
            "La realisation technique avec FastAPI, React, SQLAlchemy, SQLite et JWT montre qu'il est possible de construire une application professionnelle avec une architecture simple et evolutive.",
        ], None, None),
        ("Bibliographie et webographie", [], None, (["Reference", "Utilisation dans le projet"], [
            ("Documentation FastAPI", "Conception des endpoints REST et validation des routes."),
            ("Documentation React", "Creation des composants et gestion de l'interface."),
            ("Documentation SQLAlchemy", "Modelisation des tables et relations."),
            ("Documentation JWT", "Authentification et gestion du token."),
            ("Supports internes CAIDELEC", "Format des affectations journalieres et besoins metier."),
        ])),
        ("Annexe A : Scenarios de test", [
            "1. Login admin, consulter dashboard, employes, interventions et frais.",
            "2. Creer un employe et verifier le compte utilisateur lie.",
            "3. Creer une intervention avec start_date et end_date.",
            "4. Login employe et verifier l'affichage de ses interventions uniquement.",
            "5. Ajouter un frais avec justificatif photo pour une intervention assignee.",
            "6. Revenir admin et observer tous les frais en lecture seule.",
            "7. Ouvrir le module Rapports, filtrer une periode et exporter le fichier CSV.",
        ], None, None),
    ])
    return pages


def main():
    doc = setup_document()
    cover(doc)
    add_header_footer(doc)
    page_break(doc)

    pages = build_pages()
    # Keep the final report at 50 pages including the cover and four diagram pages.
    selected_page_numbers = list(range(1, 32)) + [32, 33, 34, 36, 37, 38, 40, 41, 43, 44, 45, 46, 57, 72]
    pages = [pages[number - 1] for number in selected_page_numbers]
    diagrams = [
        ("Diagramme de cas d'utilisation", "Ce diagramme montre les acteurs Administrateur et Employe avec les fonctions principales de la plateforme.", ASSETS / "use_cases.png"),
        ("Diagramme de classes", "Ce diagramme presente les classes User, Employee, Intervention et Expense avec leurs attributs et relations.", ASSETS / "classes.png"),
        ("Diagramme de sequence - Declaration des frais", "Ce diagramme decrit la declaration d'un frais par l'employe, avec controle de l'intervention et enregistrement en base.", ASSETS / "sequence_expenses.png"),
        ("Diagramme d'architecture", "Ce diagramme presente la communication entre React, FastAPI, SQLAlchemy, SQLite et les modules fonctionnels.", ASSETS / "architecture.png"),
    ]

    for heading, paragraphs, bullets, rows in pages:
        simple_page(doc, heading, paragraphs, bullets, rows)
        page_break(doc)
    for i, (heading, details, image_path) in enumerate(diagrams):
        diagram_page(doc, heading, details, image_path)
        if i < len(diagrams) - 1:
            page_break(doc)

    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
