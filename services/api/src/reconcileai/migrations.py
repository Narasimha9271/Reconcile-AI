"""Small migration runner for the production managed PostgreSQL deployment."""

from pathlib import Path

from sqlalchemy import create_engine, text


def apply_migrations(database_url: str) -> None:
    """Apply each SQL migration once, serializing concurrent API starts."""
    migrations_dir = Path(__file__).resolve().parents[2] / "migrations"
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            connection.execute(text("SELECT pg_advisory_xact_lock(73459201)"))
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                  filename text PRIMARY KEY,
                  applied_at timestamptz NOT NULL DEFAULT now()
                )
            """))
            applied = set(connection.execute(text("SELECT filename FROM schema_migrations")).scalars())
            raw_connection = connection.connection.driver_connection
            for migration in sorted(migrations_dir.glob("*.sql")):
                if migration.name in applied:
                    continue
                with raw_connection.cursor() as cursor:
                    cursor.execute(migration.read_text(encoding="utf-8"))
                connection.execute(text("INSERT INTO schema_migrations (filename) VALUES (:filename)"), {"filename": migration.name})
    finally:
        engine.dispose()
