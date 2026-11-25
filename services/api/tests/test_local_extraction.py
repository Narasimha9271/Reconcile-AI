import unittest

from reconcileai.modules.ai.local_extraction import extract_invoice


class TestInvoiceFallback(unittest.TestCase):
    def test_same_po_distinct_invoices(self):
        for number, total in (("INV-CL-0501", "1,000.00"), ("INV-CL-0502", "1,250.00")):
            text = f"Invoice\nInvoice number: {number}\nVendor: Colgate\nPurchase order: PO-501\nInvoice total\nINR {total}"
            result = extract_invoice(text)
            self.assertEqual(result["invoice_number"], number)
            self.assertEqual(result["total_amount"], float(total.replace(",", "")))
            self.assertEqual(result["currency"], "INR")

    def test_missing_number_is_not_a_heading_or_po(self):
        self.assertIsNone(extract_invoice("Invoice\nInvoice date: 2026-11-25\nPurchase order: PO-501")["invoice_number"])

    def test_common_number_formats(self):
        for text in ("Invoice #: INV-42", "Invoice No. INV-42", "INV# INV-42", "Invoice\nINV-42"):
            self.assertEqual(extract_invoice(text)["invoice_number"], "INV-42")
