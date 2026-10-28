from pathlib import Path
import shutil

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


BASE = Path(r"C:\Users\user\Documents\pfe project")
REFERENCE = Path(r"C:\Users\user\Downloads\Rapport_PFE_CAIDELEC_Yassir_Kemmissa_FINAL PFE.docx")
OUT = BASE / "Rapport_PFE_CAIDELEC_Yassir_Kemmissa_CORRIGE_2026.docx"
DIAGRAMS = BASE / "uml_diagrams_corrige_2026"


def set_run_font(run, size=11, bold=False, color="000000"):
    font = "Times New Roman"
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:ascii"), font)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), font)
    run.font.size = Pt(size)
    run.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_border(cell, color="D9D9D9", sz="8"):
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


def paragraph(doc, text, style=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph(style=style)
    p.alignment = align
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    set_run_font(run, 11)
    return p


def heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(8)
    p.add_run(text)
    return p


def caption(doc, text):
    style = "Table Caption" if "Table Caption" in [s.name for s in doc.styles] else None
    p = doc.add_paragraph(style=style)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_run_font(run, 10, bold=True, color="1F4E79")
    return p


def table(doc, headers, rows):
    tbl = doc.add_table(rows=1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    if "Table Grid" in [style.name for style in doc.styles]:
        tbl.style = "Table Grid"

    for i, header in enumerate(headers):
        cell = tbl.rows[0].cells[i]
        cell.text = header
        set_cell_shading(cell, "D9EAF7")
        set_cell_border(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                set_run_font(run, 9.5, bold=True)

    for row in rows:
        cells = tbl.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)
            set_cell_border(cells[i])
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in cells[i].paragraphs:
                p.paragraph_format.space_after = Pt(1)
                for run in p.runs:
                    set_run_font(run, 9)

    doc.add_paragraph()
    return tbl


def add_image_page(doc, title, caption_text, image_name):
    doc.add_page_break()
    heading(doc, title, 1)
    image_path = DIAGRAMS / image_name
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if image_path.exists():
        p.add_run().add_picture(str(image_path), width=Cm(16.5))
    caption(doc, caption_text)


def main():
    shutil.copy2(REFERENCE, OUT)
    doc = Document(OUT)

    doc.add_page_break()
    heading(doc, "Annexe D Corrections et fonctionnalite ajoutee", 1)
    paragraph(
        doc,
        "Cette annexe presente les corrections ajoutees apres la soutenance et integre les nouveaux diagrammes UML. "
        "La fonctionnalite ajoutee est le module Rapports et Statistiques. Elle permet de consulter les indicateurs par periode, "
        "de regrouper les frais par employe et par intervention, puis d'exporter les resultats au format CSV.",
    )
    paragraph(
        doc,
        "Ce module renforce l'application parce qu'il ne se limite pas a la saisie des donnees. Il donne une vision de pilotage "
        "aux responsables et permet a chaque employe de consulter ses propres statistiques sans acceder aux donnees des autres utilisateurs.",
    )

    caption(doc, "Tableau D.1 - Fonctionnalite supplementaire ajoutee")
    table(
        doc,
        ["Element", "Description"],
        [
            ("Endpoint backend", "GET /reports/summary avec filtres start_date et end_date."),
            ("Interface frontend", "Page Rapports pour admin et Mes rapports pour employe."),
            ("Controle d'acces", "Admin consulte toutes les donnees. Employe consulte seulement ses donnees."),
            ("Indicateurs", "Total frais, interventions, frais par statut, frais par employe et frais par intervention."),
            ("Export", "Export CSV telechargeable depuis l'interface."),
        ],
    )

    heading(doc, "Tests de verification ajoutes", 2)
    caption(doc, "Tableau D.2 - Scenarios de verification du module rapports")
    table(
        doc,
        ["Scenario", "Resultat attendu"],
        [
            ("Connexion admin puis ouverture Rapports", "Les statistiques globales sont affichees."),
            ("Filtrage par periode", "Les interventions et frais hors periode ne sont pas inclus."),
            ("Export CSV", "Le fichier contient les totaux et les regroupements principaux."),
            ("Connexion employe", "Seules les donnees de l'employe connecte sont affichees."),
            ("Acces non autorise", "Le backend refuse toute consultation en dehors du role autorise."),
        ],
    )

    add_image_page(
        doc,
        "Diagramme de cas d'utilisation corrige",
        "Figure D.1 - Diagramme de cas d'utilisation avec module Rapports",
        "01_use_case_caidelec.png",
    )
    add_image_page(
        doc,
        "Diagramme de classes corrige",
        "Figure D.2 - Diagramme de classes avec ReportService et ReportSummary",
        "02_class_caidelec.png",
    )
    add_image_page(
        doc,
        "Diagramme de sequence corrige",
        "Figure D.3 - Sequence de consultation des rapports et export CSV",
        "03_sequence_rapports_caidelec.png",
    )
    add_image_page(
        doc,
        "Diagramme d'activite corrige",
        "Figure D.4 - Activites principales avec rapports statistiques",
        "04_activity_caidelec.png",
    )

    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
