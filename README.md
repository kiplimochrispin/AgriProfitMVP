# AgriProfit

AgriProfit is a PostgreSQL-ready farm operations and profit dashboard with a FastAPI backend and a TypeScript browser app.

## What the app includes

- FastAPI routes for users, crop plans, inputs, harvests, auth, analytics, and fertilizer recommendations
- TypeScript browser dashboard with authenticated CRUD management
- PostgreSQL-ready runtime with SQLite fallback for quick local use
- App status and data overview endpoints for dashboard-style operations
- Audit log history for create, update, and delete actions
- Installable web app shell with manifest and service worker
- Restore helper for PostgreSQL dumps
- Backup and restore verification scripts for PostgreSQL
- Alembic migration baseline for schema upgrades
- Health endpoints and structured request logging

## Structure

```text
agriprofit/
├── app/
├── alembic/
├── scripts/
├── src/frontend/
├── static/
├── templates/
├── tests/
├── docker-compose.yml
└── package.json
```

## Quick start

1. Create and activate a virtual environment.
2. Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

3. Build the frontend:

```bash
npm install
npm run build:frontend
```

4. Copy `.env.example` to `.env`.
5. Start PostgreSQL with Docker Compose:

```bash
docker compose up -d db
```

6. Run migrations:

```bash
.venv/bin/alembic upgrade head
```

7. Start the app:

```bash
python3 -m uvicorn app.main:app --reload
```

8. Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## Core routes

- `POST /auth/login`
- `GET /health/live`
- `GET /health/ready`
- `GET /api/status`
- `GET /audit-logs`
- `GET /analytics/overview`
- `GET /analytics/dashboard`
- `GET /analytics/fertilizer-recommendation?crop=maize&soil_type=loam&acres=2`
- `GET|POST|PATCH|DELETE /users`
- `GET|POST|PATCH|DELETE /crop-plans`
- `GET|POST|PATCH|DELETE /inputs`
- `GET|POST|PATCH|DELETE /harvests`

## Connect PostgreSQL

Set `DATABASE_URL` in `.env` using the format from `.env.example`:

```env
DATABASE_URL=postgresql+psycopg2://agriprofit:agriprofit@localhost:5432/agriprofit
```

You can use:

- Local PostgreSQL
- Docker Compose with [`docker-compose.yml`](/home/chris/Chris/agriprofit/docker-compose.yml)
- A hosted PostgreSQL instance

## Restore PostgreSQL data

Use the restore helper with either a `.sql` dump or a custom `pg_dump` archive:

```bash
./scripts/restore_postgres.sh backup.dump
```

Create a backup:

```bash
./scripts/backup_postgres.sh
```

Verify that a backup restores into a temporary PostgreSQL database:

```bash
./scripts/verify_restore.sh backups/agriprofit_YYYYMMDD_HHMMSS.dump
```

You can also pass an explicit connection string:

```bash
./scripts/restore_postgres.sh backup.sql postgresql://agriprofit:agriprofit@localhost:5432/agriprofit
```

## Web app notes

- The homepage at `/` is rendered from [`src/frontend/main.ts`](/home/chris/Chris/agriprofit/src/frontend/main.ts).
- The browser app exposes live database mode, record counts, and recent activity.
- The app can be installed as a PWA through the browser when the platform supports `beforeinstallprompt`.
- Mutating routes require login.
- HTTP requests are logged in structured JSON format by the FastAPI app.

## Run tests

```bash
npm run build:frontend
.venv/bin/python -m unittest tests/test_app_flows.py
```

## Deployment

- A starter [`Dockerfile`](/home/chris/Chris/agriprofit/Dockerfile) is included for container deployment.
- [`docker-compose.yml`](/home/chris/Chris/agriprofit/docker-compose.yml) provides a local PostgreSQL-backed stack.
- The web container waits for PostgreSQL, runs `alembic upgrade head`, and then starts Uvicorn through [`start_web.sh`](/home/chris/Chris/agriprofit/scripts/start_web.sh).
- Replace the default admin credentials and `SECRET_KEY` before any real deployment.
