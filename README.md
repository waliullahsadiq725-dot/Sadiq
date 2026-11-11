# NUDL Backend — Nangarhar University Digital Library

FastAPI backend for a university library. Students and teachers can register and upload PDF books. Every new upload is **pending** until an administrator approves it. Approved PDFs can be searched, read/downloaded by signed-in users.

## Features
- Student and teacher public registration; admin accounts are created privately.
- JWT login and `/api/auth/me`.
- PDF upload with file extension, PDF signature and size checks.
- Admin approval/rejection queue.
- Search and category/faculty filters.
- User's own upload list and deletion.
- Admin user management and statistics.
- SQLite for local testing; PostgreSQL for production.
- Persistent upload directory configured by environment variable.

## 1. Run locally (Windows)
Install Python 3.11 or newer. Open PowerShell in this folder:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to test the API.

For local testing, the default database is SQLite. The `uploads` folder is created automatically.

## 2. Create the first Super Admin
In PowerShell, set credentials and run:

```powershell
$env:ADMIN_NAME="NUDL Super Admin"
$env:ADMIN_EMAIL="your-admin-email@example.com"
$env:ADMIN_PASSWORD="Use-A-Strong-Password"
python create_admin.py
```

Do not publish admin credentials or commit `.env` to GitHub.

## 3. Deploy on Render
1. Push this folder's contents to a new GitHub repository (the files inside the folder, not an extra nested folder).
2. Create a PostgreSQL database on Render.
3. Create a Web Service from the repository.
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `DATABASE_URL`: Render PostgreSQL **Internal Database URL** (replace `postgres://` if needed; app handles that prefix).
   - `SECRET_KEY`: a long random secret.
   - `UPLOAD_DIR`: `/var/data/uploads`
   - `MAX_UPLOAD_MB`: `50`
   - `FRONTEND_ORIGINS`: your frontend URL, or `*` temporarily while testing.
7. Add a Render Persistent Disk mounted at `/var/data`. Without persistent storage, uploaded PDFs may disappear when the service restarts or redeploys.
8. To create the first admin, open the Render Shell and run `python create_admin.py` after setting `ADMIN_NAME`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD` environment variables. If shell access is unavailable, run the script locally with the production `DATABASE_URL` set securely.

## API quick guide
All protected routes require header:
`Authorization: Bearer YOUR_ACCESS_TOKEN`

- `POST /api/auth/register` — student/teacher registration.
- `POST /api/auth/login` — login.
- `GET /api/auth/me` — current account.
- `POST /api/books/upload` — multipart PDF upload. Fields: `title` (required), `pdf` (required), `author`, `description`, `faculty`, `department`, `category`.
- `GET /api/books` — approved books for normal users. Query: `search`, `category`, `faculty`, `skip`, `limit`.
- `GET /api/books/mine` — books uploaded by current user, including pending/rejected.
- `GET /api/books/pending` — admin review queue.
- `PATCH /api/books/{id}/review` — admin approval. JSON: `{"status":"approved"}` or `{"status":"rejected","rejection_reason":"..."}`
- `GET /api/books/{id}/download` — PDF download.
- `DELETE /api/books/{id}` — owner or admin deletes a book.
- `GET /api/admin/users` — admin user list.
- `PATCH /api/admin/users/{id}/status?is_active=false` — enable/disable user.
- `GET /api/admin/stats` — dashboard counts.
- `GET /health` — health check.

## Important notes
- This starter stores PDFs on the server disk. For Render production, a persistent disk is required. For multiple server instances, use object storage instead.
- Before going live, set a strong `SECRET_KEY`, restrict `FRONTEND_ORIGINS` to the exact frontend domain, and confirm that you have permission to share each uploaded book. Do not upload copyrighted books without permission.
- This package is a clean backend foundation. It does not automatically modify an already deployed Render service. Deploy it to the intended repository/service and then connect the frontend to its API URL.
