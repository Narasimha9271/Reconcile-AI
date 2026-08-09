# Sample data walkthrough

The full set of values is in [`samples/demo-data.json`](../samples/demo-data.json). Start with the exact-match case; it is also available as `samples/INV-NW-1001.pdf` for testing AI extraction.

## Exact-match walkthrough

1. Sign in to `http://localhost:3000`.
2. Create vendor:
   - Vendor name: `Northwind Office Supplies`
   - External reference: `NW-001`
3. Create purchase order:
   - Vendor: `Northwind Office Supplies`
   - PO number: `PO-2026-1001`
   - Line description: `Ergonomic office chairs`
   - Quantity: `5`
   - Unit price: `120.00`
4. In **3. Extract & reconcile invoice**, choose `samples/INV-NW-1001.pdf` and click **Extract with AI**.
5. Confirm these candidate values before submitting:
   - Invoice number: `INV-NW-1001`
   - Vendor: `Northwind Office Supplies`
   - Amount: `600.00`
   - Currency: `USD`
6. Select `PO-2026-1001` and click **Review & run reconciliation**.

Expected result: **MATCHED** at **100% confidence**, with an explanation that vendor, currency, and total agree.

## Exception tests

Use the two remaining entries in `demo-data.json` to demonstrate the human-in-the-loop workflow:

- `INV-CL-1002`: amount differs by 75.00 from its PO.
- `INV-FIT-1003`: vendor name differs from its PO.

Both should require review. Sign in with an email configured in `GOOGLE_FINANCE_APPROVER_EMAILS` to use **Approve** or **Reject**.
