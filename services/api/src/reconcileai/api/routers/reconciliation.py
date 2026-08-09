from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from reconcileai.api.database import get_tenant_session
from reconcileai.api.identity import DevelopmentActor,get_development_actor
from reconcileai.modules.reconciliation.repository import DuplicateInvoiceError,ReconciliationRepository
from reconcileai.modules.reconciliation.schemas import ReconciliationCreate,ReviewDecision
router=APIRouter(prefix="/v1/reconciliations",tags=["reconciliation"]); repository=ReconciliationRepository()
@router.post("",status_code=status.HTTP_201_CREATED)
def create_case(payload:ReconciliationCreate,actor:DevelopmentActor=Depends(get_development_actor),session:Session=Depends(get_tenant_session))->dict:
    try:return repository.create(session,actor.organization_id,payload)
    except DuplicateInvoiceError as error:raise HTTPException(status_code=409,detail=str(error)) from error
    except LookupError as error:raise HTTPException(status_code=404,detail=str(error)) from error
@router.get("")
def list_cases(actor:DevelopmentActor=Depends(get_development_actor),session:Session=Depends(get_tenant_session))->list[dict]: return repository.list(session) if actor.role in {"ORG_ADMIN","FINANCE_APPROVER"} else []
@router.post("/{case_id}/decision")
def review_case(case_id:UUID,payload:ReviewDecision,actor:DevelopmentActor=Depends(get_development_actor),session:Session=Depends(get_tenant_session))->dict:
    if actor.role not in {"ORG_ADMIN","FINANCE_APPROVER"}:raise HTTPException(status_code=403,detail="Finance approval role required.")
    try:return repository.decide(session,case_id,actor.user_id,payload.decision)
    except DuplicateInvoiceError as error:raise HTTPException(status_code=409,detail=str(error)) from error
    except LookupError as error:raise HTTPException(status_code=404,detail=str(error)) from error
