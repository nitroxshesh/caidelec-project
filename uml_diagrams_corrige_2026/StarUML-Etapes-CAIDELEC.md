# CAIDELEC - Etapes StarUML

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
2. Ajouter lifelines : Utilisateur, Frontend React, Backend FastAPI, ReportService, SQLite, Fichier CSV.
3. Ajouter le scenario : choix de periode, GET /reports/summary, verification du role, chargement des interventions, calcul des frais et export CSV.
4. Ajouter fragment alt : admin voit tout / employe voit seulement ses donnees.
5. Garder les messages courts pour que le diagramme reste lisible.

## 4. Diagramme d'activite
1. Creer un Activity Diagram.
2. Ajouter start, login, verification identifiants.
3. Ajouter decision role admin.
4. Branche admin : dashboard, employes, interventions, verifier frais, export Excel.
5. Branche employe : mes interventions, declarer frais, justificatif photo, mes frais.
6. Ajouter final node.
