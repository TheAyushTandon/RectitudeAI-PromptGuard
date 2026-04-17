# Local Backend Setup for Vercel Frontend

To use your local machine as the "real" backend while keeping the frontend hosted on Vercel, follow these steps.

## 1. Expose Local Backend (Optional but Recommended)
If you visiting your Vercel URL from a different network (e.g., your phone), you will need a public tunnel.
*   **ngrok**: Run `ngrok http 8000`. Use the `https://...` URL it provides.
*   **Direct Localhost**: If ONLY visiting from the SAME machine as the backend, you can use `http://localhost:8000`.

## 2. Update Vercel Environment Variables
1.  Go to the **Vercel Dashboard** -> Your Project -> **Settings** -> **Environment Variables**.
2.  Find `NEXT_PUBLIC_API_BASE_URL`.
3.  Change its value to your tunnel URL (or `http://localhost:8000`).
4.  **Save** and **Redeploy** the latest commit.

## 3. Backend Configuration
Ensure your local `.env` has:
```env
USE_LOCAL_DB=true
```
This ensures your agents hit the local SQLite database.

## 4. Run the Backend
Always keep this command running on your local terminal:
```powershell
$env:PYTHONPATH = "."; uvicorn backend.gateway.main:app --reload
```
