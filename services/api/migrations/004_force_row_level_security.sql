-- Table owners normally bypass RLS. Force policies for the application role as well.
ALTER TABLE organizations FORCE ROW LEVEL SECURITY;
ALTER TABLE memberships FORCE ROW LEVEL SECURITY;
ALTER TABLE vendors FORCE ROW LEVEL SECURITY;
ALTER TABLE purchase_orders FORCE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

ALTER TABLE purchase_order_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_order_lines FORCE ROW LEVEL SECURITY;
CREATE POLICY purchase_order_lines_tenant_scope ON purchase_order_lines
  USING (EXISTS (
    SELECT 1 FROM purchase_orders
    WHERE purchase_orders.id = purchase_order_lines.purchase_order_id
      AND purchase_orders.organization_id = current_setting('app.organization_id', true)::uuid
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM purchase_orders
    WHERE purchase_orders.id = purchase_order_lines.purchase_order_id
      AND purchase_orders.organization_id = current_setting('app.organization_id', true)::uuid
  ));
