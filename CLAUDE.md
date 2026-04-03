# Capsule — Shared Patient Summary

## What this project is
Capsule is a prototype shared patient summary system for multidisciplinary clinics
where patients see GPs, physios, dietitians, and psychologists. 

This prototype demonstrates an information architecture and permission model for a
shared Patient Summary that is genuinely useful, clinically safe, low overhead, and
legally survivable.

---

## Stack
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **Frontend:** React (Vite), JSX

---

## Project Structure
```
capsule/
├── backend/
│   ├── venv/                 # Virtual environment (already gitignored)
│   ├── main.py               # FastAPI app entry point, registers routers, sets up CORS
│   ├── models.py             # SQLAlchemy table definitions and Pydantic schemas
│   ├── database.py           # SQLite engine, session management, get_db dependency
│   ├── seed.py               # Seeds one realistic patient with data across all disciplines
│   ├── permissions.py        # Core permission logic — roles, access levels, filter_summary
│   └── routers/
│       ├── summary.py        # Main summary endpoint — filters data, writes audit log
│       └── auth.py           # Simulated auth — accepts role param, returns mock session context
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

## Three Core Requirements
Every decision in this codebase should serve these three requirements:

### 1. Audit Trail
- Every access to a patient summary is logged to the AuditLog table
- Log entries include: practitioner role, patient ID, fields accessed, timestamp
- Logging happens in routers/summary.py after filtering, before returning the response
- The audit log is append-only — no deletes, no updates

### 2. Role-Based Defaults
- Each discipline gets a sensible default view defined in permissions.py
- Roles: GP, PHYSIO, DIETITIAN, PSYCHOLOGIST
- Access levels: FULL, RESTRICTED, HIDDEN
- GP has no HIDDEN fields — they always know every category exists
- Other roles have HIDDEN applied to categories that are clinically irrelevant to them
- RESTRICTED means the role knows the category exists but cannot see the value

### 3. Visibility Controls
- Patients can opt out of sharing sensitive categories: mental_health, substance_use, sexual_health
- Practitioners can choose whether their notes are summarised for other practitioners
- Both controls are stored in the database and evaluated in filter_summary
- Controls are applied on top of role defaults — they can only restrict further, never grant more access

---

## Permission Logic
The core of this project lives in permissions.py. Key principles:

- **Raw summary is never sent directly to the frontend** — it always passes through filter_summary
- **Every field always returns a consistent shape:**
  - Visible: `{"visible": True, "value": "..."}`
  - Unavailable: `{"visible": False, "reason": "...", "label": "..."}`
- **Four unavailability reasons:**
  - `no_record` — nothing exists for this patient in this category
  - `role_restricted` — this role's access level is RESTRICTED for this category
  - `patient_restricted` — patient has opted out of sharing this category
  - `practitioner_restricted` — practitioner has chosen not to share this in the summary
- **Check order in filter_summary:**
  1. no_record (short circuits — nothing to restrict if data doesn't exist)
  2. practitioner_restricted (active privacy decision, respected before consent)
  3. patient_restricted (patient consent)
  4. role access level (HIDDEN silently skips, RESTRICTED returns reason)
  5. FULL — return value

---

## Data Model
Tables in models.py:

- `Patient` — basic demographics
- `Practitioner` — name, role, discipline
- `Consultation` — a clinical encounter, owned by a practitioner
- `SummaryField` — a structured shareable fact extracted from a consultation
- `PatientConsent` — which sensitive categories a patient has opted out of sharing
- `PractitionerVisibilityControl` — whether a practitioner allows their notes to be summarised
- `AuditLog` — every access event: practitioner role, patient ID, fields accessed, timestamp

---

## Key Architectural Decisions
These are intentional — do not change without good reason:

1. **Permissions are enforced server-side in filter_summary, never on the frontend.**
   The frontend receives only what the role is allowed to see. Hiding fields in the UI
   is not access control.

2. **The raw summary always contains every field, even if the value is None.**
   This ensures filter_summary always iterates over every category and no_record
   is always surfaced correctly.

3. **HIDDEN fields are silently skipped for non-GP roles, but GPs always see every category.**
   A GP needs to know a category exists even if data is unavailable, so they can
   ask the patient directly. Other roles don't need to know irrelevant categories exist.

4. **Unavailability reasons travel with the field in the API response.**
   The label is included in the response so SensitiveField.jsx just renders
   field.label without its own lookup table.

5. **Auth is simulated for demo purposes.**
   routers/auth.py accepts a role parameter and returns a mock session. This is
   intentional for the prototype — real auth would use JWT tokens.

6. **The audit log is written after filtering, before returning the response.**
   This ensures we log what was actually returned, not what existed in the raw summary.

---

## Build Order
When building out files, follow this order — each step depends on the previous:

1. database.py
2. models.py
3. seed.py — run this immediately to have data to work with
4. permissions.py
5. routers/summary.py
6. routers/auth.py
7. main.py
8. SensitiveField.jsx
9. RoleSwitcher.jsx
10. SummaryView.jsx
11. PatientSummary.jsx

---

## What to Avoid
- Do not put permission logic in the frontend
- Do not omit fields from the raw summary — always include them with None if no record exists
- Do not skip the audit log write — every access must be logged
- Do not add free-text clinical notes to the summary layer — structured fields only
- Do not allow HIDDEN fields to surface for non-GP roles, even with a reason label