# AgriProfit Python

This version of AgriProfit runs as a Python API with a live browser homepage, SQLite by default, and authenticated record management.

## Run locally

1. Create or activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the API:

```bash
uvicorn app.main:app --reload
```

4. Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## Notes

- By default, the app now uses a local SQLite database at `agriprofit.db`.
- If you want to use PostgreSQL later, set `DATABASE_URL` before starting the server.
- The homepage at `/` includes live forms for creating farmers, crop plans, inputs, and harvests.
- Create a local `.env` from `.env.example` if you want to override database or admin credentials.
- Mutating routes now require login.
- The most useful standalone endpoints right now are:
  - `/auth/login`
  - `/analytics/dashboard`
  - `/analytics/fertilizer-recommendation?crop=maize&soil_type=loam&acres=2`

## Run Tests

```bash
python -m unittest tests/test_app_flows.py
```

## Deployment

- A starter [`Dockerfile`](/home/chris/Chris/agriprofit/Dockerfile) is included for container deployment.
- Use `.env.example` as the basis for production environment variables.
- Replace the default admin credentials and `SECRET_KEY` before any real deployment.
