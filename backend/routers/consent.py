import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import AuditLog, Patient, PatientConsent
from permissions import CATEGORY_LABELS

router = APIRouter()

SENSITIVE_CATEGORIES = ["mental_health", "substance_use", "sexual_health"]


@router.get("/patients/{patient_id}/consent")
def get_consent(patient_id: int, db: Session = Depends(get_db)):
    """Returns the patient's current consent settings for all sensitive categories."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    consents = db.query(PatientConsent).filter(PatientConsent.patient_id == patient_id).all()
    consent_map = {c.category: c.opted_out for c in consents}

    return {
        "patient_id": patient_id,
        "name": patient.name,
        "consent": [
            {
                "category": cat,
                "label": CATEGORY_LABELS[cat],
                "opted_out": consent_map.get(cat, False),
            }
            for cat in SENSITIVE_CATEGORIES
        ]
    }


class ConsentUpdate(BaseModel):
    category: str
    opted_out: bool


@router.patch("/patients/{patient_id}/consent")
def update_consent(patient_id: int, body: ConsentUpdate, db: Session = Depends(get_db)):
    """
    Toggles a patient's opt-out status for a sensitive category.
    Logs the change to the AuditLog.
    """
    if body.category not in SENSITIVE_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"'{body.category}' is not a sensitive category")

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    consent = (
        db.query(PatientConsent)
        .filter(PatientConsent.patient_id == patient_id, PatientConsent.category == body.category)
        .first()
    )

    if consent:
        consent.opted_out = body.opted_out
    else:
        consent = PatientConsent(patient_id=patient_id, category=body.category, opted_out=body.opted_out)
        db.add(consent)

    # Log the consent change to the audit log
    action = "opted_out" if body.opted_out else "opted_in"
    db.add(AuditLog(
        patient_id=patient_id,
        practitioner_id=None,  # null for patient-initiated actions
        practitioner_role="PATIENT",
        fields_accessed=json.dumps(["Patient Consent Settings", action]),
        timestamp=datetime.now(timezone.utc),
    ))

    db.commit()

    return {
        "patient_id": patient_id,
        "category": body.category,
        "label": CATEGORY_LABELS[body.category],
        "opted_out": body.opted_out,
        "action": action,
    }
