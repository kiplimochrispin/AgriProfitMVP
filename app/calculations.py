from typing import Any

FERTILIZER_RECS: dict[str, dict[str, dict[str, Any]]] = {
    "maize": {
        "loam": {
            "basal": "DAP or NPK 23:23:0",
            "basal_kg": 50,
            "top": "CAN",
            "top_kg": 50,
            "notes": "Standard Uasin Gishu recommendation",
        },
        "clay": {
            "basal": "DAP",
            "basal_kg": 60,
            "top": "CAN",
            "top_kg": 55,
            "notes": "Higher rate for Rift Valley clay soils",
        },
    },
    "potato": {
        "loam": {
            "basal": "DAP",
            "basal_kg": 110,
            "top": "CAN",
            "top_kg": 50,
            "notes": "High phosphorus for tuber development",
        },
    },
    "wheat": {
        "loam": {
            "basal": "DAP",
            "basal_kg": 40,
            "top": "CAN",
            "top_kg": 30,
            "notes": "Top-dress at tillering stage",
        },
    },
}

AVG_FERT_PRICE_KG = 65.0


def calculate_fertilizer_needs(crop: str, soil_type: str, acres: float) -> dict[str, Any]:
    rec = FERTILIZER_RECS.get(crop.lower(), {}).get(soil_type.lower())
    if not rec:
        return {"error": "No recommendation available yet for this crop/soil"}

    basal_total = rec["basal_kg"] * acres
    top_total = rec["top_kg"] * acres
    total_kg = basal_total + top_total
    est_cost = round(total_kg * AVG_FERT_PRICE_KG, 2)

    return {
        "crop": crop,
        "soil_type": soil_type,
        "acres": acres,
        "basal": f"{rec['basal']} - {basal_total:.1f} kg",
        "top_dress": f"{rec['top']} - {top_total:.1f} kg",
        "total_fertilizer_kg": round(total_kg, 1),
        "estimated_cost_ksh": est_cost,
        "notes": rec["notes"],
    }


def calculate_profit_loss(
    revenue: float, input_cost: float, other_costs: float, acres: float
) -> dict[str, float]:
    total_cost = input_cost + other_costs
    profit = revenue - total_cost
    return {
        "total_revenue_ksh": round(revenue, 2),
        "total_cost_ksh": round(total_cost, 2),
        "profit_loss_ksh": round(profit, 2),
        "profit_per_acre_ksh": round(profit / acres, 2) if acres > 0 else 0,
        "roi_percent": round((profit / total_cost) * 100, 1) if total_cost > 0 else 0,
    }
