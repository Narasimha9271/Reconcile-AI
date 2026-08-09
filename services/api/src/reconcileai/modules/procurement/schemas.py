from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

class VendorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    external_ref: str | None = Field(default=None, max_length=100)

    @field_validator('name')
    @classmethod
    def trim_name(cls, value: str) -> str:
        value = ' '.join(value.split())
        if not value: raise ValueError('name cannot be blank')
        return value

class POLineCreate(BaseModel):
    line_no: int = Field(gt=0)
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(gt=0, max_digits=19, decimal_places=4)
    unit_price: Decimal = Field(ge=0, max_digits=19, decimal_places=4)
    sku: str | None = Field(default=None, max_length=100)

class PurchaseOrderCreate(BaseModel):
    vendor_id: UUID
    number: str = Field(min_length=1, max_length=100)
    currency: str = Field(pattern='^[A-Z]{3}$')
    lines: list[POLineCreate] = Field(min_length=1, max_length=500)

    @field_validator('lines')
    @classmethod
    def unique_line_numbers(cls, lines: list[POLineCreate]) -> list[POLineCreate]:
        if len({line.line_no for line in lines}) != len(lines): raise ValueError('line_no values must be unique')
        return lines
