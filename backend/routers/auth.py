import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import AuditLog, Consultation, Patient, Practitioner, PractitionerVisibilityControl
from permissions import ROLE_DEFAULTS

router = APIRouter()


@router.get("/patients")
def list_patients(db: Session = Depends(get_db)):
    """Returns all patients in the database for use in the patient switcher."""
    patients = db.query(Patient).all()
    return [{"id": p.id, "name": p.name} for p in patients]


@router.get("/auth/session")
def get_session(role: str, db: Session = Depends(get_db)):
    """
    Simulated auth — accepts a role param and returns a mock session context.
    Returns the first practitioner in the database matching the given role.

    In a real system this would validate a JWT and return the authenticated user.
    """
    role = role.upper()
    if role not in ROLE_DEFAULTS:
        raise HTTPException(status_code=400, detail=f"Unknown role: {role}")

    practitioner = db.query(Practitioner).filter(Practitioner.role == role).first()
    if not practitioner:
        raise HTTPException(status_code=404, detail=f"No practitioner found for role: {role}")

    return {
        "practitioner_id": practitioner.id,
        "name": practitioner.name,
        "role": practitioner.role,
    }


@router.get("/practitioners")
def list_practitioners(patient_id: int, db: Session = Depends(get_db)):
    """Returns all practitioners with their allow_summary status for a specific patient's consultations."""
    practitioners = db.query(Practitioner).all()
    result = []
    for p in practitioners:
        consultations = (
            db.query(Consultation)
            .filter(Consultation.practitioner_id == p.id, Consultation.patient_id == patient_id)
            .all()
        )
        controls = []
        for c in consultations:
            visibility = (
                db.query(PractitionerVisibilityControl)
                .filter(PractitionerVisibilityControl.consultation_id == c.id)
                .first()
            )
            controls.append({
                "consultation_id": c.id,
                "date": c.date,
                "allow_summary": visibility.allow_summary if visibility else False,
            })
        result.append({
            "id": p.id,
            "name": p.name,
            "role": p.role,
            "consultations": controls,
        })
    return result


class VisibilityUpdate(BaseModel):
    consultation_id: int
    allow_summary: bool


@router.patch("/practitioners/{practitioner_id}/visibility")
def update_visibility(practitioner_id: int, body: VisibilityUpdate, db: Session = Depends(get_db)):
    """Toggles a practitioner's allow_summary flag for a specific consultation."""
    practitioner = db.query(Practitioner).filter(Practitioner.id == practitioner_id).first()
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")

    visibility = (
        db.query(PractitionerVisibilityControl)
        .filter(PractitionerVisibilityControl.consultation_id == body.consultation_id)
        .first()
    )
    if not visibility:
        raise HTTPException(status_code=404, detail="No visibility control found for this consultation")

    visibility.allow_summary = body.allow_summary

    action = "opted_in" if body.allow_summary else "opted_out"
    consultation = db.query(Consultation).filter(Consultation.id == body.consultation_id).first()
    db.add(AuditLog(
        patient_id=consultation.patient_id,
        practitioner_id=practitioner_id,
        practitioner_role=practitioner.role,
        fields_accessed=json.dumps(["Practitioner Consent Settings", action]),
        timestamp=datetime.now(timezone.utc),
    ))
    db.commit()

    return {
        "practitioner_id": practitioner_id,
        "consultation_id": body.consultation_id,
        "allow_summary": body.allow_summary,
    }
