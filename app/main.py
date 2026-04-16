from pathlib import Path
import json
import logging
import os
import time

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import (
    DATABASE_URL,
    database_backend,
    database_is_ready,
    init_db,
    using_default_sqlite,
)
from app.routers.analytics import router as analytics_router
from app.routers.audit_logs import router as audit_logs_router
from app.routers.auth import router as auth_router
from app.routers.crop_plans import router as crop_plans_router
from app.routers.harvests import router as harvests_router
from app.routers.inputs import router as inputs_router
from app.routers.users import router as users_router

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
logger = logging.getLogger("agriprofit.http")
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000").split(",") if origin.strip()]
APP_SHELL = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AgriProfit MVP</title>
    <meta name="theme-color" content="#203328" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-title" content="AgriProfit" />
    <link rel="manifest" href="/static/manifest.webmanifest" />
    <link rel="icon" href="/static/icon.svg" type="image/svg+xml" />
    <link rel="stylesheet" href="/static/styles.css" />
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/static/main.js"></script>
  </body>
</html>
"""

app = FastAPI(title="AgriProfit MVP - Uasin Gishu", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        json.dumps(
            {
                "event": "http_request",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client": request.client.host if request.client else None,
            }
        )
    )
    return response


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", include_in_schema=False)
def read_root():
    return HTMLResponse(APP_SHELL)


@app.get("/dashboard", include_in_schema=False)
@app.get("/dashboard/{path:path}", include_in_schema=False)
def read_dashboard(path: str = ""):
    return HTMLResponse(APP_SHELL)


@app.get("/api")
def api_status():
    return {
        "message": "AgriProfit Python API is running.",
        "docs": "/docs",
        "dashboard": "/analytics/dashboard",
    }


@app.get("/health/live")
def live_health():
    return {"status": "ok"}


@app.get("/health/ready")
def ready_health():
    db_ready = database_is_ready()
    status_code = 200 if db_ready else 503
    payload = {
        "status": "ready" if db_ready else "degraded",
        "database": {
            "backend": database_backend(),
            "ready": db_ready,
            "using_default_sqlite": using_default_sqlite(),
        },
    }
    return JSONResponse(content=payload, status_code=status_code)


@app.get("/api/status")
def app_status():
    return {
        "name": "AgriProfit",
        "docs": "/docs",
        "dashboard": "/analytics/dashboard",
        "installable_web_app": True,
        "health": {
            "live": "/health/live",
            "ready": "/health/ready",
        },
        "database": {
            "backend": database_backend(),
            "configured": bool(DATABASE_URL),
            "using_default_sqlite": using_default_sqlite(),
        },
    }


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(audit_logs_router, prefix="/audit-logs", tags=["audit-logs"])
app.include_router(crop_plans_router, prefix="/crop-plans", tags=["crop-plans"])
app.include_router(inputs_router, prefix="/inputs", tags=["inputs"])
app.include_router(harvests_router, prefix="/harvests", tags=["harvests"])
