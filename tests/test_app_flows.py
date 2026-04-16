import importlib
import os
import tempfile
import unittest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class AppFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = os.path.join(self.temp_dir.name, "test.db")
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
        os.environ["ADMIN_USERNAME"] = "admin"
        os.environ["ADMIN_PASSWORD"] = "admin123"
        os.environ["ADMIN_PHONE"] = "+254700000000"

        import app.crud as crud_module
        import app.database as database_module
        import app.main as main_module
        import app.models as models_module
        import app.routers.analytics as analytics_module
        import app.schemas as schemas_module
        import app.security as security_module

        database_module = importlib.reload(database_module)
        models_module = importlib.reload(models_module)
        schemas_module = importlib.reload(schemas_module)
        crud_module = importlib.reload(crud_module)
        analytics_module = importlib.reload(analytics_module)
        security_module = importlib.reload(security_module)
        main_module = importlib.reload(main_module)

        self.models = models_module
        self.schemas = schemas_module
        self.Base = database_module.Base
        self.engine = create_engine(
            os.environ["DATABASE_URL"],
            connect_args={"check_same_thread": False},
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.seed_recommendations = database_module.SEED_RECOMMENDATIONS
        self.database_backend = database_module.database_backend
        self.using_default_sqlite = database_module.using_default_sqlite
        self.app_status = main_module.app_status
        self.live_health = main_module.live_health
        self.ready_health = main_module.ready_health
        self.build_dashboard_for_user = analytics_module.build_dashboard_for_user
        self.build_overview = analytics_module.build_overview
        self.get_profit_loss = analytics_module.get_profit_loss
        self.authenticate_user = security_module.authenticate_user
        self.create_access_token = security_module.create_access_token
        self.hash_password = security_module.hash_password
        self.crud = crud_module

        self.Base.metadata.create_all(bind=self.engine)
        self.db = self.SessionLocal()
        self.db.add(
            self.models.User(
                username="admin",
                phone=os.environ["ADMIN_PHONE"],
                password_hash=self.hash_password("admin123"),
                full_name="System Admin",
                role="admin",
                county="Uasin Gishu",
                is_active=True,
            )
        )
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
                username="farmer1",
                phone="+254700000001",
                password="testpass123",
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

        overview = self.build_overview(self.db)
        self.assertEqual(overview["database"]["backend"], "sqlite")
        self.assertEqual(overview["counts"]["users"], 2)
        self.assertEqual(overview["counts"]["crop_plans"], 1)
        self.assertEqual(overview["counts"]["inputs"], 1)
        self.assertEqual(overview["counts"]["harvests"], 1)
        self.assertEqual(overview["latest"]["user_name"], "Test Farmer")
        self.assertEqual(overview["latest"]["crop_type"], "maize")
        self.assertGreaterEqual(len(overview["recent_activity"]), 4)

        audit_logs = self.crud.get_audit_logs(self.db)
        self.assertEqual(len(audit_logs), 4)
        self.assertEqual(audit_logs[0].action, "create")
        self.assertEqual(audit_logs[0].actor, "system")

    def test_auth_helpers(self):
        admin = self.authenticate_user(self.db, "admin", "admin123")
        self.assertIsNotNone(admin)
        self.assertIsNone(self.authenticate_user(self.db, "admin", "wrong"))
        token = self.create_access_token(admin)
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 20)

    def test_database_mode_helpers(self):
        self.assertEqual(self.database_backend(), "sqlite")
        self.assertFalse(self.using_default_sqlite())

    def test_health_and_status_endpoints(self):
        live = self.live_health()
        self.assertEqual(live["status"], "ok")

        ready = self.ready_health()
        self.assertEqual(ready.status_code, 200)
        ready_payload = json.loads(ready.body.decode("utf-8"))
        self.assertEqual(ready_payload["database"]["ready"], True)
        self.assertEqual(ready_payload["database"]["backend"], "sqlite")

        status = self.app_status()
        self.assertEqual(status["health"]["live"], "/health/live")


if __name__ == "__main__":
    unittest.main()
