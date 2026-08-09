# Step 5 — PostgreSQL persistence and tenant transactions

## What changed

The vendor, purchase-order, and document metadata endpoints now use PostgreSQL. The database is no longer just schema prepared for a future release: each request opens a short transaction and sets `app.organization_id` using `SET LOCAL`. PostgreSQL row-level security then scopes tenant data even if an application query accidentally omits its organization filter. The Step 5 migration also forces those policies for the database owner, which prevents the usual table-owner RLS bypass. It includes purchase-order lines too, protecting them through their parent purchase order's tenant boundary.

Document bytes still use the existing local storage adapter for development. In cloud deployment, replace this adapter with private S3 storage plus malware scanning; the durable document metadata is already in PostgreSQL.

Docker also loads a local-only demo organization, user, and `ORG_ADMIN` membership for the `X-Development-*` test headers. This seed is deliberately separate from production migrations, so no fake account is deployed to a cloud environment.

## Why this comes before OCR and AI

OCR extraction, confidence scores, reconciliation decisions, and approvals must reference durable source documents and purchase orders. Building them on in-memory dictionaries would lose data on restart and bypass the core multi-tenant boundary.

## Run and verify

From the project root:

```powershell
docker compose down -v
docker compose up --build
```

`down -v` is required once because PostgreSQL only runs the migration files during its first initialization. It deletes the local Docker database volume only; it does not delete project files.

In a second PowerShell window:

```powershell
cd "C:\Users\narasimha\Desktop\Reconcile AI"
$headers = @{
  "X-Development-User-Id" = "018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bc"
  "X-Development-Organization-Id" = "018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bd"
  "X-Development-Role" = "ORG_ADMIN"
}
$vendor = Invoke-RestMethod -Method Post -Uri http://localhost:8000/v1/vendors -Headers $headers -ContentType "application/json" -Body '{"name":"Acme Supplies","external_ref":"ACME-001"}'
$vendor

$body = @{ vendor_id = $vendor.id; number = "PO-1001"; currency = "USD"; lines = @(@{ line_no = 1; description = "Widgets"; quantity = "2"; unit_price = "12.50" }) } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri http://localhost:8000/v1/purchase-orders -Headers $headers -ContentType "application/json" -Body $body
Invoke-RestMethod http://localhost:8000/v1/vendors -Headers $headers
Invoke-RestMethod http://localhost:8000/v1/purchase-orders -Headers $headers
```

Restart the API container with `docker compose restart api`, then run the two GET commands again. The records must remain: this demonstrates they are in PostgreSQL rather than application memory.

## Temporary development boundary

`X-Development-*` headers are still a local testing mechanism. They must be replaced by verified OIDC bearer tokens before any internet-facing deployment.
