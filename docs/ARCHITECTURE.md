# Architecture

```text
Next.js dashboard → FastAPI API → PostgreSQL with tenant RLS
                       └────────→ local document adapter (development)
```

The API separates identity, procurement, documents, reconciliation, and structured extraction. A request transaction sets `app.organization_id`; PostgreSQL row-level security enforces the tenant boundary. Matching is deterministic and explainable; any future AI may extract candidate fields, but it must never approve an invoice.

For production, replace development headers with OIDC JWT verification, local storage with S3 and malware scanning, and inline work with idempotent queue workers. Deploy replicas behind ALB/WAF with managed PostgreSQL, secrets, backups, tracing, and alerting.
