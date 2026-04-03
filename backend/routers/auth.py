from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Practitioner
from permissions import ROLE_DEFAULTS

router = APIRouter()


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
