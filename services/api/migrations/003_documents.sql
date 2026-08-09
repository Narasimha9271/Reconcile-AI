CREATE TABLE documents (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
  document_type text NOT NULL CHECK (document_type IN ('INVOICE', 'PURCHASE_ORDER', 'RECEIPT', 'QUOTE')),
  original_filename text NOT NULL,
  content_type text NOT NULL,
  byte_size bigint NOT NULL CHECK (byte_size > 0 AND byte_size <= 10485760),
  sha256 char(64) NOT NULL,
  storage_key text NOT NULL UNIQUE,
  status text NOT NULL CHECK (status IN ('UPLOADED', 'QUEUED', 'PROCESSING', 'READY', 'FAILED')),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, sha256)
);
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY documents_tenant_scope ON documents USING (organization_id = current_setting('app.organization_id', true)::uuid) WITH CHECK (organization_id = current_setting('app.organization_id', true)::uuid);
CREATE INDEX documents_tenant_status_idx ON documents(organization_id, status, created_at DESC);
