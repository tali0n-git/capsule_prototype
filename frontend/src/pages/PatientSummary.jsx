import { useState, useEffect } from 'react';
import api from '../api.js';
import RoleSwitcher from '../components/RoleSwitcher';
import SummaryView from '../components/SummaryView';

const PatientSummary = ({ patientId }) => {
  const [role, setRole] = useState('GP');
  const [practitionerId, setPractitionerId] = useState(null);
  const [patient, setPatient] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  // Fetch session (practitioner_id) whenever role changes
  useEffect(() => {
    const fetchSession = async () => {
      try {
        const response = await api.get('/auth/session', { params: { role } });
        setPractitionerId(response.data.practitioner_id);
      } catch (err) {
        setError(`Could not load session for role: ${role}`);
      }
    };
    fetchSession();
  }, [role]);

  // Fetch summary whenever practitioner_id is resolved or patient changes
  useEffect(() => {
    if (!practitionerId) return;
    const fetchSummary = async () => {
      try {
        setError(null);
        const response = await api.get(`/summary/${patientId}`, {
          params: { role, practitioner_id: practitionerId },
        });
        setPatient(response.data.patient);
        setSummary(response.data.summary);
      } catch (err) {
        setError('Could not load patient summary.');
      }
    };
    fetchSummary();
  }, [practitionerId, patientId]);

  return (
    <div className="patient-summary">
      <RoleSwitcher currentRole={role} onRoleChange={setRole} />
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
