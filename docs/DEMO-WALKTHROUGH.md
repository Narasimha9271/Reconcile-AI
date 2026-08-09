# Dashboard walkthrough

## Start

```powershell
cd "C:\Users\narasimha\Desktop\Reconcile AI"
docker compose up --build
```

Open `http://localhost:3000`. If the page was open during an API restart, press `Ctrl + Shift + R` once.

## Exact demo input

### 1. Create vendor

In **Create vendor** enter:

- Vendor name: `Acme Supplies`
- External reference: `ACME-001`

Click **Add vendor**. A blue `Acme Supplies` chip appears below the form.

### 2. Create purchase order

In **Create purchase order** enter:

- Select vendor: `Acme Supplies`
- PO number: `PO-1001`
- Line description: `Widgets`
- Quantity: `2`
- Unit price: `12.50`

Click **Create PO**. The PO becomes available in the reconciliation dropdown.

### 3. Test a correct invoice

In **Reconcile invoice** enter:

- Select purchase order: `PO-1001`
- Invoice number: `INV-1001`
- Invoice vendor name: `Acme Supplies`
- Invoice amount: `25.00`

Click **Run reconciliation**.

Correct result: a green **MATCHED** badge, `99%` confidence, and an explanation that vendor, currency, and total agree.

### 4. Test an exception

Submit another invoice with:

- Invoice number: `INV-1002`
- Invoice vendor name: `Acme Supplies`
- Invoice amount: `30.00`

Correct result: yellow **REVIEW REQUIRED** with an amount-difference explanation.

### 5. Test approval persistence

Click **Approve** or **Reject** on one queue item, then click **Refresh data**. The decision remains visible because it was saved in PostgreSQL.

## If you see a CORS error

Run `docker compose restart api`, wait five seconds, then use `Ctrl + Shift + R` on the dashboard. The API allows browser calls from `http://localhost:3000` only in this local development setup.
