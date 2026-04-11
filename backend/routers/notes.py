import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import AuditLog, Consultation, Patient, Practitioner, PractitionerVisibilityControl, SummaryField
from permissions import CATEGORY_ORDER, ROLE_DEFAULTS, AccessLevel

router = APIRouter()


class CategoryNote(BaseModel):
    category: str
    note: str


class NoteSubmission(BaseModel):
    patient_id: int
    practitioner_id: int
    notes: list[CategoryNote]


@router.post("/notes")
def submit_notes(body: NoteSubmission, db: Session = Depends(get_db)):
    """
    Create a new consultation for the given practitioner and patient, then save
    the provided notes as SummaryFields. Logs the write to AuditLog.

    Only categories where the practitioner's role has FULL access are accepted.
    A PractitionerVisibilityControl is created defaulting to allow_summary=True.
    """
    if not body.notes:
        raise HTTPException(status_code=400, detail="No notes provided")

    practitioner = db.query(Practitioner).filter(Practitioner.id == body.practitioner_id).first()
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")

    patient = db.query(Patient).filter(Patient.id == body.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    role_defaults = ROLE_DEFAULTS.get(practitioner.role, {})

    for entry in body.notes:
        if entry.category not in CATEGORY_ORDER:
            raise HTTPException(status_code=400, detail=f"Unknown category: {entry.category}")
        if role_defaults.get(entry.category) != AccessLevel.FULL:
            raise HTTPException(
                status_code=403,
                detail=f"Role {practitioner.role} does not have write access to: {entry.category}",
            )

    today = datetime.now().strftime("%Y-%m-%d")
    consultation = Consultation(
        patient_id=body.patient_id,
        practitioner_id=body.practitioner_id,
        date=today,
        is_manual=True,
    )
    db.add(consultation)
    db.flush()

    categories_written = []
    for entry in body.notes:
        db.add(SummaryField(
            consultation_id=consultation.id,
            category=entry.category,
            value=entry.note,
        ))
        categories_written.append(entry.category)

    # Manual notes are raw full notes — default to not shared until the practitioner
    # explicitly enables sharing via the Practitioner Consent Settings toggle.
    db.add(PractitionerVisibilityControl(
        practitioner_id=body.practitioner_id,
        consultation_id=consultation.id,
        allow_summary=False,
    ))

    db.add(AuditLog(
        patient_id=body.patient_id,
        practitioner_id=body.practitioner_id,
        practitioner_role=practitioner.role,
        fields_accessed=json.dumps(["Add Practitioners' Notes", "submitted"]),
        timestamp=datetime.now(timezone.utc),
    ))

    db.commit()

    return {
        "consultation_id": consultation.id,
        "categories": categories_written,
        "message": "Notes saved. Sharing is off by default — enable it in Practitioner Consent Settings.",
    }
