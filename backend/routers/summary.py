import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AuditLog, Consultation, Patient, PatientConsent, PractitionerVisibilityControl, SummaryField
from permissions import ROLE_DEFAULTS, filter_summary

router = APIRouter()


def build_raw_summary(patient_id: int, db: Session) -> tuple[dict, set]:
    """
    Collect all SummaryFields for a patient into a flat dict keyed by category.
    Where multiple consultations have contributed to the same category, the most
    recent value is used.

    Also returns the set of categories where every contributing practitioner
    has set allow_summary=False (practitioner_restricted).
    """
    # All known categories across all roles
    all_categories = set()
    for role_map in ROLE_DEFAULTS.values():
        all_categories.update(role_map.keys())

    # Fetch all consultations for this patient, ordered oldest-first so later
    # entries overwrite earlier ones (most recent wins per category).
    consultations = (
        db.query(Consultation)
        .filter(Consultation.patient_id == patient_id)
        .order_by(Consultation.date.asc())
        .all()
    )

    raw: dict[str, str | None] = {cat: None for cat in all_categories}
    # Track which categories have been contributed by at least one practitioner
    # who has allow_summary=True
    category_has_allowed_source: dict[str, bool] = {cat: False for cat in all_categories}

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
            raw[field.category] = field.value
            if allow:
                category_has_allowed_source[field.category] = True

    # A category is practitioner_restricted if it has data but no allowed source
    practitioner_restricted = {
        cat for cat, value in raw.items()
        if value is not None and not category_has_allowed_source[cat]
    }

    return raw, practitioner_restricted


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

    # Build raw summary and determine practitioner-restricted categories
    raw_summary, practitioner_restricted = build_raw_summary(patient_id, db)

    # Apply permission logic
    filtered = filter_summary(
        raw_summary=raw_summary,
        role=role,
        opted_out_categories=opted_out,
        practitioner_restricted_categories=practitioner_restricted,
    )

    # Write audit log — log what was actually returned
    fields_accessed = [cat for cat, field in filtered.items() if field.get("visible")]
    db.add(AuditLog(
        patient_id=patient_id,
        practitioner_id=practitioner_id,
        practitioner_role=role,
        fields_accessed=json.dumps(fields_accessed),
        timestamp=datetime.now(timezone.utc),
    ))
    db.commit()

    return {
        "patient": {"id": patient.id, "name": patient.name, "date_of_birth": patient.date_of_birth},
        "role": role,
        "summary": filtered,
    }
