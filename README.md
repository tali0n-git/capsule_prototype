# Capsule — Shared Patient Summary

A prototype information architecture and permission system for shared patient
summaries in multidisciplinary clinics.

---
---
---

# Post-Submission Changes

Changes made after April 6th submission:

- **Note entry tab** — Added an "Add Practitioners' Notes" tab where practitioners can submit structured notes per category. Only categories their role has full access to are shown. Notes are written to a new `Consultation` and `SummaryField`, and the write is logged to the audit trail.

- **Summary & Add Practitioners' Notes persistence** - The selected practitioner persists between these two tabs such that changing the practitioner view in the Summary tab switches the view to the same practitioner in the Notes tab, and vice-versa.

- **Practitioner consent state persistence** — The selected practitioner in the Practitioner Consent Settings tab now persists when switching between tabs, consistent with how the role selection persists in the Summary/Add Notes tabs.

- **Permission hierarchy fix** — Reordered the checks in `filter_summary` so that `role_restricted` is evaluated before `patient_restricted`. Previously, a patient opting out could override the reason label shown to a role that was already restricted, causing misleading feedback.

- **Summary field ordering** — Unified the category display order across the Summary tab and the Patient Consent Settings tab, with the three sensitive categories (Substance Use, Mental Health, Sexual Health) appearing last in both.

- **Manual note sharing behavior** — Manually entered notes are treated as raw full notes and default to sharing OFF in the Practitioner Consent Settings. Toggling sharing ON replaces the note with a "Summarized practitioner notes would be shown here" placeholder, representing what an AI-generated summary would produce.

- **Audit log improvements** — Audit log entries now record meaningful action labels for all event types: summary views, note submissions, and both patient and practitioner consent changes.


---
---
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

## How Capsule Approaches CYA Note Inflation

Capsule does not prevent practitioners from sharing full notes — but it makes
summarised sharing the default. The AI summary extracts clinically relevant
facts and removes subjective language, meaning practitioners who use the default
have no reason to write defensively.

Practitioners who opt into full note sharing do so deliberately. This is a
conscious tradeoff — full transparency between practitioners is sometimes
clinically valuable, and Capsule doesn't prohibit it. The risk of defensive
writing is managed through defaults, not restrictions.

### Three core requirements

**1. Role-based defaults**
Each discipline gets a sensible default view of patient data based on clinical
relevance. All practitioners see medications and allergies. A physio also sees musculoskeletal history. A psychologist
sees mental health and substance use. A dietitian sees nutritional
conditions. The GP sees everything. Each practitioner recieves clear indicators when other data is
unavailable and why.

**2. Visibility controls**
Patients can opt out of sharing sensitive categories (mental health, substance
use, sexual health). Practitioners can choose whether their records are
summarised for colleagues and patients. Both controls are stored in the database and enforced
server-side — never just hidden in the UI.

**3. Audit trail**
Every summary access is logged with the practitioner role, patient, fields
accessed, and timestamp. This protects practitioners (proves they acted on
available information) and creates accountability without surveillance.

---

## Unavailability States

A key design decision: the GP (and subsequentially, the patient) always sees every category, even when data is
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

Every summary request by a practitioner is logged to the `audit_logs` table. To inspect it, either open the `capsule.db` in your IDE, or run
the following from the `backend/` directory after viewing at least one summary:
```bash
sqlite3 capsule.db "SELECT * FROM audit_logs;"
```

Each row contains: `patient_id`, `practitioner_id`, `practitioner_role`,
`fields_accessed`, and `timestamp`.

---

## Interpreting Audit Log


| Action | Value |
|---|---|
| `Viewing Summary tab` | ["Summary", "viewed"] |
| `Submitting notes	` | ["Add Practitioners' Notes", "submitted"] |
| `Patient toggling consent on` | ["Patient Consent Settings", "opted_in"] |
| `Patient toggling consent off` | ["Patient Consent Settings", "opted_out"] |
| `Practitioner toggling consent on` | ["Practitioner Consent Settings", "opted_in"] |
| `Practitioner toggling consent off` | ["Practitioner Consent Settings", "opted_out"] |


---

## Project Structure
```
capsule/
├── backend/
│   ├── main.py           # FastAPI entry point, registers routers, sets up CORS
│   ├── models.py         # SQLAlchemy table definitions and Pydantic schemas
│   ├── database.py       # SQLite engine, session management, get_db dependency
│   ├── seed.py           # Seeds two realistic patients
│   ├── permissions.py    # Core permission logic — roles, access levels, filter_summary
│   └── routers/
│       ├── summary.py    # Summary endpoint — filters data, writes audit log
│       ├── auth.py       # Simulated auth — accepts role, returns mock session
│       ├── consent.py    # Patient consent endpoints — GET/PATCH opted-out categories
│       └── notes.py      # Note submission endpoint — creates consultations and summary fields

└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── SummaryView.jsx      # Composes full summary from SensitiveField components
    │   │   ├── RoleSwitcher.jsx     # Demo dropdown to switch between practitioner roles
    │   │   └── SensitiveField.jsx   # Renders a single field across all visibility states
    │   └── pages/
    │       ├── PatientSummary.jsx                  # Role-filtered summary view, fetches from API
    │       ├── PractitionerConsultationsPage.jsx   # Note entry form for the active practitioner
    │       ├── PractitionerVisibilityPage.jsx      # Toggles per-consultation sharing for each practitioner
    │       └── PatientConsentPage.jsx              # Toggles patient opt-out for sensitive categories
    ├── package.json
    └── index.html
```

---


## Known Limitations

- Auth is simulated — no real JWT validation or user management
- Two patients seeded — the demo is designed around two patients: one, to illustrate
  the full range of visibility states across all roles, the other to show a more sparse summary example
- SQLite is used for simplicity — a production system would use PostgreSQL with
  row-level security
- Summary fields are static strings — a production system would generate these
  dynamically using Heidi to summarise structured records



---

## Next Steps
- Test addition of redacted sensitive patient info; it should be possible for a specific practitioner to have this info in their specialty's summary view (e.g. if a patient gives access to one PHYSIO, every PHYSIO will be able to see this info)
  - Is this a reasonable permission format/structure to have? SHOULD every practitioner in a specific specialty be able to see one patent's sensitive info?

- Add sliders to Practitioners' Notes, such that every note's 'voice' can be tailored depending on the specific consultation
  - Make 'Goldilocks' the default
