# AgriProfit Python

This version of AgriProfit runs as a simple Python API.

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

- By default, the API works without a database and returns built-in sample dashboard data.
- If you want to enable PostgreSQL later, set `DATABASE_URL` before starting the server.
- The most useful standalone endpoints right now are:
  - `/analytics/dashboard`
  - `/analytics/fertilizer-recommendation?crop=maize&soil_type=loam&acres=2`
