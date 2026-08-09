from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from reconcileai.api.identity import DevelopmentActor, get_development_actor
from reconcileai.modules.ai.extraction import extract_invoice, extract_uploaded_invoice

router = APIRouter(prefix="/v1/ai", tags=["ai"])

class ExtractionRequest(BaseModel):
    document_text: str = Field(min_length=1, max_length=20_000)

@router.post("/extract-invoice")
def extract_invoice_facts(payload: ExtractionRequest, actor: DevelopmentActor = Depends(get_development_actor)) -> dict:
    return extract_invoice(payload.document_text)


@router.post("/extract-invoice-upload")
async def extract_invoice_upload(
    file: UploadFile = File(...),
    actor: DevelopmentActor = Depends(get_development_actor),
) -> dict:
    try:
        return await extract_uploaded_invoice(await file.read(), file.content_type or "", file.filename)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
