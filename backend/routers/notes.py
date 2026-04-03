from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Consultation, PractitionerVisibilityControl, SummaryField

router = APIRouter()


class NoteSubmission(BaseModel):
    consultation_id: int
    category: str
    note: str


@router.post("/notes")
def submit_note(body: NoteSubmission, db: Session = Depends(get_db)):
    """
    Simulates a practitioner submitting a clinical note.

    If the consultation's PractitionerVisibilityControl has allow_summary=True,
    the note is written as a SummaryField and will appear in future summary requests.

    If allow_summary=False, the note is accepted but not summarised.
    """
    consultation = db.query(Consultation).filter(Consultation.id == body.consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    visibility = (
        db.query(PractitionerVisibilityControl)
        .filter(PractitionerVisibilityControl.consultation_id == body.consultation_id)
        .first()
    )
    allow_summary = visibility.allow_summary if visibility else True

    if allow_summary:
        db.add(SummaryField(
            consultation_id=body.consultation_id,
            category=body.category,
            value=body.note,
        ))
        db.commit()
        return {"summarised": True, "message": "Note accepted and added to patient summary."}

    return {"summarised": False, "message": "Note accepted but not summarised — practitioner has restricted sharing."}
