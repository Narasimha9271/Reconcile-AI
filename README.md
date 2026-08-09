# ReconcileAI

ReconcileAI is an end-to-end invoice, purchase-order, and vendor reconciliation workspace. It includes a Next.js dashboard, FastAPI API, PostgreSQL persistence with tenant row-level security, document intake, explainable matching, and finance approval.

## Start locally

```powershell
cd "C:\Users\narasimha\Desktop\Reconcile AI"
docker compose down -v
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000). Create a vendor, PO, and invoice to complete the workflow. `down -v` removes only this project's local Docker database volume; use it after migrations change.

## Documentation

- [Runbook](docs/RUNBOOK.md)
- [Dashboard walkthrough](docs/DEMO-WALKTHROUGH.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security](docs/SECURITY.md)
- API: [http://localhost:8000/docs](http://localhost:8000/docs)
