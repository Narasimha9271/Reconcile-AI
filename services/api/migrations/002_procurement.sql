CREATE TABLE vendors (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
  name text NOT NULL CHECK (char_length(name) BETWEEN 1 AND 200),
  normalized_name text NOT NULL,
  external_ref text,
  status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'BLOCKED', 'INACTIVE')),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, external_ref)
);
CREATE INDEX vendors_tenant_name_idx ON vendors(organization_id, normalized_name);

CREATE TABLE purchase_orders (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
  vendor_id uuid NOT NULL REFERENCES vendors(id) ON DELETE RESTRICT,
  number text NOT NULL,
  status text NOT NULL DEFAULT 'OPEN' CHECK (status IN ('DRAFT', 'OPEN', 'CLOSED', 'CANCELLED')),
  currency char(3) NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (organization_id, number)
);

CREATE TABLE purchase_order_lines (
  id uuid PRIMARY KEY,
  purchase_order_id uuid NOT NULL REFERENCES purchase_orders(id) ON DELETE RESTRICT,
  line_no integer NOT NULL CHECK (line_no > 0),
  sku text,
  description text NOT NULL CHECK (char_length(description) BETWEEN 1 AND 500),
  quantity numeric(19,4) NOT NULL CHECK (quantity > 0),
  unit_price numeric(19,4) NOT NULL CHECK (unit_price >= 0),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (purchase_order_id, line_no)
);

ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY vendors_tenant_scope ON vendors USING (organization_id = current_setting('app.organization_id', true)::uuid) WITH CHECK (organization_id = current_setting('app.organization_id', true)::uuid);
CREATE POLICY purchase_orders_tenant_scope ON purchase_orders USING (organization_id = current_setting('app.organization_id', true)::uuid) WITH CHECK (organization_id = current_setting('app.organization_id', true)::uuid);
