from dataclasses import dataclass
from uuid import UUID

from fastapi import Header, HTTPException, Request, status


@dataclass(frozen=True)
class DevelopmentActor:
    """Development-only actor substitute until an OIDC provider is integrated."""
    user_id: UUID
    organization_id: UUID
    role: str


def get_development_actor(
    request: Request,
    x_development_user_id: UUID | None = Header(default=None),
    x_development_organization_id: UUID | None = Header(default=None),
    x_development_role: str = Header(default="AP_ANALYST"),
) -> DevelopmentActor:
    if x_development_user_id is not None and x_development_organization_id is not None:
        return DevelopmentActor(x_development_user_id, x_development_organization_id, x_development_role)
    actor = request.session.get("actor")
    if actor:
        return DevelopmentActor(UUID(actor["user_id"]), UUID(actor["organization_id"]), actor["role"])
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in with Google or supply development identity headers.")
