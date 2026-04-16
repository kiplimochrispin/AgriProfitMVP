"""initial schema

Revision ID: 20260416_000001
Revises:
Create Date: 2026-04-16 00:00:01

"""

from alembic import op
import sqlalchemy as sa


revision = "20260416_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("county", sa.String(length=100), nullable=False),
        sa.Column("farm_size_acres", sa.Numeric(10, 2), nullable=True),
        sa.Column("soil_type", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_phone"), "users", ["phone"], unique=True)

    op.create_table(
        "crop_plans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("crop_type", sa.String(length=100), nullable=False),
        sa.Column("acres", sa.Numeric(10, 2), nullable=False),
        sa.Column("planting_date", sa.Date(), nullable=True),
        sa.Column("expected_yield_kg_per_acre", sa.Integer(), nullable=True),
        sa.Column("season_year", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_crop_plans_user_id"), "crop_plans", ["user_id"], unique=False)

    op.create_table(
        "input_usage",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("crop_plan_id", sa.String(length=36), nullable=False),
        sa.Column("item_name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=True),
        sa.Column("unit", sa.String(length=20), nullable=True),
        sa.Column("cost_ksh", sa.Numeric(12, 2), nullable=False),
        sa.Column("acres_applied", sa.Numeric(10, 2), nullable=True),
        sa.Column("application_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["crop_plan_id"], ["crop_plans.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_input_usage_crop_plan_id"), "input_usage", ["crop_plan_id"], unique=False)
    op.create_index(op.f("ix_input_usage_user_id"), "input_usage", ["user_id"], unique=False)

    op.create_table(
        "harvest_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("crop_plan_id", sa.String(length=36), nullable=False),
        sa.Column("actual_yield_kg_total", sa.Numeric(12, 2), nullable=True),
        sa.Column("selling_price_per_kg", sa.Numeric(10, 2), nullable=True),
        sa.Column("other_costs_ksh", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["crop_plan_id"], ["crop_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_harvest_records_crop_plan_id"), "harvest_records", ["crop_plan_id"], unique=True)

    op.create_table(
        "fertilizer_recommendations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("crop_type", sa.String(length=50), nullable=False),
        sa.Column("soil_type", sa.String(length=50), nullable=True),
        sa.Column("county", sa.String(length=100), nullable=False),
        sa.Column("basal_fertilizer", sa.String(length=100), nullable=True),
        sa.Column("basal_kg_per_acre", sa.Numeric(8, 2), nullable=True),
        sa.Column("basal_application_timing", sa.String(length=100), nullable=True),
        sa.Column("top_dress_fertilizer", sa.String(length=100), nullable=True),
        sa.Column("top_dress_kg_per_acre", sa.Numeric(8, 2), nullable=True),
        sa.Column("top_dress_application_timing", sa.String(length=100), nullable=True),
        sa.Column("top_dress_splits", sa.Integer(), nullable=False),
        sa.Column("confidence_level", sa.String(length=20), nullable=False),
        sa.Column("source_reference", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_fertilizer_recommendations_crop_type"),
        "fertilizer_recommendations",
        ["crop_type"],
        unique=False,
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("actor", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("summary", sa.String(length=255), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_audit_logs_actor"), "audit_logs", ["actor"], unique=False)
    op.create_index(op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity_id"), "audit_logs", ["entity_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity_type"), "audit_logs", ["entity_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_entity_type"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_entity_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_created_at"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_actor"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(
        op.f("ix_fertilizer_recommendations_crop_type"),
        table_name="fertilizer_recommendations",
    )
    op.drop_table("fertilizer_recommendations")

    op.drop_index(op.f("ix_harvest_records_crop_plan_id"), table_name="harvest_records")
    op.drop_table("harvest_records")

    op.drop_index(op.f("ix_input_usage_user_id"), table_name="input_usage")
    op.drop_index(op.f("ix_input_usage_crop_plan_id"), table_name="input_usage")
    op.drop_table("input_usage")

    op.drop_index(op.f("ix_crop_plans_user_id"), table_name="crop_plans")
    op.drop_table("crop_plans")

    op.drop_index(op.f("ix_users_phone"), table_name="users")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
