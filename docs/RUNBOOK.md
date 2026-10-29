# Local runbook

Run `docker compose up --build` from the project root. Visit `http://localhost:3000`; API health is at `http://localhost:8000/healthz` and API documentation is at `http://localhost:8000/docs`.

## Functional check

1. Add **Acme Supplies**.
2. Create PO `PO-1001`, quantity `2`, unit price `12.50`.
3. Reconcile invoice `INV-1001`, vendor **Acme Supplies**, amount `25.00`. It must be **MATCHED**.
4. Reconcile a `30.00` invoice. It must be **REVIEW REQUIRED**.
5. Approve/reject an item; refresh and verify the decision remains.

## Local extraction check

```powershell
$headers=@{"X-Development-User-Id"="018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bc";"X-Development-Organization-Id"="018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bd"}
Invoke-RestMethod -Method Post -Uri http://localhost:8000/v1/ai/extract-invoice -Headers $headers -ContentType 'application/json' -Body '{"document_text":"Vendor: Acme Supplies\nInvoice # INV-1001\nTotal: 25.00 USD"}'
```

This adapter runs locally and never transmits invoice text externally.

## Inspect records in PostgreSQL

Open the database shell:

```powershell
# Run from the cloned Reconcile-AI repository root.
docker compose exec postgres psql -U reconcileai -d reconcileai
```

Row-level security is enabled, so set the development tenant before reading records:

```sql
BEGIN;

SELECT set_config(
  'app.organization_id',
  '018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bd',
  true
);

SELECT id, name, external_ref, status FROM vendors;

SELECT
  invoice_number,
  invoice_amount,
  vendor_name,
  match_status,
  confidence,
  decision
FROM reconciliation_cases
ORDER BY created_at DESC;
```

If a SQL error occurs, PostgreSQL aborts the active transaction. Run `ROLLBACK;`, then run `BEGIN;` and the tenant `set_config` command again before retrying the query.

Finish with:

```sql
COMMIT;
\q
```
