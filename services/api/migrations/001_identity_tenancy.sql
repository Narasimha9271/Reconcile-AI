CREATE EXTENSION IF NOT EXISTS citext;

CREATE TABLE organizations (
  id uuid PRIMARY KEY,
  slug citext NOT NULL UNIQUE,
  name text NOT NULL CHECK (char_length(name) BETWEEN 1 AND 200),
  status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUSPENDED')),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE users (
  id uuid PRIMARY KEY,
  idp_subject text NOT NULL UNIQUE,
  email citext NOT NULL UNIQUE,
  status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'DISABLED')),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE memberships (
  organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  role text NOT NULL CHECK (role IN ('AP_ANALYST', 'PROCUREMENT_MANAGER', 'FINANCE_APPROVER', 'ORG_ADMIN', 'AUDITOR')),
  approval_limit numeric(19,4),
  approval_currency char(3),
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (organization_id, user_id),
  CHECK ((approval_limit IS NULL AND approval_currency IS NULL) OR (approval_limit >= 0 AND approval_currency ~ '^[A-Z]{3}$'))
);

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;
CREATE POLICY organization_tenant_scope ON organizations
  USING (id = current_setting('app.organization_id', true)::uuid);
CREATE POLICY membership_tenant_scope ON memberships
  USING (organization_id = current_setting('app.organization_id', true)::uuid)
  WITH CHECK (organization_id = current_setting('app.organization_id', true)::uuid);

CREATE INDEX memberships_user_organization_idx ON memberships(user_id, organization_id);
