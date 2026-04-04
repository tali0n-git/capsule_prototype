import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import './App.css';
import api from './api.js';
import PatientSummary from './pages/PatientSummary';
import PatientConsentPage from './pages/PatientConsentPage';
import PractitionerVisibilityPage from './pages/PractitionerVisibilityPage';

const App = () => {
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState(null);

  useEffect(() => {
    const fetchPatients = async () => {
      const response = await api.get('/patients');
      setPatients(response.data);
      if (response.data.length > 0) setPatientId(response.data[0].id);
    };
    fetchPatients();
  }, []);

  return (
    <BrowserRouter>
      <div className="App">
        <header className="App-header">
          <h1>Capsule: Patient Summary</h1>
          <nav className="app-nav">
            <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link nav-link--active' : 'nav-link'}>
              Summary
            </NavLink>
            <NavLink to="/consent" className={({ isActive }) => isActive ? 'nav-link nav-link--active' : 'nav-link'}>
              Patient Consent Settings
            </NavLink>
            <NavLink to="/practitioner-visibility" className={({ isActive }) => isActive ? 'nav-link nav-link--active' : 'nav-link'}>
              Practitioner Notes
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
              <Route path="/" element={<PatientSummary patientId={patientId} />} />
              <Route path="/consent" element={<PatientConsentPage patientId={patientId} />} />
              <Route path="/practitioner-visibility" element={<PractitionerVisibilityPage patientId={patientId} />} />
            </Routes>
          )}
        </main>
      </div>
    </BrowserRouter>
  );
};

export default App;
