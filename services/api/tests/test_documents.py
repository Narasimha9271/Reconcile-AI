from fastapi.testclient import TestClient
from reconcileai.main import create_app

HEADERS = {'X-Development-User-Id':'018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bc','X-Development-Organization-Id':'018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bd'}

def test_invoice_upload_is_tenant_scoped_and_queued(tmp_path):
    app = create_app(); app.state.document_store.root = tmp_path
    client = TestClient(app)
    response = client.post('/v1/documents', headers=HEADERS, data={'document_type':'INVOICE'}, files={'file':('invoice.pdf', b'%PDF-1.4 fixture', 'application/pdf')})
    assert response.status_code == 201
    assert response.json()['status'] == 'QUEUED'
    assert len(client.get('/v1/documents', headers=HEADERS).json()) == 1

def test_document_rejects_unsafe_content_type():
    response = TestClient(create_app()).post('/v1/documents', headers=HEADERS, data={'document_type':'INVOICE'}, files={'file':('payload.exe', b'x', 'application/octet-stream')})
    assert response.status_code == 415
