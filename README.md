# Smart Civic Issue Reporting & Resolution Platform (Nagar Setu)

Build a platform where citizens report civic issues (potholes, garbage overflow, broken streetlights, water leakage) with geo-tagged photos. Issues are automatically routed to the correct municipal department, tracked through status updates, and displayed on a public transparency dashboard.

> **Note:** this repo uses session-based Django auth for both standard views and DRF API endpoints. Ensure you pass the `X-CSRFToken` header for API POST/PATCH requests.

## Tech Stack
- **Backend**: Django 4.2 + Django REST Framework (DRF)
- **Database**: SQLite (configured for local setup)
- **Frontend**: Django Templates with dynamic JS Fetch API integration
- **Maps**: Leaflet.js + OpenStreetMap (no API key required)
- **Image Storage**: Local Django `MEDIA_ROOT`
- **Auth**: Built-in Django Auth (session/cookie)

## Features Implemented
1. **Geo-tagged Reporting**
   - Citizens must be logged in to submit.
   - Interactive Leaflet map to pin location (lat/lng captured).
   - Form inputs for title, category, description, and photo (saved to `media/issues/`).
2. **Automated Routing & Status Tracking**
   - Issue category automatically maps to the correct department (`Roads`, `Sanitation`, `Electricity`, `Water Supply`) on creation.
   - Admin (superusers) can view all issues, filter by department, and update status (`submitted` → `in_progress` → `resolved`).
   - Citizens track their own submitted issues from a personal dashboard tab.
3. **Community Transparency Dashboard**
   - Public view, no login required.
   - Interactive Leaflet map with colored pins by status (Red = submitted, Blue = in progress, Green = resolved).
   - Metrics: % resolved, total issues, avg resolution time, resolution rate per department.
   - Open-issue list with an upvote toggle (1 per citizen per issue).

## Local Setup Instructions

1. **Activate Virtual Environment**
```powershell
   .\venv\Scripts\Activate.ps1
```
   *(or `.\myenv\Scripts\activate`, depending on which env folder your machine has)*

2. **Install Dependencies**
```bash
   pip install django djangorestframework django-cors-headers Pillow
```

3. **Navigate to the project directory**
```bash
   cd Smart_Civic_Issue
```

4. **Database Migrations** (run inside `myproject/` if that's your Django project root)
```bash
   python manage.py makemigrations
   python manage.py migrate
```

5. **Seed Initial Departments** *(if using the API-based seed command)*
```bash
   python manage.py seed_data
```

6. **Create Admin Superuser**
```bash
   python manage.py createsuperuser
```
   *Note: a demo superuser may already exist for testing — username `admin`, password `admin123`. Change this before deploying anywhere public.*

7. **Run Development Server**
```bash
   python manage.py runserver
```
   - Template views: `http://127.0.0.1:8000/`
   - API root (if applicable): `http://127.0.0.1:8000/api/`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/signup/` | Register a citizen |
| POST | `/api/login/` | Login a citizen |
| POST | `/api/login/admin/` | Login as admin |
| GET | `/api/issues/` | List issues (filter by `department` or `scope`) |
| POST | `/api/issues/create/` | Create an issue (auth required) |
| POST | `/api/issues/<id>/upvote/` | Upvote an issue (auth required, duplicates toggled) |
| POST | `/api/issues/<id>/status/` | Update status — requires admin (`is_superuser`) |
| GET | `/api/departments/` | List departments |

## Frontend Architecture

**Nagar Setu**'s frontend layers modern web patterns over a vintage municipal-ledger aesthetic:

### Visual theme
- **Typewriter tactility** — Google Fonts `Special Elite`, `Public Sans`, `IBM Plex Mono` evoke a physical ledger.
- **Palette** — soft paper background (`--paper: #F7F3E9`), deep navy ink (`--ink: #1F2A44`).
- **Stamps** — status indicators (`submitted`, `in_progress`, `resolved`) render as rotated rubber-ink stamps.

### Tab navigation
- Single-page-style dashboard in vanilla JS; tabs (`Public dashboard`, `Report an issue`, `Track my dockets`) toggle a `.hidden` class on content panels.
- `leafletMap.invalidateSize()` is called whenever a map panel goes from hidden → visible, so tiles recalculate correctly.

### Leaflet.js integration
- **Public dashboard map** — fetches active issues from `/api/issues/`, plots colored markers by status.
- **Location picker map** — click-to-pin, plus a "Use current location" button using the browser Geolocation API; matched against local zone landmarks (e.g. University Road) via distance calculation.

### REST integration
- Form submissions (including photo uploads) use `FormData` via the Fetch API.
- Auth forms retrieve the session's `csrftoken` cookie to secure POST headers.