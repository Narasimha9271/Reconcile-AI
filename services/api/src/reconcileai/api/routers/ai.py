from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from reconcileai.api.identity import DevelopmentActor, get_development_actor
from reconcileai.modules.ai.extraction import extract_invoice

router = APIRouter(prefix="/v1/ai", tags=["ai"])

class ExtractionRequest(BaseModel):
    document_text: str = Field(min_length=1, max_length=20_000)

@router.post("/extract-invoice")
def extract_invoice_facts(payload: ExtractionRequest, actor: DevelopmentActor = Depends(get_development_actor)) -> dict:
    return extract_invoice(payload.document_text)
