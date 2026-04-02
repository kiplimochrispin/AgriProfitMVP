from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers.analytics import router as analytics_router
from app.routers.crop_plans import router as crop_plans_router
from app.routers.harvests import router as harvests_router
from app.routers.inputs import router as inputs_router
from app.routers.users import router as users_router

app = FastAPI(title="AgriProfit MVP - Uasin Gishu", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def read_root():
    return {
        "message": "AgriProfit Python API is running.",
        "docs": "/docs",
        "dashboard": "/analytics/dashboard",
    }


app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(crop_plans_router, prefix="/crop-plans", tags=["crop-plans"])
app.include_router(inputs_router, prefix="/inputs", tags=["inputs"])
app.include_router(harvests_router, prefix="/harvests", tags=["harvests"])
