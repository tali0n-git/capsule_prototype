from database import engine, SessionLocal, Base
from models import (
    Patient, Practitioner, Consultation, SummaryField,
    PatientConsent, PractitionerVisibilityControl
)

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()

    try:
        # --- Practitioners ---
        gp = Practitioner(name="Dr. Sarah Nguyen", role="GP")
        physio = Practitioner(name="James Okafor", role="PHYSIO")
        dietitian = Practitioner(name="Rachel Kim", role="DIETITIAN")
        psychologist = Practitioner(name="Dr. Tom Ellis", role="PSYCHOLOGIST")
        db.add_all([gp, physio, dietitian, psychologist])
        db.flush()

        # --- Patient 1: Robert Marsh, 65-yr old male ---
        # Mental health history, musculoskeletal issue, dietary condition
        robert = Patient(name="Robert Marsh", date_of_birth="1960-03-14")
        db.add(robert)
        db.flush()

        # GP consultation — medications and general history
        consult_r_gp = Consultation(patient_id=robert.id, practitioner_id=gp.id, date="2025-11-10")
        db.add(consult_r_gp)
        db.flush()
        db.add_all([
            SummaryField(consultation_id=consult_r_gp.id, category="medications",
                         value="Sertraline 100mg daily, Atorvastatin 20mg nightly, Metformin 500mg twice daily"),
            SummaryField(consultation_id=consult_r_gp.id, category="allergies",
                         value="Penicillin — anaphylaxis"),
        ])
        db.add(PractitionerVisibilityControl(
            practitioner_id=gp.id, consultation_id=consult_r_gp.id, allow_summary=True
        ))

        # Psychologist consultation — mental health
        consult_r_psych = Consultation(patient_id=robert.id, practitioner_id=psychologist.id, date="2025-10-22")
        db.add(consult_r_psych)
        db.flush()
        db.add_all([
            SummaryField(consultation_id=consult_r_psych.id, category="mental_health",
                         value="Recurrent major depressive disorder, currently stable on Sertraline. "
                               "History of one inpatient episode in 2019. Engaging in fortnightly CBT."),
        ])
        db.add(PractitionerVisibilityControl(
            practitioner_id=psychologist.id, consultation_id=consult_r_psych.id, allow_summary=True
        ))

        # Physio consultation — musculoskeletal
        consult_r_physio = Consultation(patient_id=robert.id, practitioner_id=physio.id, date="2025-12-01")
        db.add(consult_r_physio)
        db.flush()
        db.add_all([
            SummaryField(consultation_id=consult_r_physio.id, category="musculoskeletal",
                         value="Chronic lower back pain secondary to L4/L5 disc degeneration. "
                               "Currently on a 6-week progressive loading program. Avoiding heavy lifting."),
        ])
        db.add(PractitionerVisibilityControl(
            practitioner_id=physio.id, consultation_id=consult_r_physio.id, allow_summary=True
        ))

        # Dietitian consultation — dietary
        consult_r_diet = Consultation(patient_id=robert.id, practitioner_id=dietitian.id, date="2025-11-28")
        db.add(consult_r_diet)
        db.flush()
        db.add_all([
            SummaryField(consultation_id=consult_r_diet.id, category="nutrition",
                         value="Type 2 diabetes, managed with diet and Metformin. "
                               "Low-GI diet plan in place. HbA1c trending down at last review (52 mmol/mol)."),
        ])
        db.add(PractitionerVisibilityControl(
            practitioner_id=dietitian.id, consultation_id=consult_r_diet.id, allow_summary=True
        ))

        # Robert's consent — no opt-outs
        db.add_all([
            PatientConsent(patient_id=robert.id, category="mental_health", opted_out=False),
            PatientConsent(patient_id=robert.id, category="substance_use", opted_out=False),
            PatientConsent(patient_id=robert.id, category="sexual_health", opted_out=False),
        ])

        # --- Patient 2: Maya Patel, 25-yr old female ---
        # Musculoskeletal issue, dietary condition, no mental health history
        maya = Patient(name="Maya Patel", date_of_birth="2000-07-30")
        db.add(maya)
        db.flush()

        # GP consultation — medications
        consult_m_gp = Consultation(patient_id=maya.id, practitioner_id=gp.id, date="2026-01-15")
        db.add(consult_m_gp)
        db.flush()
        db.add_all([
            SummaryField(consultation_id=consult_m_gp.id, category="medications",
                         value="Ibuprofen 400mg as needed (short course), Vitamin D 1000 IU daily"),
            SummaryField(consultation_id=consult_m_gp.id, category="allergies",
                         value="None known"),
        ])
        db.add(PractitionerVisibilityControl(
            practitioner_id=gp.id, consultation_id=consult_m_gp.id, allow_summary=True
        ))

        # Physio consultation — musculoskeletal
        consult_m_physio = Consultation(patient_id=maya.id, practitioner_id=physio.id, date="2026-01-20")
        db.add(consult_m_physio)
        db.flush()
        db.add_all([
            SummaryField(consultation_id=consult_m_physio.id, category="musculoskeletal",
                         value="Patellofemoral pain syndrome, right knee. Onset after increased running volume. "
                               "Quadriceps strengthening program commenced, activity modification advised."),
        ])
        db.add(PractitionerVisibilityControl(
            practitioner_id=physio.id, consultation_id=consult_m_physio.id, allow_summary=True
        ))

        # Dietitian consultation — dietary
        consult_m_diet = Consultation(patient_id=maya.id, practitioner_id=dietitian.id, date="2026-01-22")
        db.add(consult_m_diet)
        db.flush()
        db.add_all([
            SummaryField(consultation_id=consult_m_diet.id, category="nutrition",
                         value="Iron deficiency anaemia confirmed on bloods. Dietary iron intake low. "
                               "Increasing red meat and legume intake recommended. Oral iron supplement trialled "
                               "previously — poorly tolerated. Dietary-first approach agreed."),
        ])
        db.add(PractitionerVisibilityControl(
            practitioner_id=dietitian.id, consultation_id=consult_m_diet.id, allow_summary=True
        ))

        # Maya's consent — opts out of mental_health sharing (no history, privacy preference)
        db.add_all([
            PatientConsent(patient_id=maya.id, category="mental_health", opted_out=True),
            PatientConsent(patient_id=maya.id, category="substance_use", opted_out=False),
            PatientConsent(patient_id=maya.id, category="sexual_health", opted_out=False),
        ])

        db.commit()
        print("Seeded successfully.")
        print(f"  Patients:      Robert Marsh (id={robert.id}), Maya Patel (id={maya.id})")
        print(f"  Practitioners: GP={gp.id}, Physio={physio.id}, Dietitian={dietitian.id}, Psychologist={psychologist.id}")

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
