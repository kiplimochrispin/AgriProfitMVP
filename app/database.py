import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")


def load_local_env():
    if not os.path.exists(ENV_PATH):
        return

    with open(ENV_PATH, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


load_local_env()

DEFAULT_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'agriprofit.db')}"
DATABASE_URL = os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL

engine = (
    create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    )
    if DATABASE_URL
    else None
)
SessionLocal = (
    sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine is not None else None
)
Base = declarative_base()

SEED_RECOMMENDATIONS = [
    {
        "crop_type": "maize",
        "soil_type": "loam",
        "county": "Uasin Gishu",
        "basal_fertilizer": "DAP",
        "basal_kg_per_acre": 80.0,
        "basal_application_timing": "At planting",
        "top_dress_fertilizer": "Urea or CAN",
        "top_dress_kg_per_acre": 60.0,
        "top_dress_application_timing": "First top dress at knee height, second before tasseling if split",
        "top_dress_splits": 2,
        "confidence_level": "baseline",
        "source_reference": "Kenya Ministry guidance and Uasin Gishu studies",
        "notes": "Sample local baseline for MVP use. Confirm with soil test and county extension guidance.",
    },
    {
        "crop_type": "maize",
        "soil_type": "clay",
        "county": "Uasin Gishu",
        "basal_fertilizer": "DAP",
        "basal_kg_per_acre": 60.0,
        "basal_application_timing": "At planting",
        "top_dress_fertilizer": "CAN or Urea",
        "top_dress_kg_per_acre": 55.0,
        "top_dress_application_timing": "Top dress at 4 to 6 weeks after emergence",
        "top_dress_splits": 1,
        "confidence_level": "baseline",
        "source_reference": "Kenya Ministry guidance and Uasin Gishu studies",
        "notes": "Sample local baseline for heavier Rift Valley soils. Confirm with soil test and county extension guidance.",
    },
    {
        "crop_type": "maize",
        "soil_type": "sand",
        "county": "Uasin Gishu",
        "basal_fertilizer": "NPK 23:23:0",
        "basal_kg_per_acre": 45.0,
        "basal_application_timing": "At planting",
        "top_dress_fertilizer": "CAN",
        "top_dress_kg_per_acre": 45.0,
        "top_dress_application_timing": "Apply smaller split top-dress doses between 3 and 6 weeks after emergence",
        "top_dress_splits": 2,
        "confidence_level": "baseline",
        "source_reference": "Local agronomy baseline adapted for lighter soils",
        "notes": "Sample local baseline for lighter soils. Monitor leaching and confirm with soil test where possible.",
    },
    {
        "crop_type": "potato",
        "soil_type": "loam",
        "county": "Uasin Gishu",
        "basal_fertilizer": "NPK 17:17:17",
        "basal_kg_per_acre": 110.0,
        "basal_application_timing": "At planting in bands away from seed",
        "top_dress_fertilizer": "CAN",
        "top_dress_kg_per_acre": 50.0,
        "top_dress_application_timing": "At first earthing up",
        "top_dress_splits": 1,
        "confidence_level": "placeholder",
        "source_reference": "Regional potato production guidance for Rift Valley",
        "notes": "Draft local placeholder for MVP use. Likely conservative; confirm with soil test and county extension guidance.",
    },
    {
        "crop_type": "wheat",
        "soil_type": "loam",
        "county": "Uasin Gishu",
        "basal_fertilizer": "DAP",
        "basal_kg_per_acre": 40.0,
        "basal_application_timing": "At planting",
        "top_dress_fertilizer": "Urea or CAN",
        "top_dress_kg_per_acre": 30.0,
        "top_dress_application_timing": "At early tillering",
        "top_dress_splits": 1,
        "confidence_level": "placeholder",
        "source_reference": "Regional wheat agronomy guidance for Rift Valley",
        "notes": "Draft local placeholder for MVP use. Confirm with county extension guidance for the target wheat zone.",
    },
]


def init_db():
    if engine is None:
        return
    from app import models

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.FertilizerRecommendation).count() == 0:
            db.add_all(models.FertilizerRecommendation(**item) for item in SEED_RECOMMENDATIONS)
            db.commit()
    finally:
        db.close()


def get_db():
    if SessionLocal is None:
        yield None
        return

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
