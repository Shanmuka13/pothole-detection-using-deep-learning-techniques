# UrbanPulse AI — Project and Viva Guide

This guide explains the project as it is currently implemented. It distinguishes working application flows from standalone/demo components so a presentation does not overstate what the software currently does.

## 1. Project at a glance

**Problem:** Road damage is often reported reactively and duplicate reports can consume municipal staff time. This project demonstrates a digital intake and review workflow: a citizen submits evidence and a location, computer vision analyzes the evidence, and a municipal user can review and update the resulting complaint.

**Users and roles**

- **Citizen:** submits a road-damage report and checks its status using the complaint ID and matching phone number.
- **Authority:** reviews complaints and changes their status; may assign a complaint to a contractor.
- **Contractor:** can sign in in the demo and update assigned complaint status.

**Important scope distinction:** This is a hackathon/demo application, not a production municipal dispatch system. It contains useful end-to-end flows, but uses heuristic estimates and demo authentication/data behavior described below.

## 2. Technology inventory

| Area | Technologies | How the project uses them |
|---|---|---|
| Language/runtime | Python 3.10+ | Backend, computer vision, and UI code |
| Web UI | Streamlit, Streamlit Cookies Controller, Streamlit Geolocation | Citizen report form, authority/contractor workspaces, browser location, session cookies |
| API | FastAPI, Uvicorn, Pydantic | HTTP endpoints, request validation, and local API server |
| Computer vision | Ultralytics YOLO, PyTorch, OpenCV, NumPy, Pillow | Pothole inference, video frame handling, image annotation, and image metadata helpers |
| Maps/GIS | Folium, Streamlit-Folium, GeoPy | Interactive maps and Nominatim geocoding |
| Data | PyMongo / MongoDB; in-memory demo store | Persisted complaints, authorities, contractors, pincode areas, and GIS defects when configured |
| Workflow prototype | LangGraph, LangChain Core, Pydantic | Standalone report-validation, deduplication, priority, and work-order graph |
| Notifications | Python SMTP/email utilities | Optional OTP and authority notification email |
| External services | OpenStreetMap/Nominatim, Open-Meteo elevation API, Google Maps URL | Map tiles, address lookup, elevation estimate, and navigation link |

`requirements.txt` lists Python packages. It does not install MongoDB, provide SMTP credentials, or guarantee external services are reachable.

## 3. Architecture and data flow

### Citizen report flow

1. The citizen selects a photo or MP4 video in the Streamlit interface, enters a pincode and contact details, and supplies browser coordinates or a manual address.
2. The interface sends a multipart request to `POST /api/report/analyze`.
3. FastAPI validates required fields, stores the upload temporarily, and calls `app/vision/vision_engine.py`.
4. YOLO checks the image or sampled video frames. If no supported pothole is detected, the API returns a no-defect result without creating a complaint.
5. For a detected pothole, the backend resolves an address if needed, requests elevation, checks for a nearby existing report, and creates a GIS defect and complaint.
6. The backend builds an email draft and attempts an authority notification if SMTP is configured. The interface presents the analysis and report status.
7. An authority can review the complaint and update its workflow status. A citizen can look up a complaint with its ID and matching phone number.

### Authority and contractor flow

- Authority sign-in requests an email OTP; successful verification returns a bearer token. The frontend stores workspace/session details in browser cookies.
- Contractor sign-in uses the seeded `contact@metrofix.com` demo account. Set `DEMO_CONTRACTOR_PASSWORD` in the local `.env` before starting the backend; sign-in remains disabled when it is unset.
- Authority complaint listing and status changes use protected API routes.
- Assigning a contractor changes the complaint status to `ASSIGNED_TO_CONTRACTOR`; the contractor can update a complaint through its own route.

### Separate GIS dispatch flow

`app/geo/geo_dispatch.py` also contains a GIS processing path that can geocode an address, check for duplicates, obtain elevation, save a defect, generate a Google Maps route URL, and render a Folium HTML map. It is related to the reporting flow, but its simulated contractor alert is not the same as a real contractor dispatch integration.

