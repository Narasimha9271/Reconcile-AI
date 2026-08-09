# Security posture

Current controls: forced tenant RLS, transaction-scoped tenant context, parameterized SQL, validated requests, constrained uploads, SHA-256 duplicate detection, role-gated approval, and correlation IDs.

Before production: verified OIDC JWTs, least-privilege database roles, a managed secrets vault, S3 malware scanning, WAF/rate limits, immutable audit events, backups, dependency scanning, and data-retention/privacy review. An external AI provider requires explicit security and privacy approval before invoices are sent to it.
