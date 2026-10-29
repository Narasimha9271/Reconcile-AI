# AI invoice extraction

## What is implemented

ReconcileAI can accept an invoice PDF, PNG, JPEG, or WEBP file (maximum 8 MB) and return candidate invoice fields:

- invoice number
- vendor name
- total amount
- currency
- extraction confidence and notes

When `OPENAI_API_KEY` is configured, the API sends the document to the OpenAI Responses API and requests a strict JSON schema. Images use vision input. Text-based PDFs are parsed locally and supplied as text. A PDF without selectable text should be exported as a clear image for this version.

Without an API key, text-based PDFs use the existing local pattern extractor. If the OpenAI service is temporarily unavailable, text-based PDFs also fall back locally and show an `extraction_notes` warning. Image extraction requires a working API key.

## Safety design

The model receives document data only. The prompt explicitly treats document contents as untrusted and asks for `null` instead of invented values. The output is candidate data that is shown to the user for review. It cannot approve or pay an invoice.

The reconciliation module independently compares the vendor, currency, and amount against the selected purchase order. A Finance Approver must approve or reject a case. This keeps a clear audit boundary between AI extraction and a financial decision.

## Enable it locally

1. Open `.env` in the repository root; create it from `.env.example` if needed.
2. Add the values from `.env.ai.example`, replacing `your_openai_api_key_here` with a key from the OpenAI Platform. Do not paste the key into source code or commit it.
3. Restart the stack:

```powershell
# Run from the cloned Reconcile-AI repository root.
docker compose up --build
```

4. Open `http://localhost:3000`, sign in, then create a vendor and purchase order.
5. In **3. Extract & reconcile invoice**, choose an invoice file and select **Extract with AI**.
6. Inspect and correct the filled invoice fields. Select the PO, then choose **Review & run reconciliation**.

## API test

After signing in through the browser, use the dashboard for the simplest test because the browser sends its session cookie. For development-header testing only, replace `C:\path\to\a-real-invoice.pdf` with a valid PDF or image on your computer. `curl.exe` is used because Windows PowerShell 5.1 does not support multipart form upload through `Invoke-RestMethod`.

```powershell
$headers = @{
  "X-Development-User-Id" = "018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bc"
  "X-Development-Organization-Id" = "018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bd"
  "X-Development-Role" = "ORG_ADMIN"
}

curl.exe -X POST "http://localhost:8000/v1/ai/extract-invoice-upload" `
  -H "X-Development-User-Id: $($headers['X-Development-User-Id'])" `
  -H "X-Development-Organization-Id: $($headers['X-Development-Organization-Id'])" `
  -H "X-Development-Role: ORG_ADMIN" `
  -F "file=@C:\path\to\a-real-invoice.pdf;type=application/pdf"
```

Expected result: JSON with `provider` equal to `openai:<model>` when the key is configured, or `local-structured-extractor` for the fallback. The extracted values should appear in the dashboard form; they are not automatically approved.

## Operational constraints

- Do not use production finance documents until your company has approved the AI provider, retention policy, and data-processing terms.
- Keep the key in a secret manager when deployed; `.env` is for local development only.
- The system enforces format and size limits but is not yet a malware-scanning file store. Add virus scanning and durable S3 storage before production.
