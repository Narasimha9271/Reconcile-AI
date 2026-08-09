# Google OAuth local setup

1. In Google Cloud Console, add this authorized redirect URI:

   `http://localhost:4000/api/auth/google/callback`

2. Copy `.env.example` to `.env` in the project root. Fill the ID, newly rotated secret, approved Google emails in `GOOGLE_ALLOWED_EMAIL`, and a long random `SESSION_SECRET`. Separate multiple emails with commas, for example `owner@example.com,teammate@example.com`.

3. Restart:

   ```powershell
   cd "C:\Users\narasimha\Desktop\Reconcile AI"
   docker compose up --build -d
   ```

4. Open `http://localhost:3000`, click **Sign in with Google**, and choose the allowed email.

This local implementation validates OAuth state, verifies the Google email, creates an `AP_ANALYST` membership in the demo organization, and saves a signed session cookie. Production must replace the demo organization mapping with tenant onboarding and role assignment.
