from decimal import Decimal


def evaluate_match(*, po_number: str, po_currency: str, po_vendor: str, po_total: Decimal, invoice_number: str, invoice_amount: Decimal, invoice_currency: str, invoice_vendor: str) -> tuple[str, Decimal, str]:
    """Deterministic, explainable baseline. Optional LLM extraction feeds this decision, never replaces it."""
    currency_match = po_currency == invoice_currency
    vendor_match = po_vendor.casefold() == invoice_vendor.casefold()
    amount_delta = abs(po_total - invoice_amount)
    amount_match = amount_delta <= Decimal("0.01")
    if currency_match and vendor_match and amount_match:
        return "MATCHED", Decimal("0.9900"), f"Invoice {invoice_number} matches {po_number}: vendor, currency, and total agree."
    mismatches = []
    if not vendor_match:
        mismatches.append("vendor")
    if not currency_match:
        mismatches.append("currency")
    if not amount_match:
        mismatches.append(f"amount differs by {amount_delta}")
    score = Decimal("0.8200") if len(mismatches) == 1 else Decimal("0.4500")
    status = "REVIEW_REQUIRED" if len(mismatches) == 1 else "EXCEPTION"
    return status, score, f"Invoice {invoice_number} needs review against {po_number}: {', '.join(mismatches)}."
