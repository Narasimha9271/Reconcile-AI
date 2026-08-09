from collections.abc import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from reconcileai.api.identity import DevelopmentActor, get_development_actor
from reconcileai.database import Database


def get_tenant_session(
    request: Request,
    actor: DevelopmentActor = Depends(get_development_actor),
) -> Generator[Session, None, None]:
    database: Database = request.app.state.database
    yield from database.session_for_tenant(actor.organization_id)
