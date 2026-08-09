from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from reconcileai.modules.procurement.schemas import PurchaseOrderCreate, VendorCreate


def _vendor_response(row: dict) -> dict:
    return {
        "id": str(row["id"]), "organizationId": str(row["organization_id"]),
        "name": row["name"], "externalRef": row["external_ref"], "status": row["status"],
    }


def _is_unique_violation(error: IntegrityError) -> bool:
    return getattr(error.orig, "sqlstate", None) == "23505"


class ProcurementRepository:
    def create_vendor(self, session: Session, organization_id: UUID, payload: VendorCreate) -> dict:
        try:
            row = session.execute(text("""
                INSERT INTO vendors (id, organization_id, name, normalized_name, external_ref)
                VALUES (:id, :organization_id, :name, :normalized_name, :external_ref)
                RETURNING id, organization_id, name, external_ref, status
            """), {"id": uuid4(), "organization_id": organization_id, "name": payload.name,
                    "normalized_name": payload.name.casefold(), "external_ref": payload.external_ref}).mappings().one()
            return _vendor_response(dict(row))
        except IntegrityError as error:
            if _is_unique_violation(error):
                raise ValueError("A vendor with this external reference already exists.") from error
            raise

    def list_vendors(self, session: Session) -> list[dict]:
        rows = session.execute(text("""
            SELECT id, organization_id, name, external_ref, status FROM vendors
            ORDER BY normalized_name, id
        """)).mappings().all()
        return [_vendor_response(dict(row)) for row in rows]

    def create_purchase_order(self, session: Session, organization_id: UUID, payload: PurchaseOrderCreate) -> dict:
        vendor_exists = session.execute(text("SELECT 1 FROM vendors WHERE id = :vendor_id"), {"vendor_id": payload.vendor_id}).scalar()
        if vendor_exists is None:
            raise LookupError("Vendor not found.")
        po_id = uuid4()
        try:
            session.execute(text("""
                INSERT INTO purchase_orders (id, organization_id, vendor_id, number, currency)
                VALUES (:id, :organization_id, :vendor_id, :number, :currency)
            """), {"id": po_id, "organization_id": organization_id, "vendor_id": payload.vendor_id,
                    "number": payload.number, "currency": payload.currency})
            for line in payload.lines:
                session.execute(text("""
                    INSERT INTO purchase_order_lines (id, purchase_order_id, line_no, sku, description, quantity, unit_price)
                    VALUES (:id, :purchase_order_id, :line_no, :sku, :description, :quantity, :unit_price)
                """), {"id": uuid4(), "purchase_order_id": po_id, **line.model_dump()})
        except IntegrityError as error:
            if _is_unique_violation(error):
                raise ValueError("A purchase order with this number already exists.") from error
            raise
        return self.get_purchase_order(session, po_id)

    def get_purchase_order(self, session: Session, po_id: UUID) -> dict:
        row = session.execute(text("""
            SELECT id, organization_id, vendor_id, number, currency, status FROM purchase_orders WHERE id = :id
        """), {"id": po_id}).mappings().one()
        lines = session.execute(text("""
            SELECT line_no, sku, description, quantity, unit_price FROM purchase_order_lines
            WHERE purchase_order_id = :purchase_order_id ORDER BY line_no
        """), {"purchase_order_id": po_id}).mappings().all()
        return {"id": str(row["id"]), "organizationId": str(row["organization_id"]), "vendorId": str(row["vendor_id"]),
                "number": row["number"], "currency": row["currency"], "status": row["status"],
                "lines": [{"line_no": item["line_no"], "sku": item["sku"], "description": item["description"],
                           "quantity": str(item["quantity"]), "unit_price": str(item["unit_price"])} for item in lines]}

    def list_purchase_orders(self, session: Session) -> list[dict]:
        ids = session.execute(text("SELECT id FROM purchase_orders ORDER BY created_at DESC, id")).scalars().all()
        return [self.get_purchase_order(session, po_id) for po_id in ids]
