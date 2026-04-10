import { useState, useEffect } from 'react';
import api from '../api.js';
import RoleSwitcher from '../components/RoleSwitcher';
import SummaryView from '../components/SummaryView';

const PatientSummary = ({ patientId, role, onRoleChange }) => {
  const [patient, setPatient] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const fetchAll = async () => {
      try {
        setError(null);

        // Step 1: resolve the practitioner ID for the current role
        const sessionRes = await api.get('/auth/session', { params: { role } });
        if (cancelled) return;
        const practitionerId = sessionRes.data.practitioner_id;

        // Step 2: fetch the filtered summary
        const summaryRes = await api.get(`/summary/${patientId}`, {
          params: { role, practitioner_id: practitionerId },
        });
        if (cancelled) return;

        setPatient(summaryRes.data.patient);
        setSummary(summaryRes.data.summary);
      } catch (err) {
        if (!cancelled) setError('Could not load patient summary.');
      }
    };

    fetchAll();
    return () => { cancelled = true; };
  }, [role, patientId]);

  return (
    <div className="patient-summary">
      <RoleSwitcher currentRole={role} onRoleChange={onRoleChange} />
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
