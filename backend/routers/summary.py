import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AuditLog, Consultation, Patient, PatientConsent, PractitionerVisibilityControl, SummaryField
from permissions import CATEGORY_ORDER, ROLE_DEFAULTS, filter_summary

router = APIRouter()


# Categories where practitioner visibility controls are ignored — the value is
# always included in the summary regardless of allow_summary setting.
ALWAYS_VISIBLE_CATEGORIES = {"medications", "allergies"}


def build_raw_summary(patient_id: int, db: Session) -> dict:
    """
    Collect all SummaryFields for a patient into a dict keyed by category.
    Each category maps to a list of entries ordered oldest-first, or None if
    no data exists at all (no_record).

    Each entry is one of:
      {value, date, practitioner_name, practitioner_role}  — visible entry
      {restricted: True, date, practitioner_name, practitioner_role}  — placeholder
        shown when the practitioner has set allow_summary=False

    Medications bypass practitioner restriction and always show the full value.
    """
    all_categories = CATEGORY_ORDER

    consultations = (
        db.query(Consultation)
        .filter(Consultation.patient_id == patient_id)
        .order_by(Consultation.date.asc())
        .all()
    )

    raw: dict[str, list | None] = {cat: None for cat in all_categories}

    for consultation in consultations:
        visibility = (
            db.query(PractitionerVisibilityControl)
            .filter(PractitionerVisibilityControl.consultation_id == consultation.id)
            .first()
        )
        allow = visibility.allow_summary if visibility else True

        fields = (
            db.query(SummaryField)
            .filter(SummaryField.consultation_id == consultation.id)
            .all()
        )
        for field in fields:
            if raw[field.category] is None:
                raw[field.category] = []

            entry_base = {
                "date": consultation.date,
                "practitioner_name": consultation.practitioner.name,
                "practitioner_role": consultation.practitioner.role,
            }

            if consultation.is_manual:
                # Always-visible categories (medications, allergies) bypass the toggle
                # for manual notes just as they do for seeded ones.
                if field.category in ALWAYS_VISIBLE_CATEGORIES:
                    raw[field.category].append({**entry_base, "value": field.value})
                # For other manually entered notes the toggle meaning is inverted:
                # OFF (allow=False) = full raw note is visible.
                # ON  (allow=True)  = placeholder shown in place of a real summary.
                elif allow:
                    raw[field.category].append({**entry_base, "value": "Summarized practitioner notes would be shown here"})
                else:
                    raw[field.category].append({**entry_base, "value": field.value})
            else:
                always_visible = field.category in ALWAYS_VISIBLE_CATEGORIES
                if allow or always_visible:
                    raw[field.category].append({**entry_base, "value": field.value})
                else:
                    # Practitioner has restricted this consultation — include a
                    # placeholder so the viewer knows a note exists but is withheld.
                    raw[field.category].append({**entry_base, "restricted": True})

    return raw


@router.get("/summary/{patient_id}")
def get_summary(patient_id: int, role: str, practitioner_id: int, db: Session = Depends(get_db)):
    """
    Return a filtered patient summary for the given role.

    Query params:
      role            — practitioner role (GP, PHYSIO, DIETITIAN, PSYCHOLOGIST)
      practitioner_id — used for the audit log
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    role = role.upper()
    if role not in ROLE_DEFAULTS:
        raise HTTPException(status_code=400, detail=f"Unknown role: {role}")

    # Collect patient consent opt-outs
    consents = db.query(PatientConsent).filter(PatientConsent.patient_id == patient_id).all()
    opted_out = {c.category for c in consents if c.opted_out}

    # Build raw summary
    raw_summary = build_raw_summary(patient_id, db)

    # Apply permission logic
    filtered = filter_summary(
        raw_summary=raw_summary,
        role=role,
        opted_out_categories=opted_out,
    )

    # Write audit log
    db.add(AuditLog(
        patient_id=patient_id,
        practitioner_id=practitioner_id,
        practitioner_role=role,
        fields_accessed=json.dumps(["Summary", "viewed"]),
        timestamp=datetime.now(timezone.utc),
    ))
    db.commit()

    return {
        "patient": {"id": patient.id, "name": patient.name, "date_of_birth": patient.date_of_birth},
        "role": role,
        "summary": filtered,
    }
