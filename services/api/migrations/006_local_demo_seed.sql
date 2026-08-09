-- Local Docker demonstration identity. Replace with OIDC-driven provisioning before production.
ALTER TABLE organizations NO FORCE ROW LEVEL SECURITY;
ALTER TABLE memberships NO FORCE ROW LEVEL SECURITY;

INSERT INTO organizations (id, slug, name, status)
VALUES ('018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bd', 'local-demo', 'Local Demo Organization', 'ACTIVE')
ON CONFLICT (id) DO NOTHING;

INSERT INTO users (id, idp_subject, email, status)
VALUES ('018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bc', 'local-dev-user', 'developer@local.test', 'ACTIVE')
ON CONFLICT (id) DO NOTHING;

INSERT INTO memberships (organization_id, user_id, role)
VALUES ('018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bd', '018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bc', 'ORG_ADMIN')
ON CONFLICT (organization_id, user_id) DO NOTHING;

ALTER TABLE organizations FORCE ROW LEVEL SECURITY;
ALTER TABLE memberships FORCE ROW LEVEL SECURITY;
