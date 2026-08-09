# Duplicate invoice prevention

ReconcileAI blocks a duplicate before it enters the finance review queue.

## Rule

For one organization, the combination of the selected PO's vendor and normalized invoice number must be unique. Invoice-number comparisons ignore leading/trailing spaces, repeated internal spaces, and letter case.

Examples treated as the same invoice:

- `INV-NW-1001`
- `inv-nw-1001`
- `  INV-NW-1001  `

The first submission creates a reconciliation case. A repeat submission returns HTTP `409 Conflict` with a clear message and cannot be approved.

## Defense in depth

1. The API checks before creating a case, which gives the user an understandable error.
2. PostgreSQL has a unique index, which prevents concurrent requests or future services from bypassing the rule.

## Local migration

For a fresh Docker database, `007_duplicate_invoice_prevention.sql` runs automatically. For an existing local database, run:

```powershell
cd "C:\Users\narasimha\Desktop\Reconcile AI"
docker compose exec -T postgres psql -U reconcileai -d reconcileai -f /docker-entrypoint-initdb.d/007_duplicate_invoice_prevention.sql
```

If historical duplicates already exist, the migration preserves them. It marks every later duplicate as linked to the oldest original, blocks its approval, and creates the unique index for all future invoices. No reconciliation case is deleted.
