# Steps 1 and 2 verification

## Prerequisites

- Docker Desktop, or Python 3.12+ and Node.js 20+.

## Docker

```powershell
docker compose up --build
```

Open `http://localhost:3000`. Verify API probes at `http://localhost:8000/healthz` and `http://localhost:8000/readyz`.

Verify the Step 2 development identity endpoint:

```powershell
$headers = @{
  "X-Development-User-Id" = "018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bc"
  "X-Development-Organization-Id" = "018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bd"
  "X-Development-Role" = "ORG_ADMIN"
}
Invoke-RestMethod http://localhost:8000/v1/me -Headers $headers
```

The `X-Development-*` headers are temporary test-only identity. Step 3 replaces them with real OIDC authentication.

## Step 4: upload a document

```powershell
$headers = @{ "X-Development-User-Id" = "018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bc"; "X-Development-Organization-Id" = "018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bd" }
Invoke-RestMethod -Method Post -Uri http://localhost:8000/v1/documents -Headers $headers -Form @{ document_type = 'INVOICE'; file = Get-Item '.\sample-invoice.pdf' }
```

## API tests without Docker

```powershell
cd "C:\Users\narasimha\Desktop\Reconcile AI\services\api"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
uvicorn reconcileai.main:app --reload
```

## Web without Docker

```powershell
cd "C:\Users\narasimha\Desktop\Reconcile AI\apps\web"
npm install
npm run dev
```



"D:\ADBC_Srcs\CR-ALL-0535-SWIFT\ISCTRSTL_V9_NEW_final- Abu Dhabi\ISCTRSTL_V9_NEW_final\DDL\ISTB_CONTRACT_STRUCTURED_ADDR.sql"

use the same table and make rad and generate units