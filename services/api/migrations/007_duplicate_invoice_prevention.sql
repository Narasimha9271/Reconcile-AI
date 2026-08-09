-- One invoice number may be submitted once per vendor and organization.
-- vendor_id is derived from the selected PO, not trusted invoice text.
ALTER TABLE reconciliation_cases ADD COLUMN IF NOT EXISTS vendor_id uuid;
ALTER TABLE reconciliation_cases ADD COLUMN IF NOT EXISTS duplicate_of uuid;

UPDATE reconciliation_cases AS rc
SET vendor_id = po.vendor_id
FROM purchase_orders AS po
WHERE po.id = rc.purchase_order_id
  AND rc.vendor_id IS NULL;

ALTER TABLE reconciliation_cases
  ALTER COLUMN vendor_id SET NOT NULL;

ALTER TABLE reconciliation_cases
  ADD CONSTRAINT reconciliation_cases_vendor_fk
  FOREIGN KEY (vendor_id) REFERENCES vendors(id);

-- Preserve historical duplicate records instead of deleting them. The oldest
-- case remains the original; later copies cannot be approved.
WITH ranked_cases AS (
  SELECT
    id,
    first_value(id) OVER invoice_group AS original_id,
    row_number() OVER invoice_group AS invoice_rank
  FROM reconciliation_cases
  WINDOW invoice_group AS (
    PARTITION BY organization_id, vendor_id,
      lower(regexp_replace(btrim(invoice_number), '\\s+', ' ', 'g'))
    ORDER BY created_at, id
  )
)
UPDATE reconciliation_cases AS rc
SET duplicate_of = ranked_cases.original_id
FROM ranked_cases
WHERE rc.id = ranked_cases.id
  AND ranked_cases.invoice_rank > 1
  AND rc.duplicate_of IS NULL;

ALTER TABLE reconciliation_cases
  ADD CONSTRAINT reconciliation_cases_duplicate_of_fk
  FOREIGN KEY (duplicate_of) REFERENCES reconciliation_cases(id);

CREATE UNIQUE INDEX reconciliation_cases_unique_vendor_invoice_idx
  ON reconciliation_cases (
    organization_id,
    vendor_id,
    lower(regexp_replace(btrim(invoice_number), '\\s+', ' ', 'g'))
  )
  WHERE duplicate_of IS NULL;
