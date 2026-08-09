# Role access

Set approved Google users in `GOOGLE_ALLOWED_EMAIL`. Set the smaller group allowed to see and decide invoice reviews in `GOOGLE_FINANCE_APPROVER_EMAILS`.

```env
GOOGLE_ALLOWED_EMAIL=analyst@example.com,approver@example.com
GOOGLE_FINANCE_APPROVER_EMAILS=approver@example.com
```

An `AP_ANALYST` can use vendors and purchase orders but receives no reconciliation records from the API. A `FINANCE_APPROVER` can see the review queue and approve or reject decisions. Every approver must also be in the approved-user list.

After changing either list, restart the stack and log out/in again so the membership and session are refreshed.
