from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from reconcileai.api.database import get_tenant_session
from reconcileai.api.identity import DevelopmentActor, get_development_actor
from reconcileai.modules.procurement.schemas import PurchaseOrderCreate, VendorCreate
from reconcileai.modules.procurement.repository import ProcurementRepository

router = APIRouter(prefix='/v1', tags=['procurement'])
repository = ProcurementRepository()

@router.post('/vendors', status_code=status.HTTP_201_CREATED)
async def create_vendor(payload: VendorCreate, actor: DevelopmentActor = Depends(get_development_actor), session: Session = Depends(get_tenant_session)) -> dict:
    try:
        return repository.create_vendor(session, actor.organization_id, payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

@router.get('/vendors')
async def list_vendors(actor: DevelopmentActor = Depends(get_development_actor), session: Session = Depends(get_tenant_session)) -> list[dict]:
    return repository.list_vendors(session)

@router.post('/purchase-orders', status_code=status.HTTP_201_CREATED)
async def create_purchase_order(payload: PurchaseOrderCreate, actor: DevelopmentActor = Depends(get_development_actor), session: Session = Depends(get_tenant_session)) -> dict:
    try:
        return repository.create_purchase_order(session, actor.organization_id, payload)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

@router.get('/purchase-orders')
async def list_purchase_orders(actor: DevelopmentActor = Depends(get_development_actor), session: Session = Depends(get_tenant_session)) -> list[dict]:
    return repository.list_purchase_orders(session)
