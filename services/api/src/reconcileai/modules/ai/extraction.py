import re
from decimal import Decimal


def extract_invoice(text: str) -> dict:
    """Local safe extraction adapter; external providers require privacy approval."""
    number = re.search(r"(?:invoice\s*(?:number|#)?|inv#)\s*[:#-]?\s*([A-Za-z0-9-]+)", text, re.I)
    amount = re.search(r"(?:total|amount due)\s*[:$]?\s*([0-9,]+(?:\.\d{1,2})?)", text, re.I)
    currency = re.search(r"\b(USD|EUR|GBP|INR)\b", text)
    vendor = re.search(r"(?:vendor|from)\s*:\s*(.+)", text, re.I)
    return {"invoice_number": number.group(1) if number else None, "vendor_name": vendor.group(1).strip() if vendor else None, "total_amount": float(Decimal(amount.group(1).replace(",", ""))) if amount else None, "currency": currency.group(1) if currency else "USD", "provider": "local-structured-extractor", "confidence": 0.55}