### Standalone LangGraph workflow

`app/core/agent_graph.py` defines a separate workflow:

`validate → deduplicate → calculate priority/urgency → estimate materials and crew → create work order`

It uses deterministic formulas and Pydantic models. The current FastAPI complaint endpoint does **not** call `process_report`; the LangGraph work-order workflow is therefore a standalone prototype, not the live complaint-processing pipeline. `OLLAMA_BASE_URL` and `OLLAMA_MODEL` are defined in `app/core/config.py`, but the current graph does not use an LLM.

## 4. Repository map

| Path | Responsibility |
|---|---|
| `app/main.py` | FastAPI app, startup, report analysis, authentication, complaint APIs, and GIS API routes |
| `app/vision/vision_engine.py` | YOLO model loading, image/video inference, filtering, severity estimates, and annotated image output |
| `app/vision/models/best.pt` | Trained YOLO weights used by the vision engine |
| `app/mongo_store.py` | MongoDB setup, demo-mode in-memory collections, indexes, seed data, and data access |
| `app/auth.py` | PBKDF2 password hashing and verification for password-based demo accounts |
| `app/email_alerts.py` | OTP email and authority alert construction/sending |
| `app/geo/database.py` | GIS defect persistence and distance-based duplicate check |
| `app/geo/geo_dispatch.py` | Geocoding, elevation/flood-risk heuristic, route URL, dispatch simulation, and map rendering |
| `app/core/agent_graph.py` | Standalone LangGraph workflow and deterministic work-order calculations |
| `app/core/config.py` | Graph configuration values |
| `frontend/app.py` | Main Streamlit interface and calls to the API |
| `frontend/components/` | Reusable map and sidebar components |
| `tests/` | Pytest tests and a separate manual GIS smoke test |
| `requirements.txt` | Python dependency list |
| `Dockerfile` | Container build and combined API/UI startup |
| `.env.example` | Names and safe examples for environment configuration; not credentials |

## 5. Vision behavior and numbers

The model is loaded from `app/vision/models/best.pt` when the vision module is imported.

- YOLO inference uses confidence threshold **0.35**, IoU **0.45**, image size **640**, and at most **20** detections per inference.
- Only model class names `pothole` or `potholes` are accepted.
- A bounding box is accepted when its area is between **0.05%** and **60%** of the image area.
- Video is sampled every **10 frames** and requires at least **2 sampled frames** with valid detections to count as a confirmed defect.
- The displayed **0–10 severity score** is a heuristic based on bounding-box area and model confidence; it is not a calibrated engineering measurement.
- The additional Low/Medium/High/Critical label uses bounding-box size, position, and shape. The displayed depth values (5, 15, 20, or 25 cm) are estimates, not measured depth.
- An annotated image is written under `temp/`; this output is temporary and is not a complaint evidence archive.

The vision module has an EXIF GPS helper, but the current report endpoint uses location supplied by the interface (browser coordinates or manual address) rather than using the helper's returned GPS coordinates.

## 6. Geospatial and duplicate logic

- Manual addresses can be forward-geocoded; coordinates can be reverse-geocoded through Nominatim.
- Elevation is queried from Open-Meteo. The project labels a location flood-prone when the elevation value is below **15 m**. This is a simple demo heuristic, not a real flood forecast.
- Complaint intake checks for an existing defect within **15 m** before inserting. The lower-level GIS database helper has a **50 m** default when called without an explicit threshold; the report flow passes 15 m.
- The standalone LangGraph duplicate check uses the configurable `DUPLICATE_DISTANCE_METERS`, default **15 m**, and only considers pending reports supplied to the graph.
- The project uses OpenStreetMap map tiles and creates a Google Maps driving-directions URL; it does not calculate an optimized contractor route.

