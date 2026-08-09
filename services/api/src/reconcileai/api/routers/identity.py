from fastapi import APIRouter, Depends, Request

from reconcileai.api.identity import DevelopmentActor, get_development_actor

router = APIRouter(prefix="/v1", tags=["identity"])


@router.get("/me")
async def get_me(request: Request, actor: DevelopmentActor = Depends(get_development_actor)) -> dict[str, str | None]:
    profile = request.session.get("actor", {})
    return {"userId": str(actor.user_id), "organizationId": str(actor.organization_id), "role": actor.role, "email": profile.get("email"), "name": profile.get("name")}
