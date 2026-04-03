import os
import tempfile
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class AppFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = os.path.join(self.temp_dir.name, "test.db")
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        os.environ["ADMIN_USERNAME"] = "admin"
        os.environ["ADMIN_PASSWORD"] = "admin123"

        from app import models, schemas
        from app.database import Base, SEED_RECOMMENDATIONS
        from app.routers.analytics import build_dashboard_for_user, get_profit_loss
        from app.security import authenticate_admin, create_access_token
        from app import crud

        self.models = models
        self.schemas = schemas
        self.Base = Base
        self.engine = create_engine(
            os.environ["DATABASE_URL"],
            connect_args={"check_same_thread": False},
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.seed_recommendations = SEED_RECOMMENDATIONS
        self.build_dashboard_for_user = build_dashboard_for_user
        self.get_profit_loss = get_profit_loss
        self.authenticate_admin = authenticate_admin
        self.create_access_token = create_access_token
        self.crud = crud

        self.Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()
        self.db.add_all(self.models.FertilizerRecommendation(**item) for item in self.seed_recommendations)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
        self.temp_dir.cleanup()
        os.environ.pop("DATABASE_URL", None)

    def test_create_records_and_compute_dashboard(self):
        user = self.crud.create_user(
            self.db,
            self.schemas.UserCreate(
                phone="+254700000001",
                full_name="Test Farmer",
                county="Uasin Gishu",
                soil_type="loam",
            ),
        )
        crop_plan = self.crud.create_crop_plan(
            self.db,
            self.schemas.CropPlanCreate(
                user_id=user.id,
                crop_type="maize",
                acres=2,
                season_year=2026,
                expected_yield_kg_per_acre=1800,
            ),
        )
        self.crud.create_input_usage(
            self.db,
            self.schemas.InputUsageCreate(
                user_id=user.id,
                crop_plan_id=crop_plan.id,
                item_name="DAP",
                category="fertilizer",
                quantity=130,
                unit="kg",
                cost_ksh=9500,
                acres_applied=2,
            ),
        )
        self.crud.create_harvest_record(
            self.db,
            self.schemas.HarvestRecordCreate(
                crop_plan_id=crop_plan.id,
                actual_yield_kg_total=3200,
                selling_price_per_kg=35,
                other_costs_ksh=4000,
            ),
        )

        dashboard = self.build_dashboard_for_user(self.db, user)
        self.assertEqual(dashboard["total_revenue_ksh"], 112000.0)
        self.assertEqual(dashboard["total_cost_ksh"], 13500.0)
        self.assertEqual(dashboard["profit_loss_ksh"], 98500.0)
        self.assertEqual(dashboard["crop_type"], "maize")

        profit_loss = self.get_profit_loss(crop_plan.id, self.db)
        self.assertEqual(profit_loss["profit_loss_ksh"], 98500.0)

    def test_auth_helpers(self):
        self.assertTrue(self.authenticate_admin("admin", "admin123"))
        self.assertFalse(self.authenticate_admin("admin", "wrong"))
        token = self.create_access_token("admin")
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 20)


if __name__ == "__main__":
    unittest.main()
