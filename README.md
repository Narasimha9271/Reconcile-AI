# ReconcileAI

ReconcileAI is an end-to-end invoice, purchase-order, and vendor reconciliation workspace. It includes a Next.js dashboard, FastAPI API, PostgreSQL persistence with tenant row-level security, document intake, OpenAI-powered structured invoice extraction, explainable matching, and finance approval.

## Start locally

```powershell
cd "C:\Users\narasimha\Desktop\Reconcile AI"
docker compose down -v
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000). Create a vendor, PO, and invoice to complete the workflow. `down -v` removes only this project's local Docker database volume; use it after migrations change.

## Enable invoice AI

Copy the variables in [`.env.ai.example`](.env.ai.example) to your local `.env`, add your OpenAI API key, and restart Docker Compose. Then upload a PDF or image in **3. Extract & reconcile invoice**. AI fills candidate invoice fields; you review them, the deterministic reconciler checks the PO, and a Finance Approver makes the final decision.

## Documentation

- [Runbook](docs/RUNBOOK.md)
- [Dashboard walkthrough](docs/DEMO-WALKTHROUGH.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security](docs/SECURITY.md)
- [AI invoice extraction](docs/AI-INVOICE-EXTRACTION.md)
- [Sample data walkthrough](docs/SAMPLE-DATA.md)
- [Duplicate invoice prevention](docs/DUPLICATE-INVOICE-PREVENTION.md)
- API: [http://localhost:8000/docs](http://localhost:8000/docs)
