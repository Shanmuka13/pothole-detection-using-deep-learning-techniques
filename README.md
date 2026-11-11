# UrbanPulse AI — Pothole Detection

UrbanPulse AI is a Python project for collecting road-damage reports, detecting potholes in uploaded images or videos, and helping municipal staff review and track complaints on a map.

**For the detailed architecture, module-by-module explanations, configuration, API routes, known limitations, and viva preparation, see [VIVA_GUIDE.md](VIVA_GUIDE.md).**

## What is included

- Streamlit citizen and authority-facing interface.
- FastAPI backend for media analysis, complaints, authentication, and GIS endpoints.
- YOLO model at `app/vision/models/best.pt`, plus sample image and video files.
- Optional MongoDB storage; without a working MongoDB connection the app uses an in-memory demo store.
- A standalone LangGraph workflow for deduplication, priority scoring, and simulated work-order estimates.
- Pytest tests under `tests/`.

The GitHub repository contains committed files only. Local `.env` settings, databases, logs, caches, virtual environments, and temporary outputs are excluded. Never commit passwords, SMTP credentials, or other secrets.

## Run locally

Use Python 3.10 (the Dockerfile's base version) and a terminal in the repository root.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

In terminal 1, start the API:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

In terminal 2, start the interface:

```powershell
streamlit run frontend/app.py --server.port 8501
```

Open <http://127.0.0.1:8501>. The API documentation is at <http://127.0.0.1:8001/docs>.

Copy `.env.example` to `.env` for local settings. Leave `MONGO_URI` empty for the in-memory demo. To use contractor sign-in, set a private `DEMO_CONTRACTOR_PASSWORD`; the contractor demo account is seeded with its hash when the backend starts. Keep `.env` local and never commit it. Email OTP and authority notifications require valid SMTP settings; map, geocoding, and elevation features use internet services.

## Run tests

```powershell
python -m pytest tests
```

`tests/test_geo.py` is a separate manual GIS smoke-test script; it makes external geocoding/elevation requests and can write generated map files.

## Sharing through GitHub

Commit and push the files you want your friend to receive. A GitHub ZIP contains only the committed files from the chosen branch and does not include Git history; use `git clone` to get the history. Check `git status` before sharing so intended local edits are committed, and review the repository for personal data and credentials before making it public.
