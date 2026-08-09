from fastapi.testclient import TestClient
from reconcileai.main import create_app

HEADERS = {'X-Development-User-Id':'018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bc','X-Development-Organization-Id':'018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bd'}

def test_vendor_and_purchase_order_are_tenant_scoped():
    client = TestClient(create_app())
    vendor = client.post('/v1/vendors', headers=HEADERS, json={'name':'Acme Supplies'}).json()
    response = client.post('/v1/purchase-orders', headers=HEADERS, json={'vendor_id':vendor['id'],'number':'PO-1001','currency':'USD','lines':[{'line_no':1,'description':'Widgets','quantity':'2','unit_price':'12.50'}]})
    assert response.status_code == 201
    assert response.json()['lines'][0]['quantity'] == '2'
    other_headers = {**HEADERS, 'X-Development-Organization-Id':'018f1c43-68a1-7f1e-a7ec-0e8cf2ef72be'}
    assert client.get('/v1/vendors', headers=other_headers).json() == []
