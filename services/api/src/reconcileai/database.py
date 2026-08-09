from collections.abc import Generator
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from reconcileai.config import get_settings


class Database:
    """Owns the application's database engine and short-lived sessions."""

    def __init__(self, url: str) -> None:
        self.engine = create_engine(url, pool_pre_ping=True)
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)

    def session_for_tenant(self, organization_id: UUID) -> Generator[Session, None, None]:
        session = self.session_factory()
        try:
            # SET LOCAL scopes this setting to the transaction, preventing reuse by the pool.
            session.execute(
                text("SELECT set_config('app.organization_id', :organization_id, true)"),
                {"organization_id": str(organization_id)},
            )
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def create_database() -> Database:
    return Database(get_settings().database_url)
