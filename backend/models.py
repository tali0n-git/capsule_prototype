from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from database import Base


# --- SQLAlchemy Tables ---

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date_of_birth = Column(String, nullable=False)

    consultations = relationship("Consultation", back_populates="patient")
    consents = relationship("PatientConsent", back_populates="patient")


class Practitioner(Base):
    __tablename__ = "practitioners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # GP, PHYSIO, DIETITIAN, PSYCHOLOGIST

    consultations = relationship("Consultation", back_populates="practitioner")
    visibility_controls = relationship("PractitionerVisibilityControl", back_populates="practitioner")


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    practitioner_id = Column(Integer, ForeignKey("practitioners.id"), nullable=False)
    date = Column(String, nullable=False)

    patient = relationship("Patient", back_populates="consultations")
    practitioner = relationship("Practitioner", back_populates="consultations")
    summary_fields = relationship("SummaryField", back_populates="consultation")
    visibility_control = relationship("PractitionerVisibilityControl", back_populates="consultation", uselist=False)


class SummaryField(Base):
    __tablename__ = "summary_fields"

    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    category = Column(String, nullable=False)  # e.g. medications, mental_health, substance_use
    value = Column(Text, nullable=False)

    consultation = relationship("Consultation", back_populates="summary_fields")


class PatientConsent(Base):
    __tablename__ = "patient_consents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    category = Column(String, nullable=False)  # mental_health, substance_use, sexual_health
    opted_out = Column(Boolean, nullable=False, default=False)

    patient = relationship("Patient", back_populates="consents")


class PractitionerVisibilityControl(Base):
    __tablename__ = "practitioner_visibility_controls"

    id = Column(Integer, primary_key=True, index=True)
    practitioner_id = Column(Integer, ForeignKey("practitioners.id"), nullable=False)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    allow_summary = Column(Boolean, nullable=False, default=False)

    practitioner = relationship("Practitioner", back_populates="visibility_controls")
    consultation = relationship("Consultation", back_populates="visibility_control")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    practitioner_id = Column(Integer, ForeignKey("practitioners.id"), nullable=True)  # null for patient-initiated actions
    practitioner_role = Column(String, nullable=False)
    fields_accessed = Column(Text, nullable=False)  # JSON-encoded list of category names
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


# --- Pydantic Schemas ---

class SummaryFieldSchema(BaseModel):
    category: str
    value: str

    class Config:
        from_attributes = True


class PatientSchema(BaseModel):
    id: int
    name: str
    date_of_birth: str

    class Config:
        from_attributes = True


class PractitionerSchema(BaseModel):
    id: int
    name: str
    role: str

    class Config:
        from_attributes = True
