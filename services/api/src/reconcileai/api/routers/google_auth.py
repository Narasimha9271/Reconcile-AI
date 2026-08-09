import secrets
from urllib.parse import urlencode
from uuid import NAMESPACE_URL, UUID, uuid5

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import text

from reconcileai.config import get_settings

router = APIRouter(prefix="/api/auth/google", tags=["authentication"])
DEMO_ORGANIZATION_ID = UUID("018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bd")


def configured() -> None:
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret or not settings.google_allowed_email:
        raise HTTPException(status_code=503, detail="Google OAuth is not configured. Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_ALLOWED_EMAIL in .env.")


@router.get("/login")
async def login(request: Request) -> RedirectResponse:
    configured()
    settings = get_settings()
    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state
    query = urlencode({"client_id": settings.google_client_id, "redirect_uri": settings.google_callback_url, "response_type": "code", "scope": "openid email profile", "state": state, "prompt": "select_account"})
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{query}", status_code=302)


@router.get("/callback")
async def callback(request: Request, code: str | None = None, state: str | None = None) -> RedirectResponse:
    configured()
    settings = get_settings()
    if not code or not state or not secrets.compare_digest(state, request.session.pop("google_oauth_state", "")):
        raise HTTPException(status_code=400, detail="Invalid Google OAuth state.")
    async with httpx.AsyncClient(timeout=15) as client:
        token = await client.post("https://oauth2.googleapis.com/token", data={"code": code, "client_id": settings.google_client_id, "client_secret": settings.google_client_secret, "redirect_uri": settings.google_callback_url, "grant_type": "authorization_code"})
        token.raise_for_status()
        profile = await client.get("https://openidconnect.googleapis.com/v1/userinfo", headers={"Authorization": f"Bearer {token.json()['access_token']}"})
        profile.raise_for_status()
    identity = profile.json(); email = identity.get("email", "").casefold()
    allowed_emails = {item.strip().casefold() for item in settings.google_allowed_email.split(",") if item.strip()}
    if not identity.get("email_verified") or email not in allowed_emails:
        raise HTTPException(status_code=403, detail="This Google account is not approved for the local workspace.")
    approver_emails = {item.strip().casefold() for item in (settings.google_finance_approver_emails or "").split(",") if item.strip()}
    role = "FINANCE_APPROVER" if email in approver_emails else "AP_ANALYST"
    user_id = uuid5(NAMESPACE_URL, f"google:{identity['sub']}")
    session = request.app.state.database.session_factory()
    try:
        session.execute(text("SELECT set_config('app.organization_id', :org, true)"), {"org": str(DEMO_ORGANIZATION_ID)})
        session.execute(text("INSERT INTO users (id, idp_subject, email) VALUES (:id, :subject, :email) ON CONFLICT (idp_subject) DO UPDATE SET email = EXCLUDED.email"), {"id": user_id, "subject": f"google:{identity['sub']}", "email": email})
        session.execute(text("INSERT INTO memberships (organization_id, user_id, role) VALUES (:org, :user, :role) ON CONFLICT (organization_id, user_id) DO UPDATE SET role = EXCLUDED.role"), {"org": DEMO_ORGANIZATION_ID, "user": user_id, "role": role})
        session.commit()
    except Exception:
        session.rollback(); raise
    finally:
        session.close()
    request.session["actor"] = {"user_id": str(user_id), "organization_id": str(DEMO_ORGANIZATION_ID), "role": role, "email": email, "name": identity.get("name") or email}
    return RedirectResponse("http://localhost:3000/?signedIn=google", status_code=302)


@router.post("/logout")
async def logout(request: Request) -> dict[str, bool]:
    request.session.clear()
    return {"signedOut": True}
