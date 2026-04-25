import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import './App.css';
import api from './api.js';
import PatientSummary from './pages/PatientSummary';
import PatientConsentPage from './pages/PatientConsentPage';
import PractitionerVisibilityPage from './pages/PractitionerVisibilityPage';
import PractitionerConsultationsPage from './pages/PractitionerConsultationsPage';

const App = () => {
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState(null);
  const [practitioners, setPractitioners] = useState([]);
  const [viewingPractitioner, setViewingPractitioner] = useState(null); // {id, name, role}
  const [consentPractitionerId, setConsentPractitionerId] = useState(null);

  useEffect(() => {
    const fetchPatients = async () => {
      const response = await api.get('/patients');
      setPatients(response.data);
      if (response.data.length > 0) setPatientId(response.data[0].id);
    };
    fetchPatients();
  }, []);

  // Fetch practitioners whenever the selected patient changes
  useEffect(() => {
    if (!patientId) return;
    const fetchPractitioners = async () => {
      const response = await api.get('/practitioners', { params: { patient_id: patientId } });
      setPractitioners(response.data);
      if (response.data.length > 0) {
        setViewingPractitioner(p => p ?? response.data[0]);
        setConsentPractitionerId(id => id ?? response.data[0].id);
      }
    };
    fetchPractitioners();
  }, [patientId]);

  return (
    <BrowserRouter>
      <div className="App">
        <header className="App-header">
          <h1>Capsule: Patient Summary</h1>
          <nav className="app-nav">
            <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link nav-link--active' : 'nav-link'}>
              Summary
            </NavLink>
            <NavLink to="/consultations" className={({ isActive }) => isActive ? 'nav-link nav-link--active' : 'nav-link'}>
              Add Practitioners' Notes
            </NavLink>
            <NavLink to="/practitioner-visibility" className={({ isActive }) => isActive ? 'nav-link nav-link--active' : 'nav-link'}>
              Practitioner Consent Settings
            </NavLink>
            <NavLink to="/consent" className={({ isActive }) => isActive ? 'nav-link nav-link--active' : 'nav-link'}>
              Patient Consent Settings
            </NavLink>
          </nav>
        </header>
        <main>
          {patients.length > 0 && (
            <div className="patient-switcher">
              <label htmlFor="patient-select">Patient:</label>
              <select
                id="patient-select"
                value={patientId}
                onChange={(e) => setPatientId(Number(e.target.value))}
              >
                {patients.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
          )}
          {patientId && (
            <Routes>
              <Route path="/" element={
                <PatientSummary
                  patientId={patientId}
                  practitioner={viewingPractitioner}
                  practitioners={practitioners}
                  onPractitionerChange={setViewingPractitioner}
                />}
              />
              <Route path="/consent" element={<PatientConsentPage patientId={patientId} />} />
              <Route path="/practitioner-visibility" element={
                <PractitionerVisibilityPage
                  patientId={patientId}
                  selectedId={consentPractitionerId}
                  onPractitionerChange={setConsentPractitionerId}
                />}
              />
              <Route path="/consultations" element={
                <PractitionerConsultationsPage
                  patientId={patientId}
                  practitioner={viewingPractitioner}
                  practitioners={practitioners}
                  onPractitionerChange={setViewingPractitioner}
                />}
              />
            </Routes>
          )}
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
