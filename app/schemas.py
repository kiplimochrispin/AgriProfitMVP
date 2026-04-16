from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    phone: str
    email: str | None = None
    full_name: str | None = None
    role: str = "farmer"
    county: str = "Uasin Gishu"
    farm_size_acres: float | None = None
    soil_type: str | None = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = None
    phone: str | None = None
    email: str | None = None
    password: str | None = None
    is_active: bool | None = None
    full_name: str | None = None
    role: str | None = None
    county: str | None = None
    farm_size_acres: float | None = None
    soil_type: str | None = None


class AuthUserRead(BaseModel):
    id: str
    username: str
    phone: str
    email: str | None = None
    full_name: str | None = None
    role: str
    is_active: bool

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


class CropPlanUpdate(BaseModel):
    user_id: str | None = None
    crop_type: str | None = None
    acres: float | None = None
    planting_date: date | None = None
    expected_yield_kg_per_acre: int | None = None
    season_year: int | None = None


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


class InputUsageUpdate(BaseModel):
    user_id: str | None = None
    crop_plan_id: str | None = None
    item_name: str | None = None
    category: str | None = None
    quantity: float | None = None
    unit: str | None = None
    cost_ksh: float | None = None
    acres_applied: float | None = None
    application_date: date | None = None
    notes: str | None = None


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


class HarvestRecordUpdate(BaseModel):
    crop_plan_id: str | None = None
    actual_yield_kg_total: float | None = None
    selling_price_per_kg: float | None = None
    other_costs_ksh: float | None = None


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


class AuditLogRead(BaseModel):
    id: int
    actor: str
    action: str
    entity_type: str
    entity_id: str
    summary: str
    payload_json: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserRead
