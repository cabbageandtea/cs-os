"""Lightweight SQLite migrations for MVP schema updates."""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.database import Base


CLIENT_REVENUE_COLUMNS: dict[str, str] = {
    "email": "VARCHAR(320)",
    "public_id": "VARCHAR(36)",
    "package_slug": "VARCHAR(50)",
    "customer_lifecycle": "VARCHAR(50)",
    "intake_status": "VARCHAR(50)",
    "intake_token_hash": "VARCHAR(128)",
    "intake_token_expires_at": "DATETIME",
    "paid_at": "DATETIME",
    "purchase_id": "INTEGER",
    "intake_completed_at": "DATETIME",
}


def run_migrations(engine: Engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    if "tasks" in table_names:
        columns = {col["name"] for col in inspector.get_columns("tasks")}
        if "stage_name" not in columns:
            with engine.begin() as conn:
                conn.execute(
                    text("ALTER TABLE tasks ADD COLUMN stage_name VARCHAR(50) DEFAULT 'Intake'")
                )
            _backfill_task_stages(engine)

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    if "clients" in table_names:
        columns = {col["name"] for col in inspector.get_columns("clients")}
        with engine.begin() as conn:
            for name, col_type in CLIENT_REVENUE_COLUMNS.items():
                if name not in columns:
                    conn.execute(text(f"ALTER TABLE clients ADD COLUMN {name} {col_type}"))
        _backfill_manual_clients(engine)


def _backfill_task_stages(engine: Engine) -> None:
    """Map legacy tasks to stages by title."""
    title_to_stage = {
        "Review intake data": "Intake",
        "Audit LinkedIn profile": "Analysis",
        "Audit GitHub profile": "Analysis",
        "Select portfolio template": "Analysis",
        "Build portfolio site": "Build",
        "Resume rewrite": "Build",
        "QA checklist": "QA",
        "Client review + revisions": "Review",
        "Deploy + handoff": "Delivered",
    }
    with engine.begin() as conn:
        for title, stage in title_to_stage.items():
            conn.execute(
                text("UPDATE tasks SET stage_name = :stage WHERE title = :title"),
                {"stage": stage, "title": title},
            )
        conn.execute(
            text(
                "UPDATE tasks SET stage_name = 'Intake' "
                "WHERE stage_name IS NULL OR stage_name = ''"
            )
        )


def _backfill_manual_clients(engine: Engine) -> None:
    """Existing manual clients are active with completed intake."""
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE clients
                SET customer_lifecycle = 'active',
                    intake_status = 'complete'
                WHERE customer_lifecycle IS NULL
                  AND purchase_id IS NULL
                  AND name NOT LIKE '[DEMO]%'
                """
            )
        )
        conn.execute(
            text(
                """
                UPDATE clients
                SET package_slug = CASE package_tier
                    WHEN 'Basic' THEN 'foundation'
                    WHEN 'Standard' THEN 'launch'
                    WHEN 'Premium' THEN 'accelerator'
                    ELSE NULL
                END
                WHERE package_slug IS NULL
                  AND purchase_id IS NULL
                """
            )
        )
