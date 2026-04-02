from datetime import date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="farmer")
    county: Mapped[str] = mapped_column(String(100), default="Uasin Gishu")
    farm_size_acres: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CropPlan(Base):
    __tablename__ = "crop_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    crop_type: Mapped[str] = mapped_column(String(100))
    acres: Mapped[float] = mapped_column(Numeric(10, 2))
    planting_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expected_yield_kg_per_acre: Mapped[int | None] = mapped_column(Integer, nullable=True)
    season_year: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InputUsage(Base):
    __tablename__ = "input_usage"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    crop_plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("crop_plans.id"), index=True)
    item_name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(50))
    quantity: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cost_ksh: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    acres_applied: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    application_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HarvestRecord(Base):
    __tablename__ = "harvest_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    crop_plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("crop_plans.id"), unique=True, index=True
    )
    actual_yield_kg_total: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    selling_price_per_kg: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    other_costs_ksh: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FertilizerRecommendation(Base):
    __tablename__ = "fertilizer_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_type: Mapped[str] = mapped_column(String(50), index=True)
    soil_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    county: Mapped[str] = mapped_column(String(100), default="Uasin Gishu")
    basal_fertilizer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    basal_kg_per_acre: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    basal_application_timing: Mapped[str | None] = mapped_column(String(100), nullable=True)
    top_dress_fertilizer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    top_dress_kg_per_acre: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    top_dress_application_timing: Mapped[str | None] = mapped_column(String(100), nullable=True)
    top_dress_splits: Mapped[int] = mapped_column(Integer, default=1)
    confidence_level: Mapped[str] = mapped_column(String(20), default="baseline")
    source_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
