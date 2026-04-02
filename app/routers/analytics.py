from collections import defaultdict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import models
from app.calculations import calculate_fertilizer_needs
from app.database import get_db

router = APIRouter()


def as_float(value, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def fallback_dashboard():
    return {
        "profit_loss_ksh": 18500,
        "profit_per_acre_ksh": 9250,
        "roi_percent": 42.5,
        "total_revenue_ksh": 62000,
        "total_cost_ksh": 43500,
        "crop_type": "maize",
        "acres": 2,
        "profit_history": [12000, 8500, 18500],
        "seasons": ["2024", "2025", "2026"],
        "avg_fert_used": 65,
        "recommended_fert": 50,
        "season_year": "2026",
        "over_under_fert_percent": 30,
        "fertilizer_comparison": {
            "labels": ["Maize"],
            "used_per_acre": [65],
            "recommended_per_acre": [50],
        },
    }


def empty_dashboard():
    return {
        "profit_loss_ksh": 0,
        "profit_per_acre_ksh": 0,
        "roi_percent": 0,
        "total_revenue_ksh": 0,
        "total_cost_ksh": 0,
        "crop_type": None,
        "acres": 0,
        "profit_history": [],
        "seasons": [],
        "avg_fert_used": 0,
        "recommended_fert": 0,
        "season_year": None,
        "over_under_fert_percent": 0,
        "fertilizer_comparison": {
            "labels": [],
            "used_per_acre": [],
            "recommended_per_acre": [],
        },
    }


def recommendation_from_record(
    rec: models.FertilizerRecommendation, crop: str, soil_type: str, acres: float, county: str
):
    basal_rate = as_float(rec.basal_kg_per_acre)
    top_rate = as_float(rec.top_dress_kg_per_acre)
    total_kg = (basal_rate + top_rate) * acres
    return {
        "crop": crop,
        "soil_type": soil_type,
        "county": county,
        "acres": acres,
        "source_reference": rec.source_reference,
        "basal_fertilizer": f"{rec.basal_fertilizer or 'Basal'} {round(basal_rate * acres, 1)} kg",
        "top_dress_fertilizer": f"{rec.top_dress_fertilizer or 'Top dress'} {round(top_rate * acres, 1)} kg",
        "basal_application_timing": rec.basal_application_timing,
        "top_dress_application_timing": rec.top_dress_application_timing,
        "top_dress_splits": rec.top_dress_splits,
        "bag_estimate_50kg": {
            "basal_bags": round((basal_rate * acres) / 50.0, 2),
            "top_dress_bags": round((top_rate * acres) / 50.0, 2),
        },
        "per_acre": {
            "basal_fertilizer": rec.basal_fertilizer,
            "basal_kg_acre": basal_rate,
            "basal_application_timing": rec.basal_application_timing,
            "top_dress_fertilizer": rec.top_dress_fertilizer,
            "top_dress_kg_acre": top_rate,
            "top_dress_application_timing": rec.top_dress_application_timing,
            "top_dress_splits": rec.top_dress_splits,
        },
        "total_fertilizer_kg": round(total_kg, 1),
        "notes": rec.notes,
    }


def find_recommendation(db: Session, crop: str, soil_type: str | None, county: str):
    records = (
        db.query(models.FertilizerRecommendation)
        .filter(models.FertilizerRecommendation.crop_type.ilike(crop))
        .filter(models.FertilizerRecommendation.county.ilike(county))
        .all()
    )
    normalized_soil = (soil_type or "").strip().lower()
    for record in records:
        if (record.soil_type or "").lower() == normalized_soil:
            return record
    for record in records:
        if record.soil_type is None:
            return record
    return records[0] if records else None


def build_profit_loss(plan: models.CropPlan, inputs: list[models.InputUsage], harvest: models.HarvestRecord | None):
    total_input_cost = round(sum(as_float(item.cost_ksh) for item in inputs), 2)
    revenue = 0.0
    other_costs = 0.0
    if harvest is not None:
        revenue = round(
            as_float(harvest.actual_yield_kg_total) * as_float(harvest.selling_price_per_kg), 2
        )
        other_costs = as_float(harvest.other_costs_ksh)
    total_cost = round(total_input_cost + other_costs, 2)
    profit = round(revenue - total_cost, 2)
    acres = as_float(plan.acres)
    return {
        "crop_plan_id": plan.id,
        "crop_type": plan.crop_type,
        "acres": acres,
        "total_revenue_ksh": revenue,
        "total_cost_ksh": total_cost,
        "profit_loss_ksh": profit,
        "profit_per_acre_ksh": round(profit / acres, 2) if acres > 0 else 0,
        "roi_percent": round((profit / total_cost) * 100, 1) if total_cost > 0 else 0,
    }


def build_dashboard_for_user(db: Session, user: models.User):
    plans = db.query(models.CropPlan).filter(models.CropPlan.user_id == user.id).all()
    if not plans:
        return empty_dashboard()

    season_year = max(plan.season_year for plan in plans)
    all_plan_ids = [plan.id for plan in plans]
    inputs = (
        db.query(models.InputUsage)
        .filter(models.InputUsage.crop_plan_id.in_(all_plan_ids))
        .all()
        if all_plan_ids
        else []
    )
    harvests = (
        db.query(models.HarvestRecord)
        .filter(models.HarvestRecord.crop_plan_id.in_(all_plan_ids))
        .all()
        if all_plan_ids
        else []
    )
    inputs_by_plan = defaultdict(list)
    for item in inputs:
        inputs_by_plan[item.crop_plan_id].append(item)
    harvest_by_plan = {item.crop_plan_id: item for item in harvests}

    current_plans = [plan for plan in plans if plan.season_year == season_year]
    current_plan_ids = {plan.id for plan in current_plans}
    season_summary = {
        "profit_loss_ksh": 0.0,
        "total_revenue_ksh": 0.0,
        "total_cost_ksh": 0.0,
        "acres": 0.0,
    }
    season_profit_map = defaultdict(float)

    for plan in plans:
        profit = build_profit_loss(plan, inputs_by_plan.get(plan.id, []), harvest_by_plan.get(plan.id))
        season_profit_map[plan.season_year] += profit["profit_loss_ksh"]
        if plan.id in current_plan_ids:
            season_summary["profit_loss_ksh"] += profit["profit_loss_ksh"]
            season_summary["total_revenue_ksh"] += profit["total_revenue_ksh"]
            season_summary["total_cost_ksh"] += profit["total_cost_ksh"]
            season_summary["acres"] += profit["acres"]

    ordered_seasons = sorted(season_profit_map)
    crop_types = sorted({plan.crop_type for plan in current_plans})
    display_crop = crop_types[0] if len(crop_types) == 1 else "Mixed"

    crop_rows = []
    for crop_type in crop_types:
        crop_plan_group = [plan for plan in current_plans if plan.crop_type == crop_type]
        fert_inputs = []
        for plan in crop_plan_group:
            for item in inputs_by_plan.get(plan.id, []):
                if item.category.lower() == "fertilizer":
                    fert_inputs.append((plan, item))

        per_acre_values = []
        for plan, item in fert_inputs:
            quantity = as_float(item.quantity)
            acres_applied = as_float(item.acres_applied)
            plan_acres = as_float(plan.acres)
            divisor = acres_applied if acres_applied > 0 else plan_acres
            if quantity > 0 and divisor > 0:
                per_acre_values.append(quantity / divisor)

        used_per_acre = round(sum(per_acre_values) / len(per_acre_values), 2) if per_acre_values else 0.0
        rec = find_recommendation(db, crop_type, user.soil_type, user.county)
        recommended = 0.0
        if rec is not None:
            recommended = round(as_float(rec.basal_kg_per_acre) + as_float(rec.top_dress_kg_per_acre), 2)
        crop_rows.append((crop_type.title(), used_per_acre, recommended))

    labels = [row[0] for row in crop_rows]
    used_values = [row[1] for row in crop_rows]
    recommended_values = [row[2] for row in crop_rows]
    paired = [(used, rec) for used, rec in zip(used_values, recommended_values) if rec > 0]
    avg_used = round(sum(used_values) / len(used_values), 2) if used_values else 0.0
    avg_recommended = round(sum(recommended_values) / len(recommended_values), 2) if recommended_values else 0.0
    if paired:
        over_under = round(sum(((used - rec) / rec) * 100 for used, rec in paired) / len(paired), 2)
    else:
        over_under = 0.0

    acres = season_summary["acres"]
    total_cost = season_summary["total_cost_ksh"]
    total_profit = season_summary["profit_loss_ksh"]

    return {
        "profit_loss_ksh": round(total_profit, 2),
        "profit_per_acre_ksh": round(total_profit / acres, 2) if acres > 0 else 0,
        "roi_percent": round((total_profit / total_cost) * 100, 2) if total_cost > 0 else 0,
        "total_revenue_ksh": round(season_summary["total_revenue_ksh"], 2),
        "total_cost_ksh": round(total_cost, 2),
        "crop_type": display_crop.lower() if display_crop else None,
        "acres": round(acres, 2),
        "profit_history": [round(season_profit_map[year], 2) for year in ordered_seasons],
        "seasons": [str(year) for year in ordered_seasons],
        "avg_fert_used": avg_used,
        "recommended_fert": avg_recommended,
        "season_year": str(season_year),
        "over_under_fert_percent": over_under,
        "fertilizer_comparison": {
            "labels": labels,
            "used_per_acre": used_values,
            "recommended_per_acre": recommended_values,
        },
    }


@router.get("/fertilizer-recommendation")
def get_fertilizer_recommendation(
    crop: str,
    soil_type: str,
    acres: float,
    county: str = "Uasin Gishu",
    db: Session = Depends(get_db),
):
    if db is None:
        return calculate_fertilizer_needs(crop, soil_type, acres)

    try:
        recommendation = find_recommendation(db, crop, soil_type, county)
        if recommendation is not None:
            return recommendation_from_record(recommendation, crop, soil_type, acres, county)
    except SQLAlchemyError:
        pass

    return calculate_fertilizer_needs(crop, soil_type, acres)


@router.get("/profit-loss/{crop_plan_id}")
def get_profit_loss(crop_plan_id: str, db: Session = Depends(get_db)):
    if db is None:
        return {"error": "Database mode is disabled. Set DATABASE_URL to enable saved crop plans."}

    try:
        plan = db.query(models.CropPlan).filter(models.CropPlan.id == crop_plan_id).first()
        if plan is None:
            return {"error": "Crop plan not found"}
        inputs = db.query(models.InputUsage).filter(models.InputUsage.crop_plan_id == crop_plan_id).all()
        harvest = db.query(models.HarvestRecord).filter(models.HarvestRecord.crop_plan_id == crop_plan_id).first()
        return build_profit_loss(plan, inputs, harvest)
    except SQLAlchemyError:
        return {"error": "Database is unavailable. Set DATABASE_URL to enable saved crop plans."}


@router.get("/dashboard")
def get_dashboard(
    user_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if db is None:
        return fallback_dashboard()

    try:
        user = None
        if user_id:
            user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            user = db.query(models.User).order_by(models.User.created_at.desc()).first()
        if user is None:
            return fallback_dashboard()
        return build_dashboard_for_user(db, user)
    except SQLAlchemyError:
        return fallback_dashboard()
