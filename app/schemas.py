from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    phone: str
    email: str | None = None
    full_name: str | None = None
    role: str = "farmer"
    county: str = "Uasin Gishu"
    farm_size_acres: float | None = None
    soil_type: str | None = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CropPlanBase(BaseModel):
    user_id: str
    crop_type: str
    acres: float
    planting_date: date | None = None
    expected_yield_kg_per_acre: int | None = None
    season_year: int


class CropPlanCreate(CropPlanBase):
    pass


class CropPlanRead(CropPlanBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InputUsageBase(BaseModel):
    user_id: str
    crop_plan_id: str
    item_name: str
    category: str
    quantity: float | None = None
    unit: str | None = None
    cost_ksh: float = 0
    acres_applied: float | None = None
    application_date: date | None = None
    notes: str | None = None


class InputUsageCreate(InputUsageBase):
    pass


class InputUsageRead(InputUsageBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HarvestRecordBase(BaseModel):
    crop_plan_id: str
    actual_yield_kg_total: float | None = None
    selling_price_per_kg: float | None = None
    other_costs_ksh: float = 0


class HarvestRecordCreate(HarvestRecordBase):
    pass


class HarvestRecordRead(HarvestRecordBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FertilizerRecommendationBase(BaseModel):
    crop_type: str
    soil_type: str | None = None
    county: str = "Uasin Gishu"
    basal_fertilizer: str | None = None
    basal_kg_per_acre: float | None = None
    basal_application_timing: str | None = None
    top_dress_fertilizer: str | None = None
    top_dress_kg_per_acre: float | None = None
    top_dress_application_timing: str | None = None
    top_dress_splits: int = 1
    confidence_level: str = "baseline"
    source_reference: str | None = None
    notes: str | None = None


class FertilizerRecommendationRead(FertilizerRecommendationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