External geocoding/elevation requests require internet access and may be rate-limited or unavailable. Coordinates and addresses should be reviewed before operational use.

## 7. Data storage and configuration

At startup the store initializes and seeds demo records. If MongoDB is configured and reachable, collections are stored in the selected database. If `MONGO_URI` is empty or the MongoDB ping fails, the app uses an in-memory demo store; data in that store is lost when the process restarts. The separate `defects.db`/`urbanpulse.db` files found in some local workspaces are not required by the current store implementation and are ignored by Git.

| Variable | Purpose | Default/notes |
|---|---|---|
| `MONGO_URI` | MongoDB connection string | Empty means in-memory demo mode |
| `MONGO_DATABASE` | MongoDB database name | `urbanpulse` |
| `SMTP_HOST` | SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | SMTP login user | May fall back to `SMTP_EMAIL` or `APP_EMAIL` |
| `SMTP_EMAIL` / `APP_EMAIL` | Sender account compatibility settings | Configure only with an account you control |
| `SMTP_PASSWORD` | SMTP password or app password | Keep private; never commit it |
| `SMTP_FROM` | Displayed sender | Defaults to the SMTP username |
| `AUTHORITY_ALERT_EMAIL` | Fallback authority notification destination | Demo fallback |
| `DEMO_CONTRACTOR_PASSWORD` | Password for the seeded contractor demo account | Optional; set privately in `.env` to enable contractor sign-in |
| `BACKEND_BASE_URL` | API URL used by the Streamlit frontend | `http://127.0.0.1:8001` |
| `DUPLICATE_DISTANCE_METERS` | Standalone graph's duplicate radius | `15` |
| `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | Reserved graph configuration | Not used by the current graph processing |

Copy `.env.example` to `.env` for local configuration. `.env` is intentionally ignored. Contractor sign-in stays disabled until `DEMO_CONTRACTOR_PASSWORD` is set and the backend is restarted. The admin/authority portal uses email OTP, not this contractor password. Do not copy real passwords, access tokens, or private database URLs into GitHub.

## 8. API route overview

FastAPI's interactive schema at `/docs` is the authoritative request/response reference.

| Method and route | Purpose |
|---|---|
| `POST /api/report/analyze` | Analyze uploaded media and create a complaint when a defect is confirmed |
| `POST /api/auth/login` | Start authority OTP sign-in or contractor password sign-in |
| `POST /api/auth/verify-otp` | Verify an authority OTP and issue a token |
| `GET /api/complaints/{complaint_id}` | Get a complaint when the reporter phone matches |
| `GET /api/pincodes/{pincode}` | Look up an active authority area |
| `GET /api/authority/complaints` | List complaints for an authenticated authority |
| `PATCH /api/authority/complaints/{complaint_id}` | Update an authority complaint and optionally assign a contractor |
| `PATCH /api/contractor/complaints/{complaint_id}` | Update a complaint as an authenticated contractor |
| `POST /api/geo/dispatch` | Run the separate GIS dispatch operation |
| `GET /api/geo/defects` | List GIS defects |
| `GET /api/geo/map` | Generate/return the dispatch map |
| `GET /api/analysis/annotated-image` | Retrieve the latest annotated image |
| `GET /api/sample-db` | Inspect sample/demo database status |

## 9. Complaint statuses

The API accepts these authority complaint statuses:

- `PENDING_VERIFICATION`
- `IN_PROGRESS`
- `ASSIGNED_TO_CONTRACTOR`
- `RESOLVED`
- `REJECTED`

When a contractor ID is supplied during an authority update, the backend sets the status to `ASSIGNED_TO_CONTRACTOR`.

## 10. Run and test

Use Python 3.10, matching the Dockerfile base image. From the repository root on Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start the backend in one terminal:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Start the UI in another:

```powershell
streamlit run frontend/app.py --server.port 8501
```

Then open <http://127.0.0.1:8501>. API schema: <http://127.0.0.1:8001/docs>.

Run the automated pytest tests:

```powershell
python -m pytest tests
```

`tests/test_geo.py` is not a normal pytest test module; run it manually with `python tests/test_geo.py` only when you want the network-dependent GIS smoke test. It can write `test_map.html` and mutate the active data store.

The Dockerfile starts the API on port 8001 and Streamlit on port 7860. Local development commands above use ports 8001 and 8501 respectively.

## 11. Demo and production limitations

Be transparent about these points during a viva:

1. **Authentication is demo-oriented.** Authority OTP sign-in accepts a syntactically valid email and can assign the shared authority workspace; it is not an invitation-controlled production identity system. Restrict it before deployment.
2. **Do not use seeded credentials in production.** Demo accounts and seed data are in source code. Replace them and rotate any credentials if the repository has been exposed publicly.
3. **Demo fallback data is temporary.** The in-memory store is not durable and is not a substitute for configured production MongoDB.
4. **Severity and depth are estimates.** Bounding-box heuristics do not measure physical pothole depth or replace an engineer's inspection.
5. **Flood risk is a simplistic rule.** Elevation below 15 m alone does not establish flood risk.
6. **Dispatch is not fully automated.** Email notifications depend on SMTP configuration; the GIS contractor alert is simulated, and the email draft is reviewable.
7. **External services can fail.** Geocoding, elevation lookups, map tiles, SMTP, and MongoDB require working network/service configuration.
8. **Security hardening is needed.** Demo OTP/account behavior, broad CORS settings, and local token handling need review before public production use.

## 12. Suggested viva questions and answers

**What problem does the project solve?**

It demonstrates how citizen image/video reports can be analyzed and organized into a municipal review workflow, reducing manual triage and helping identify nearby duplicate reports.

**Why use YOLO?**

YOLO provides object-detection bounding boxes and confidence scores in one inference pass, which suits locating potholes in images and sampled video frames.

**How does the system decide that a pothole exists?**

It keeps detections for the pothole class that meet the confidence and bounding-box-size filters. A video needs detections in at least two sampled frames to reduce single-frame false positives.

**How is severity calculated?**

The code computes a heuristic score from detection box area and confidence, then maps a visual geometry score to a severity label and approximate depth. These are demo estimates, not physical measurements.

**How are duplicate reports handled?**

The live complaint path checks the report coordinates against existing GIS defects using Haversine distance and a 15 m threshold. The standalone graph has a separate pending-report deduplication stage.

**Why FastAPI and Streamlit?**

FastAPI separates model/report processing behind API endpoints, while Streamlit provides a quick Python-based interface for the citizen and staff demo.

**What happens when MongoDB is not configured?**

The app falls back to in-memory collections so a demo can start, but the records disappear when the backend restarts.

**Does the LangGraph call an LLM?**

No. The current LangGraph is a standalone deterministic workflow; it does not call an LLM and is not invoked by the active report endpoint.

**How are locations shown and addressed?**

The app accepts browser coordinates or a manual address, uses Nominatim for geocoding where needed, obtains elevation from Open-Meteo, and renders map views with Folium/OpenStreetMap.

**What would you improve next?**

Integrate the work-order graph into the live complaint lifecycle; use measured, validated severity and flood-risk models; add production-grade access control and audit logs; persist uploaded evidence securely; and add integration tests for the full workflow.

## 13. Sharing the project

GitHub shares committed files, not uncommitted local edits. Before sharing:

1. Review `git status`, then commit and push the intended code and documentation.
2. Check that `.env`, tokens, personal information, and real credentials are not staged.
3. The model `app/vision/models/best.pt`, `test_pothole.jpg`, and `Test_vid.mp4` are tracked in this checkout, so they are included in Git history/ZIPs once their commits are pushed. Check file size and licensing before redistributing them.
4. A ZIP download does not contain commit history. Your friend should clone the repository to see the history.
5. Share any required private service credentials separately through a secure method; never place them in the repository.
