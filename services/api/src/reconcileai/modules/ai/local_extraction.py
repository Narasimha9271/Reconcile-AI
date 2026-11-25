"""Read explicitly labelled fields from text; leave ambiguous identifiers for review."""
import re
from decimal import Decimal


def extract_invoice(text: str) -> dict:
    # A document title is not an ID. Prefer explicit labels anywhere on the page.
    token = r"([A-Z0-9][A-Z0-9./_-]*)"
    number = re.search(
        r"\b(?:invoice[ \t]*(?:number\b|no\b\.?|#)|inv[ \t]*#)[ \t]*[:#-]?[ \t]*" + token,
        text, re.I,
    )
    if not number:
        # Unlabelled "Invoice INV-123" and heading followed by a standalone ID.
        # Require a digit here so headings such as "Invoice date" never qualify.
        number = re.search(
            r"^[ \t]*invoice(?:[ \t]*[:#-][ \t]*|[ \t]+|[ \t]*\r?\n[ \t]*)"
            r"(?=[A-Z0-9./_-]*\d)" + token + r"[ \t]*\r?$", text, re.I | re.M,
        )
    amount = re.search(r"\b(?:total|amount due)\b\s*[:$]?\s*(?:(?:USD|EUR|GBP|INR)\s*)?([0-9,]+(?:\.\d{1,2})?)", text, re.I)
    currency = re.search(r"\b(USD|EUR|GBP|INR)\b", text)
    vendor = re.search(r"(?:vendor|from)\s*:\s*(.+)", text, re.I)
    return {"invoice_number": number.group(1) if number else None, "vendor_name": vendor.group(1).strip() if vendor else None, "total_amount": float(Decimal(amount.group(1).replace(",", ""))) if amount else None, "currency": currency.group(1) if currency else "USD", "provider": "local-structured-extractor", "confidence": 0.55}
