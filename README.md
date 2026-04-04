# Capsule — Shared Patient Summary

A prototype information architecture and permission system for shared patient
summaries in multidisciplinary clinics. Built as part of a Product Growth
application to Heidi.

---

## The Problem

In multidisciplinary clinics, patients see GPs, physios, dietitians, and
psychologists — each keeping their own notes with no unified view. This causes:

- Missed clinical context across disciplines
- Conflicting advice given to the same patient
- Patients acting as the information bridge between practitioners
- Duplicated or unsafe care

## The Approach

Capsule solves this by separating **structured summary facts** from **clinical
notes**. Practitioners write freely in their own notes, and a separate summary layer surfaces only what is clinically relevant to
each role — with explicit visibility controls for both patients and practitioners. A practitioner can choose to make specific consultation events fully visible by toggling the summary slider off (it is on by default).

### Three core requirements

**1. Role-based defaults**
Each discipline gets a sensible default view of patient data based on clinical
relevance. All practitioners see medications and allergies. A physio also sees musculoskeletal history. A psychologist
sees mental health and substance use. A dietitian sees nutritional
conditions. The GP sees everything. Each practitioner recieves clear indicators when data is
unavailable and why.

**2. Visibility controls**
Patients can opt out of sharing sensitive categories (mental health, substance
use, sexual health). Practitioners can choose whether their records are
summarised for colleagues. Both controls are stored in the database and enforced
server-side — never just hidden in the UI.

**3. Audit trail**
Every summary access is logged with the practitioner role, patient, fields
accessed, and timestamp. This protects practitioners (proves they acted on
available information) and creates accountability without surveillance.

---

## Unavailability States

A key design decision: the GP always sees every category, even when data is
unavailable. Rather than silence, every restricted field returns a reason that
guides the practitioner's next action:

| Reason | What it means | Suggested action |
|---|---|---|
| `No record` | Nothing exists for this patient | Ask the patient directly |
| `Not available to your role` | Your role cannot see this category | Contact the relevant practitioner |
| `Patient has restricted access to this field` | Patient has opted out of sharing | Discuss with the patient directly |

---

## Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Frontend:** React (Vite)

---

## Requirements

- Python 3.11+
- Node.js >= 20 (https://nodejs.org) — **required for the frontend to run**

---

## Setup Instructions

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

**Frontend** *(requires Node.js to be installed)*
```bash
cd frontend
npm install
npm run dev
```

Both servers must be running for the application to work:
- Backend runs at `http://localhost:8000`
- Frontend runs at `http://localhost:5173`
- Interactive API docs are available at `http://localhost:8000/docs`

---

## Auth Note

The `/auth/session` endpoint is simulated for demo purposes. It accepts a role
(`GP`, `PHYSIO`, `DIETITIAN`, or `PSYCHOLOGIST`) and returns the first
practitioner in the database matching that role. In a production system this
would validate a JWT and return the authenticated user.

---

## Verifying the Audit Log

Every summary request is logged to the `audit_logs` table. To inspect it, run
the following from the `backend/` directory after viewing at least one summary:
```bash
sqlite3 capsule.db "SELECT * FROM audit_logs;"
```

Each row contains: `patient_id`, `practitioner_id`, `practitioner_role`,
`fields_accessed` (JSON list of visible categories), and `timestamp`.

---

## Project Structure
```
capsule/
├── backend/
│   ├── main.py           # FastAPI entry point, registers routers, sets up CORS
│   ├── models.py         # SQLAlchemy table definitions and Pydantic schemas
│   ├── database.py       # SQLite engine, session management, get_db dependency
│   ├── seed.py           # Seeds one realistic patient across all four disciplines
│   ├── permissions.py    # Core permission logic — roles, access levels, filter_summary
│   └── routers/
│       ├── summary.py    # Summary endpoint — filters data, writes audit log
│       └── auth.py       # Simulated auth — accepts role, returns mock session
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── SummaryView.jsx      # Composes full summary from SensitiveField components
    │   │   ├── RoleSwitcher.jsx     # Demo dropdown to switch between practitioner roles
    │   │   └── SensitiveField.jsx   # Renders a single field across all visibility states
    │   └── pages/
    │       └── PatientSummary.jsx   # Page component, holds role state, fetches from API
    ├── package.json
    └── index.html
```

---

## Known Limitations

- Auth is simulated — no real JWT validation or user management
- Single patient seeded — the demo is designed around one patient to illustrate
  the full range of visibility states across roles
- SQLite is used for simplicity — a production system would use PostgreSQL with
  row-level security
- Summary fields are static strings — a production system would generate these
  dynamically, potentially using an LLM to summarise structured records