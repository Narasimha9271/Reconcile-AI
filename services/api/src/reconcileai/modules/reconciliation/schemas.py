from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field
class ReconciliationCreate(BaseModel):
    purchase_order_id: UUID
    invoice_number: str = Field(min_length=1, max_length=100)
    invoice_amount: Decimal = Field(ge=0, max_digits=19, decimal_places=4)
    currency: str = Field(pattern="^[A-Z]{3}$")
    vendor_name: str = Field(min_length=1, max_length=200)
class ReviewDecision(BaseModel):
    decision: str = Field(pattern="^(APPROVED|REJECTED)$")
