from pathlib import Path
import shutil
import zipfile


BASE = Path(r"C:\Users\user\Documents\pfe project")
OUT = BASE / "latex_caidelec_final"
ASSETS = OUT / "assets"
DIAGRAM_SRC = BASE / "uml_diagrams_corrige_2026"
STARUML_SRC = BASE / "staruml_caidelec_corrige_2026"
MEDIA = BASE / "reference_media_extract"


def copy_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def latex_escape(text: str) -> str:
    return (
        text.replace("&", r"\&")
        .replace("%", r"\%")
        .replace("#", r"\#")
        .replace("_", r"\_")
    )


MAIN_TEX = r"""
\documentclass[12pt,a4paper,oneside]{report}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[french]{babel}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{float}
\usepackage{array}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{setspace}
\usepackage{hyperref}
\usepackage{tocloft}
\usepackage{enumitem}
\usepackage{caption}

\geometry{left=2.5cm,right=2.5cm,top=2.4cm,bottom=2.4cm}
\onehalfspacing
\definecolor{caidelecBlue}{HTML}{1F66B9}
\definecolor{caidelecRed}{HTML}{E50914}
\definecolor{lightBlue}{HTML}{EAF3FC}

\hypersetup{
  colorlinks=true,
  linkcolor=caidelecBlue,
  urlcolor=caidelecBlue,
  citecolor=caidelecBlue
}

\titleformat{\chapter}[display]
  {\normalfont\bfseries\Huge\color{caidelecBlue}}
  {\chaptertitlename\ \thechapter}{18pt}{\Huge}
\titleformat{\section}{\normalfont\Large\bfseries\color{caidelecBlue}}{\thesection}{1em}{}
\titleformat{\subsection}{\normalfont\large\bfseries}{\thesubsection}{1em}{}

\pagestyle{fancy}
\fancyhf{}
\lhead{Rapport de projet de fin d'études}
\rhead{CAIDELEC}
\cfoot{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\captionsetup{font=small,labelfont=bf}
\setlist[itemize]{leftmargin=1.2cm}
\renewcommand{\arraystretch}{1.25}

\begin{document}

\begin{titlepage}
\centering
\includegraphics[width=0.43\textwidth]{assets/uic_logo.png}\hfill
\includegraphics[width=0.42\textwidth]{assets/caidelec_logo.jpeg}

\vspace{1.4cm}
{\Large Université Internationale de Casablanca\\[0.2cm]}
{\large Licence en Génie des Systèmes d'Information\\[1.2cm]}

{\Huge\bfseries PROJET DE FIN D'ÉTUDES\\[0.8cm]}
{\large Sous le thème\\[0.4cm]}
\fbox{\begin{minipage}{0.88\textwidth}
\centering
\vspace{0.4cm}
{\Large\bfseries Système de gestion de la planification des interventions quotidiennes et des frais de leurs déplacements}
\vspace{0.4cm}
\end{minipage}}

\vspace{1.4cm}
\begin{tabular}{>{\bfseries}p{5.2cm}p{8cm}}
Réalisé par : & Yassir Kemmissa\\
Encadrant académique : & \dotfill\\
Encadrant professionnel : & \dotfill\\
Organisme d'accueil : & CAIDELEC\\
Année universitaire : & 2025--2026\\
\end{tabular}

\vfill
{\large Soutenu devant les membres du jury}\\[0.5cm]
\begin{tabular}{p{6cm}p{6cm}}
\dotfill & Président du jury\\
\dotfill & Examinateur\\
\dotfill & Encadrant\\
\end{tabular}
\end{titlepage}

\pagenumbering{roman}
\chapter*{Dédicace}
\addcontentsline{toc}{chapter}{Dédicace}
Je dédie ce travail à mes parents pour leur soutien, leurs sacrifices et leur confiance. Je le dédie également à ma famille, à mes enseignants et à toutes les personnes qui m'ont accompagné durant ma formation.

\chapter*{Remerciements}
\addcontentsline{toc}{chapter}{Remerciements}
Je remercie mon encadrant académique pour ses remarques et son accompagnement. Je remercie aussi l'équipe de CAIDELEC pour les informations métier qui ont permis de comprendre le fonctionnement des interventions, des affectations et des frais de déplacement.

\chapter*{Résumé}
\addcontentsline{toc}{chapter}{Résumé}
Ce rapport présente la conception et la réalisation d'une application web destinée à la gestion des interventions quotidiennes, au suivi des employés et au contrôle des frais de déplacement au sein de CAIDELEC. L'application repose sur une architecture composée d'un backend FastAPI, d'une base SQLite, d'une authentification JWT et d'une interface React Vite.

La version finale intègre une fonctionnalité supplémentaire de rapports et statistiques. Elle permet à l'administrateur de consulter des indicateurs globaux par période et à l'employé de consulter uniquement ses propres statistiques. Cette fonctionnalité complète le tableau de bord, le calendrier, l'export Excel des affectations, la déclaration des frais et la vérification par justificatif.

\textbf{Mots-clés :} CAIDELEC, interventions, frais de déplacement, FastAPI, React, JWT, SQLite, rapports, StarUML.

\chapter*{Abstract}
\addcontentsline{toc}{chapter}{Abstract}
This report presents the design and implementation of a web application for managing daily interventions, employees and travel expenses at CAIDELEC. The solution is based on FastAPI, SQLite, JWT authentication and a React Vite frontend.

The final version adds a reporting and statistics module. Administrators can view global indicators by period, while employees can view only their own data. This module improves the consistency of the project and provides a clear operational overview.

\textbf{Keywords:} CAIDELEC, intervention planning, travel expenses, FastAPI, React, JWT, SQLite, reporting, StarUML.

\tableofcontents
\listoffigures
\listoftables

\chapter*{Liste des acronymes}
\addcontentsline{toc}{chapter}{Liste des acronymes}
\begin{longtable}{p{3cm}p{10cm}}
\toprule
\textbf{Acronyme} & \textbf{Signification}\\
\midrule
API & Application Programming Interface\\
CRUD & Create Read Update Delete\\
JWT & JSON Web Token\\
ORM & Object Relational Mapping\\
PFE & Projet de Fin d'Études\\
UML & Unified Modeling Language\\
UI & User Interface\\
UX & User Experience\\
\bottomrule
\end{longtable}

\clearpage
\pagenumbering{arabic}

\chapter*{Introduction générale}
\addcontentsline{toc}{chapter}{Introduction générale}
Les entreprises de travaux électriques gèrent chaque jour des équipes, des chantiers, des affectations et des frais de déplacement. Lorsque ces informations sont suivies avec des documents séparés ou des échanges informels, la planification devient difficile à contrôler et les dépenses perdent en traçabilité.

Le projet CAIDELEC répond à ce besoin par une application web qui centralise les employés, les interventions, les frais, les justificatifs et les indicateurs. Le rapport conserve la logique de la première version, mais il intègre la fonctionnalité supplémentaire de rapports et statistiques demandée après la soutenance.

\section*{Organisation du rapport}
\addcontentsline{toc}{section}{Organisation du rapport}
Le rapport est organisé en chapitres. Le premier présente le cadre général. Le deuxième analyse l'existant et le cahier des charges. Le troisième décrit la conduite du projet. Le quatrième détaille l'analyse fonctionnelle. Le cinquième présente la conception et les diagrammes UML. Le sixième explique la réalisation technique. Le septième expose les tests et les résultats.

\chapter{Cadre général du projet}
\section{Présentation de l'organisme d'accueil}
CAIDELEC est une entreprise spécialisée dans les travaux et équipements électriques. Son activité exige une organisation quotidienne des équipes, des chantiers, des déplacements et des retours terrain.

\section{Contexte et origine du besoin}
Le besoin initial concerne la planification des interventions quotidiennes. Les informations importantes doivent être accessibles rapidement, avec une distinction claire entre les actions de l'administrateur et celles de l'employé.

\section{Objectifs du projet}
Les objectifs du projet sont les suivants :
\begin{itemize}
  \item centraliser les employés et les comptes utilisateurs ;
  \item planifier les interventions par date de début et date de fin ;
  \item afficher les interventions dans un calendrier professionnel ;
  \item permettre aux employés de déclarer leurs frais ;
  \item associer un justificatif photo aux dépenses ;
  \item permettre à l'administrateur d'observer et de vérifier les frais ;
  \item produire des exports Excel et CSV.
\end{itemize}

\begin{table}[H]
\centering
\caption{Périmètre fonctionnel du projet}
\begin{tabular}{p{4cm}p{9cm}}
\toprule
\textbf{Module} & \textbf{Fonction principale}\\
\midrule
Authentification & Connexion sécurisée avec JWT et rôles.\\
Employés & Création, modification, suppression et compte lié.\\
Interventions & Planification avec chantier, nature des travaux, observation et période.\\
Frais & Déclaration des frais avec contrôle d'appartenance et justificatif.\\
Dashboard & Statistiques synthétiques et calendrier.\\
Rapports & Indicateurs filtrés par période et export CSV.\\
\bottomrule
\end{tabular}
\end{table}

\chapter{Étude préalable et cahier des charges}
\section{Fonctionnement avant la solution}
Le suivi manuel impose plusieurs actions répétitives : préparer les affectations, transmettre les informations, vérifier les retours, récupérer les montants de frais et contrôler les justificatifs. Ce fonctionnement augmente le risque d'oubli et rend les recherches plus lentes.

\section{Diagnostic de l'existant}
\begin{table}[H]
\centering
\caption{Diagnostic du processus initial}
\begin{tabular}{p{4cm}p{5cm}p{4cm}}
\toprule
\textbf{Constat} & \textbf{Impact} & \textbf{Réponse proposée}\\
\midrule
Planning dispersé & Consultation lente & Calendrier centralisé\\
Frais sans preuve structurée & Contrôle difficile & Justificatif photo\\
Droits peu visibles & Risque d'accès inadapté & Rôles admin et employé\\
Absence d'indicateurs & Suivi limité & Module rapports\\
\bottomrule
\end{tabular}
\end{table}

\section{Exigences fonctionnelles}
Le système doit gérer l'authentification, les employés, les interventions, les frais, les exports et les rapports. La nouvelle fonctionnalité de rapports doit être accessible depuis l'interface et doit respecter les droits de l'utilisateur connecté.

\section{Exigences non fonctionnelles}
La solution doit rester simple, claire, maintenable et présentable. Elle doit fonctionner avec SQLite pendant la phase de développement et respecter une architecture séparant le frontend, le backend et la base de données.

\chapter{Conduite du projet}
\section{Organisation générale}
Le projet a été conduit par itérations. Chaque itération a permis de stabiliser une partie fonctionnelle : authentification, employés, interventions, frais, calendrier, exports, puis rapports statistiques.

\section{Backlog fonctionnel}
\begin{longtable}{p{2.5cm}p{8.5cm}p{2.5cm}}
\caption{Backlog fonctionnel du projet}\\
\toprule
\textbf{Code} & \textbf{User story} & \textbf{Priorité}\\
\midrule
US01 & En tant qu'utilisateur, je veux me connecter afin d'accéder à mon espace. & Haute\\
US02 & En tant qu'administrateur, je veux gérer les employés. & Haute\\
US03 & En tant qu'administrateur, je veux planifier une intervention. & Haute\\
US04 & En tant qu'employé, je veux consulter mes interventions. & Haute\\
US05 & En tant qu'employé, je veux déclarer mes frais avec justificatif. & Haute\\
US06 & En tant qu'administrateur, je veux observer et vérifier les frais. & Haute\\
US07 & En tant qu'utilisateur autorisé, je veux consulter des rapports par période. & Haute\\
US08 & En tant qu'administrateur, je veux exporter les affectations en Excel. & Moyenne\\
\bottomrule
\end{longtable}

\section{Gestion des risques}
Les principaux risques concernent l'évolution du modèle de données, les droits d'accès, la qualité de l'interface et la cohérence entre le rapport, les diagrammes et l'application livrée.

\chapter{Analyse et spécification des besoins}
\section{Acteurs du système}
Le système distingue deux acteurs principaux : l'administrateur et l'employé.

\begin{table}[H]
\centering
\caption{Acteurs du système}
\begin{tabular}{p{4cm}p{9cm}}
\toprule
\textbf{Acteur} & \textbf{Responsabilités}\\
\midrule
Administrateur & Gérer les employés, planifier les interventions, consulter le dashboard, observer les frais, vérifier les justificatifs et consulter les rapports globaux.\\
Employé & Consulter ses interventions, déclarer ses frais, ajouter un justificatif, consulter ses frais et ses rapports personnels.\\
\bottomrule
\end{tabular}
\end{table}

\section{Matrice des autorisations}
\begin{table}[H]
\centering
\caption{Matrice des droits}
\begin{tabular}{p{5cm}cc}
\toprule
\textbf{Fonction} & \textbf{Admin} & \textbf{Employé}\\
\midrule
Gérer les employés & Oui & Non\\
Planifier les interventions & Oui & Non\\
Consulter les interventions & Toutes & Les siennes\\
Créer des frais & Non & Oui, pour ses interventions\\
Modifier ou supprimer des frais & Non & Oui, pour ses frais\\
Observer les frais & Tous & Les siens\\
Vérifier les frais & Oui & Non\\
Consulter les rapports & Globaux & Personnels\\
Exporter CSV & Oui & Oui, sur son périmètre\\
\bottomrule
\end{tabular}
\end{table}

\section{Nouvelle fonctionnalité de rapports}
Le module Rapports et Statistiques constitue l'amélioration ajoutée à la version finale. Il permet de choisir une période, de calculer les totaux des frais, de regrouper les dépenses par statut, par employé et par intervention, puis d'exporter les résultats au format CSV.

Cette fonctionnalité améliore la valeur du projet car elle transforme les données saisies en informations exploitables. L'administrateur dispose d'une vision globale, tandis que l'employé conserve une vision limitée à son propre périmètre.

\section{Règles de gestion}
\begin{itemize}
  \item Un employé doit être lié à une fiche employé.
  \item Un employé ne peut déclarer des frais que pour ses propres interventions.
  \item Une dépense doit être liée à une intervention existante.
  \item L'administrateur observe les frais mais ne les crée pas.
  \item Les rapports respectent les mêmes règles de sécurité que les autres modules.
  \item Les dates de fin d'intervention doivent être supérieures ou égales aux dates de début.
\end{itemize}

\chapter{Conception et architecture}
\section{Architecture logique}
L'application repose sur une architecture client-serveur. Le frontend React communique avec le backend FastAPI à travers des endpoints REST. Le backend valide les données avec Pydantic, manipule les entités avec SQLAlchemy et stocke les informations dans SQLite.

\begin{figure}[H]
\centering
\includegraphics[width=0.92\textwidth]{assets/architecture_source.png}
\caption{Architecture logique de l'application}
\end{figure}

\section{Diagramme de cas d'utilisation}
\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{assets/01_use_case_caidelec.png}
\caption{Diagramme de cas d'utilisation avec module rapports}
\end{figure}

\section{Diagramme de classes}
\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{assets/02_class_caidelec.png}
\caption{Diagramme de classes corrigé}
\end{figure}

\section{Diagramme de séquence}
\begin{figure}[H]
\centering
\includegraphics[width=\textwidth]{assets/03_sequence_rapports_caidelec.png}
\caption{Séquence de consultation des rapports et export CSV}
\end{figure}

\section{Diagramme d'activité}
\begin{figure}[H]
\centering
\includegraphics[width=0.82\textwidth]{assets/04_activity_caidelec.png}
\caption{Diagramme d'activité avec rapports statistiques}
\end{figure}

\chapter{Réalisation de l'application}
\section{Technologies utilisées}
\begin{table}[H]
\centering
\caption{Technologies utilisées}
\begin{tabular}{p{4cm}p{9cm}}
\toprule
\textbf{Technologie} & \textbf{Utilisation}\\
\midrule
FastAPI & Création des endpoints REST.\\
SQLAlchemy & Modélisation et accès à la base de données.\\
SQLite & Stockage local pendant la phase de développement.\\
JWT & Authentification et transport du rôle utilisateur.\\
React Vite & Interface utilisateur.\\
Axios & Communication entre frontend et backend.\\
StarUML & Réalisation des diagrammes UML.\\
LaTeX & Génération du rapport final.\\
\bottomrule
\end{tabular}
\end{table}

\section{Modules backend}
Le backend contient les modules d'authentification, d'employés, d'interventions, de frais et de rapports. Le nouvel endpoint \texttt{/reports/summary} accepte une période et retourne les indicateurs selon le rôle de l'utilisateur connecté.

\section{Modules frontend}
Le frontend propose une navigation adaptée au rôle. L'administrateur voit le tableau de bord, les employés, les interventions, les frais et les rapports. L'employé voit ses interventions, ses frais et ses rapports personnels.

\section{Captures de l'application}
\begin{figure}[H]
\centering
\includegraphics[width=0.88\textwidth]{assets/login_screen.jpg}
\caption{Écran d'authentification}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=0.88\textwidth]{assets/dashboard_screen.jpg}
\caption{Tableau de bord avec calendrier}
\end{figure}

\chapter{Validation et résultats}
\section{Vérifications techniques}
\begin{longtable}{p{5cm}p{6cm}p{2cm}}
\caption{Vérifications réalisées}\\
\toprule
\textbf{Test} & \textbf{Résultat attendu} & \textbf{Statut}\\
\midrule
Connexion admin & Accès au dashboard et aux modules d'administration & Validé\\
Création employé & Création de la fiche et du compte lié & Validé\\
Planification intervention & Affichage dans liste et calendrier & Validé\\
Connexion employé & Affichage des données personnelles uniquement & Validé\\
Déclaration frais & Frais lié à une intervention de l'employé & Validé\\
Justificatif photo & Preuve visible avant vérification & Validé\\
Rapports admin & Statistiques globales par période & Validé\\
Rapports employé & Statistiques limitées à l'employé connecté & Validé\\
Export CSV & Fichier exploitable avec totaux et regroupements & Validé\\
\bottomrule
\end{longtable}

\section{Scénario de démonstration}
Le scénario de démonstration consiste à se connecter comme administrateur, créer un employé, planifier une intervention, se connecter comme employé, déclarer des frais avec justificatif, revenir comme administrateur pour observer les frais, puis ouvrir le module Rapports pour consulter les indicateurs et exporter le CSV.

\section{Résultats obtenus}
La version finale couvre les besoins prioritaires et ajoute une fonctionnalité de pilotage. Les données ne sont plus seulement enregistrées ; elles peuvent aussi être consultées, filtrées et exportées.

\chapter{Conclusion générale et perspectives}
Le projet CAIDELEC a permis de développer une application web cohérente avec le besoin de planification des interventions et de suivi des frais de déplacement. La solution distingue clairement l'administrateur et l'employé, sécurise les actions sensibles et centralise les informations principales.

L'ajout du module Rapports et Statistiques améliore la consistance du projet. Il répond à la nécessité d'ajouter une fonctionnalité pertinente et démontrable, en cohérence avec le cahier des charges. Les prochaines évolutions peuvent porter sur les notifications, l'historique des validations, l'export PDF et le passage vers une base PostgreSQL.

\chapter*{Références bibliographiques}
\addcontentsline{toc}{chapter}{Références bibliographiques}
\begin{itemize}
  \item Documentation FastAPI, conception des APIs REST.
  \item Documentation SQLAlchemy, modélisation ORM.
  \item Documentation React, création d'interfaces utilisateur.
  \item Documentation StarUML, conception UML.
  \item Supports internes CAIDELEC, format des affectations et besoins métier.
\end{itemize}

\appendix
\chapter{Exécution de la version livrée}
\section{Lancement du backend}
\begin{verbatim}
cd C:\Users\user\caidelec-backend
.venv\Scripts\activate
python -m uvicorn app.main:app --reload
\end{verbatim}

\section{Lancement du frontend}
\begin{verbatim}
cd C:\Users\user\caidelec-frontend
npm run dev
\end{verbatim}

\chapter{Fichiers StarUML}
Les fichiers StarUML sont fournis dans le dossier \texttt{staruml\_caidelec\_corrige\_2026}. Ils contiennent les diagrammes de cas d'utilisation, de classes, de séquence et d'activité. Les images intégrées dans ce rapport sont exportées depuis ces diagrammes afin de garder une présentation claire.

\end{document}
"""


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    ASSETS.mkdir(parents=True)

    copy_file(MEDIA / "image2.png", ASSETS / "uic_logo.png")
    copy_file(MEDIA / "image1.jpeg", ASSETS / "caidelec_logo.jpeg")
    copy_file(MEDIA / "image4.png", ASSETS / "architecture_source.png")
    copy_file(MEDIA / "image8.jpg", ASSETS / "login_screen.jpg")
    copy_file(MEDIA / "image13.jpg", ASSETS / "dashboard_screen.jpg")

    for name in [
        "01_use_case_caidelec.png",
        "02_class_caidelec.png",
        "03_sequence_rapports_caidelec.png",
        "04_activity_caidelec.png",
    ]:
        copy_file(DIAGRAM_SRC / name, ASSETS / name)

    shutil.copytree(STARUML_SRC, OUT / "staruml_caidelec_corrige_2026")
    shutil.copytree(DIAGRAM_SRC, OUT / "uml_diagrams_corrige_2026")

    (OUT / "main.tex").write_text(MAIN_TEX.strip() + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(
        """# Rapport PFE CAIDELEC LaTeX

Ce dossier contient le rapport final en LaTeX.

## Compilation

Dans Overleaf, importer tout le dossier puis compiler `main.tex`.

En local avec MiKTeX ou TeX Live :

```bash
pdflatex main.tex
pdflatex main.tex
pdflatex main.tex
```

La table des matières, la liste des figures et la liste des tableaux sont générées automatiquement.

## Diagrammes UML

Les fichiers StarUML se trouvent dans `staruml_caidelec_corrige_2026`.
Les images intégrées au rapport se trouvent dans `assets`.
""",
        encoding="utf-8",
    )

    zip_path = BASE / "Rapport-PFE-CAIDELEC-LaTeX-final.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in OUT.rglob("*"):
            zf.write(path, path.relative_to(OUT.parent))

    print(OUT)
    print(zip_path)


if __name__ == "__main__":
    build()
