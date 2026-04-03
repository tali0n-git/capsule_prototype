import './App.css';
import PatientSummary from './pages/PatientSummary';

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Capsule: Patient Summary</h1>
      </header>
      <main>
        <PatientSummary patientId={1} />
      </main>
    </div>
  );
};

export default App;