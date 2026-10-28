# CAIDELEC Planning

Application PFE pour digitaliser la planification quotidienne des interventions, le suivi de presence et les frais de deplacement des equipes terrain.

## Objectifs

- Centraliser le planning quotidien des techniciens.
- Gérer les presences, conges, absences et indisponibilites.
- Suivre les frais de deplacement par intervention.
- Donner une interface fluide a la reception pour saisir et consulter rapidement les donnees.
- Produire une synthese mensuelle exportable pour la comptabilite.
- Securiser l'acces avec des roles: admin, reception, comptable et manager.

## Architecture

- Backend: FastAPI, Pydantic, SQLAlchemy.
- Frontend: React, TypeScript, Vite.
- Base de donnees: PostgreSQL.
- DevOps: Docker, Docker Compose.
- Documentation API: Swagger/OpenAPI disponible via FastAPI.

## Lancement rapide

```bash
docker compose up --build
```

Ensuite:

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

Compte demo:

- Admin: `admin@caidelec.local` / `admin123`
- Reception: `reception@caidelec.local` / `reception123`
- Comptable: `comptable@caidelec.local` / `comptable123`
- Manager: `manager@caidelec.local` / `manager123`

## Lancement local sans Docker

Terminal 1, backend:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd backend
..\.venv\Scripts\python.exe -m app.db.seed
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2, frontend:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Si la page affiche `Failed to fetch`, cela veut dire que le backend n'est pas encore lance sur `http://localhost:8000`.

## Structure

```text
backend/
  app/
    api/        Endpoints REST
    core/       Configuration et securite
    db/         Session database et seed
    models/     Modeles SQLAlchemy
    schemas/    Schemas Pydantic
frontend/
  src/          Interface React
database/
  001_init.sql  Migration SQL initiale
docs/
  analyse-fonctionnelle.md
```

## Livrables PFE couverts

- Code source backend/frontend structure.
- Configuration Docker Compose.
- Base PostgreSQL avec migration initiale.
- API documentee automatiquement.
- Interface web de demonstration.
- Formulaires de saisie pour ajouter employes, interventions et frais.
- Document d'analyse fonctionnelle pour le rapport.
