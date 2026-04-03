import { useState, useEffect } from 'react';
import './App.css';
import api from './api.js';
import PatientSummary from './pages/PatientSummary';

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
    <div className="App">
      <header className="App-header">
        <h1>Capsule: Patient Summary</h1>
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
        {patientId && <PatientSummary patientId={patientId} />}
      </main>
    </div>
  );
};

export default App;
