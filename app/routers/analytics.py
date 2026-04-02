from fastapi import APIRouter, Depends, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.calculations import calculate_fertilizer_needs
from app.database import get_db

router = APIRouter()


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

    query = text(
        """
        SELECT calculate_fertilizer_needs_db(
            :crop,
            :soil_type,
            :acres,
            :county
        ) AS recommendation
        """
    )
    try:
        result = db.execute(
            query,
            {
                "crop": crop,
                "soil_type": soil_type,
                "acres": acres,
                "county": county,
            },
        ).scalar_one_or_none()
    except SQLAlchemyError:
        return calculate_fertilizer_needs(crop, soil_type, acres)

    if result is not None and "error" not in result:
        return result

    return calculate_fertilizer_needs(crop, soil_type, acres)


@router.get("/profit-loss/{crop_plan_id}")
def get_profit_loss(crop_plan_id: str, db: Session = Depends(get_db)):
    if db is None:
        return {"error": "Database mode is disabled. Set DATABASE_URL to enable saved crop plans."}

    query = text(
        """
        SELECT
            cp.id AS crop_plan_id,
            cp.crop_type,
            cp.acres,
            COALESCE(plv.total_revenue_ksh, 0) AS total_revenue_ksh,
            COALESCE(plv.total_cost_ksh, 0) AS total_cost_ksh,
            COALESCE(plv.profit_loss_ksh, 0) AS profit_loss_ksh,
            COALESCE(plv.profit_per_acre_ksh, 0) AS profit_per_acre_ksh,
            CASE
                WHEN COALESCE(plv.total_cost_ksh, 0) > 0
                    THEN ROUND((plv.profit_loss_ksh / plv.total_cost_ksh) * 100, 1)
                ELSE 0
            END AS roi_percent
        FROM crop_plans cp
        LEFT JOIN profit_loss_view plv ON plv.crop_plan_id = cp.id
        WHERE cp.id = CAST(:crop_plan_id AS uuid)
        """
    )
    try:
        row = db.execute(query, {"crop_plan_id": crop_plan_id}).mappings().first()
    except SQLAlchemyError:
        return {"error": "Database is unavailable. Set DATABASE_URL to enable saved crop plans."}

    if row is None:
        return {"error": "Crop plan not found"}

    return dict(row)


@router.get("/dashboard")
def get_dashboard(
    user_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if user_id and db is not None:
        try:
            dashboard = db.execute(
                text("SELECT get_profit_dashboard_db(CAST(:user_id AS uuid)) AS dashboard"),
                {"user_id": user_id},
            ).scalar_one()

            if dashboard:
                summary = db.execute(
                    text(
                        """
                        SELECT
                            COALESCE(SUM(plv.total_revenue_ksh), 0) AS total_revenue_ksh,
                            COALESCE(SUM(plv.total_cost_ksh), 0) AS total_cost_ksh,
                            MAX(cp.crop_type) AS crop_type,
                            COALESCE(SUM(cp.acres), 0) AS acres
                        FROM crop_plans cp
                        LEFT JOIN profit_loss_view plv ON plv.crop_plan_id = cp.id
                        WHERE cp.user_id = CAST(:user_id AS uuid)
                          AND cp.season_year = (
                              SELECT MAX(season_year) FROM crop_plans WHERE user_id = CAST(:user_id AS uuid)
                          )
                        """
                    ),
                    {"user_id": user_id},
                ).mappings().first()

                fertilizer = dashboard.get("fertilizer_comparison", {})
                used = fertilizer.get("used_per_acre", [0])
                recommended = fertilizer.get("recommended_per_acre", [0])

                return {
                    "profit_loss_ksh": dashboard.get("profit_loss_ksh", 0),
                    "profit_per_acre_ksh": dashboard.get("profit_per_acre_ksh", 0),
                    "roi_percent": dashboard.get("roi_percent", 0),
                    "total_revenue_ksh": summary["total_revenue_ksh"] if summary else 0,
                    "total_cost_ksh": summary["total_cost_ksh"] if summary else 0,
                    "crop_type": summary["crop_type"] if summary else None,
                    "acres": summary["acres"] if summary else 0,
                    "profit_history": dashboard.get("profit_history", []),
                    "seasons": dashboard.get("seasons", []),
                    "avg_fert_used": used[0] if used else 0,
                    "recommended_fert": recommended[0] if recommended else 0,
                    "season_year": dashboard.get("season_year"),
                    "over_under_fert_percent": dashboard.get("over_under_fert_percent", 0),
                    "fertilizer_comparison": fertilizer,
                }
        except SQLAlchemyError:
            pass

    return fallback_dashboard()
