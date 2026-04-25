import { useState, useEffect } from 'react';
import api from '../api.js';
import RoleSwitcher from '../components/RoleSwitcher';
import SummaryView from '../components/SummaryView';

const PatientSummary = ({ patientId, practitioner, practitioners, onPractitionerChange }) => {
  const [patient, setPatient] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!practitioner) return;
    let cancelled = false;

    const fetchSummary = async () => {
      try {
        setError(null);
        const response = await api.get(`/summary/${patientId}`, {
          params: { role: practitioner.role, practitioner_id: practitioner.id },
        });
        if (cancelled) return;
        setPatient(response.data.patient);
        setSummary(response.data.summary);
      } catch (err) {
        if (!cancelled) setError('Could not load patient summary.');
      }
    };

    fetchSummary();
    return () => { cancelled = true; };
  }, [practitioner, patientId]);

  return (
    <div className="patient-summary">
      <RoleSwitcher
        practitioners={practitioners}
        currentPractitioner={practitioner}
        onPractitionerChange={onPractitionerChange}
      />
      {error && <p className="error">{error}</p>}
      {patient && (
        <div className="patient-header">
          <h2>{patient.name}</h2>
          <p>DOB: {patient.date_of_birth}</p>
        </div>
      )}
      <SummaryView summary={summary} />
    </div>
  );
};

export default PatientSummary;
