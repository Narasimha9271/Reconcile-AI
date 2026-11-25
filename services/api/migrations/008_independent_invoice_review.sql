-- Old records have no trustworthy submitter. Preserve them, but never invent one.
ALTER TABLE reconciliation_cases ADD COLUMN submitted_by uuid REFERENCES users(id);
-- NOT VALID preserves historical rows while enforcing these rules on new writes.
ALTER TABLE reconciliation_cases ADD CONSTRAINT case_submitter_required
  CHECK (submitted_by IS NOT NULL) NOT VALID;
ALTER TABLE reconciliation_cases ADD CONSTRAINT case_independent_review
  CHECK (decision IS NULL OR
    (reviewed_by IS NOT NULL AND submitted_by IS NOT NULL AND reviewed_by <> submitted_by)) NOT VALID;
