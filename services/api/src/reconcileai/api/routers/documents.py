from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session
from reconcileai.api.database import get_tenant_session
from reconcileai.api.identity import DevelopmentActor, get_development_actor
from reconcileai.modules.documents.service import LocalDocumentStore
from reconcileai.modules.documents.repository import DocumentRepository

router = APIRouter(prefix="/v1/documents", tags=["documents"])
repository = DocumentRepository()

def store(request: Request) -> LocalDocumentStore:
    return request.app.state.document_store

@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    document_type: str = Form(..., pattern="^(INVOICE|PURCHASE_ORDER|RECEIPT|QUOTE)$"),
    file: UploadFile = File(...),
    actor: DevelopmentActor = Depends(get_development_actor),
    session: Session = Depends(get_tenant_session),
) -> dict:
    document = await store(request).save(actor.organization_id, document_type, file)
    try:
        repository.create(session, document)
    except ValueError as error:
        path = store(request).root / document.storage_key
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=409, detail=str(error)) from error
    return document.__dict__

@router.get("")
async def list_documents(request: Request, actor: DevelopmentActor = Depends(get_development_actor), session: Session = Depends(get_tenant_session)) -> list[dict]:
    return [document.__dict__ for document in repository.list_for_tenant(session)]
