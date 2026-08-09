from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from reconcileai.modules.reconciliation.schemas import ReconciliationCreate


def serialize(row: dict) -> dict:
    return {"id": str(row["id"]), "purchaseOrderId": str(row["purchase_order_id"]), "invoiceNumber": row["invoice_number"], "invoiceAmount": str(row["invoice_amount"]), "currency": row["currency"], "vendorName": row["vendor_name"], "matchStatus": row["match_status"], "confidence": float(row["confidence"]), "explanation": row["explanation"], "decision": row["decision"], "createdAt": row["created_at"].isoformat()}


def normalize_name(value: str) -> str:
    return " ".join(value.split()).casefold()


class DuplicateInvoiceError(ValueError):
    """Raised when this vendor's invoice was already submitted in the tenant."""


class ReconciliationRepository:
    def create(self, session: Session, organization_id: UUID, payload: ReconciliationCreate) -> dict:
        po = session.execute(text("SELECT p.number, p.currency, p.vendor_id, v.name AS vendor_name, COALESCE(SUM(l.quantity * l.unit_price), 0) AS total FROM purchase_orders p JOIN vendors v ON v.id = p.vendor_id LEFT JOIN purchase_order_lines l ON l.purchase_order_id = p.id WHERE p.id = :id GROUP BY p.id, p.number, p.currency, p.vendor_id, v.name"), {"id": payload.purchase_order_id}).mappings().one_or_none()
        if po is None:
            raise LookupError("Purchase order not found.")

        duplicate = session.execute(text("""
            SELECT 1 FROM reconciliation_cases
            WHERE organization_id = :organization_id
              AND vendor_id = :vendor_id
              AND lower(regexp_replace(btrim(invoice_number), '\\s+', ' ', 'g'))
                  = lower(regexp_replace(btrim(:invoice_number), '\\s+', ' ', 'g'))
            LIMIT 1
        """), {"organization_id": organization_id, "vendor_id": po["vendor_id"], "invoice_number": payload.invoice_number}).scalar()
        if duplicate:
            raise DuplicateInvoiceError(f"Duplicate invoice: {payload.invoice_number} was already submitted for vendor {po['vendor_name']}.")

        delta = abs(Decimal(po["total"]) - payload.invoice_amount)
        vendor_match = normalize_name(po["vendor_name"]) == normalize_name(payload.vendor_name)
        currency_match = po["currency"] == payload.currency
        amount_match = delta <= Decimal("0.01")
        mismatches: list[str] = []
        if not vendor_match:
            mismatches.append(f"vendor differs (PO: {po['vendor_name']}; invoice: {payload.vendor_name})")
        if not currency_match:
            mismatches.append(f"currency differs (PO: {po['currency']}; invoice: {payload.currency})")
        if not amount_match:
            mismatches.append(f"amount differs by {delta:.2f}")

        if not mismatches:
            status, confidence, why = "MATCHED", Decimal("1.0000"), "vendor, currency, and total agree"
        elif len(mismatches) == 1:
            status, confidence, why = "REVIEW_REQUIRED", Decimal("0.8200"), mismatches[0]
        else:
            status, confidence, why = "EXCEPTION", Decimal("0.4500"), "; ".join(mismatches)

        try:
            with session.begin_nested():
                row = session.execute(text("INSERT INTO reconciliation_cases (id, organization_id, purchase_order_id, vendor_id, invoice_number, invoice_amount, currency, vendor_name, match_status, confidence, explanation) VALUES (:id, :organization_id, :purchase_order_id, :vendor_id, :invoice_number, :invoice_amount, :currency, :vendor_name, :match_status, :confidence, :explanation) RETURNING id, purchase_order_id, invoice_number, invoice_amount, currency, vendor_name, match_status, confidence, explanation, decision, created_at"), {"id": uuid4(), "organization_id": organization_id, "vendor_id": po["vendor_id"], **payload.model_dump(), "match_status": status, "confidence": confidence, "explanation": f"Invoice {payload.invoice_number} against {po['number']}: {why}."}).mappings().one()
        except IntegrityError as error:
            raise DuplicateInvoiceError(f"Duplicate invoice: {payload.invoice_number} was already submitted for vendor {po['vendor_name']}.") from error
        return serialize(dict(row))

    def list(self, session: Session) -> list[dict]:
        rows = session.execute(text("SELECT id, purchase_order_id, invoice_number, invoice_amount, currency, vendor_name, match_status, confidence, explanation, decision, created_at FROM reconciliation_cases ORDER BY created_at DESC, id")).mappings().all()
        return [serialize(dict(row)) for row in rows]

    def decide(self, session: Session, case_id: UUID, user_id: UUID, decision: str) -> dict:
        row = session.execute(text("UPDATE reconciliation_cases SET decision = :decision, reviewed_by = :user_id, reviewed_at = now() WHERE id = :id AND decision IS NULL AND duplicate_of IS NULL RETURNING id, purchase_order_id, invoice_number, invoice_amount, currency, vendor_name, match_status, confidence, explanation, decision, created_at"), {"id": case_id, "user_id": user_id, "decision": decision}).mappings().one_or_none()
        if row is None:
            duplicate_of = session.execute(text("SELECT duplicate_of FROM reconciliation_cases WHERE id = :id"), {"id": case_id}).scalar_one_or_none()
            if duplicate_of is not None:
                raise DuplicateInvoiceError("This duplicate invoice cannot be approved or rejected. Review the original invoice instead.")
            raise LookupError("Case not found or already reviewed.")
        return serialize(dict(row))
