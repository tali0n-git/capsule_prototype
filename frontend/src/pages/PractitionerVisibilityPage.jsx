import { useState, useEffect } from 'react';
import api from '../api.js';

const PractitionerVisibilityPage = ({ patientId, selectedId, onPractitionerChange }) => {
  const [practitioners, setPractitioners] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPractitioners = async () => {
      try {
        const response = await api.get('/practitioners', { params: { patient_id: patientId } });
        setPractitioners(response.data);
        if (response.data.length > 0 && !selectedId) onPractitionerChange(response.data[0].id);
      } catch (err) {
        setError('Could not load practitioners.');
      }
    };
    fetchPractitioners();
  }, [patientId]);

  const handleToggle = async (consultationId, currentValue) => {
    try {
      await api.patch(`/practitioners/${selectedId}/visibility`, {
        consultation_id: consultationId,
        allow_summary: !currentValue,
      });
      setPractitioners((prev) =>
        prev.map((p) =>
          p.id === selectedId
            ? {
                ...p,
                consultations: p.consultations.map((c) =>
                  c.consultation_id === consultationId
                    ? { ...c, allow_summary: !currentValue }
                    : c
                ),
              }
            : p
        )
      );
    } catch (err) {
      setError('Could not update visibility setting.');
    }
  };

  const selected = practitioners.find((p) => p.id === selectedId);

  return (
    <div className="consent-page">
      {error && <p className="error">{error}</p>}
      {practitioners.length > 0 && (
        <>
          <div className="patient-switcher">
            <label htmlFor="practitioner-select">Practitioner:</label>
            <select
              id="practitioner-select"
              value={selectedId}
              onChange={(e) => onPractitionerChange(Number(e.target.value))}
            >
              {practitioners.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} — {p.role} (ID: {p.id})
                </option>
              ))}
            </select>
          </div>
          {selected && (
            <>
              <div className="patient-header">
                <h2>{selected.name} (ID: {selected.id})</h2>
                <p>{selected.role} — Toggle whether each consultation's notes are included in the shared patient summary.</p>
              </div>
              <div className="summary-view">
                {selected.consultations.length === 0 && (
                  <p className="summary-empty" style={{ padding: '14px 16px' }}>No consultations found.</p>
                )}
                {selected.consultations.map((c) => (
                  <div key={c.consultation_id} className="field field--visible">
                    <span className="field__label">{c.date}</span>
                    <span className="field__value consent-toggle">
                      <label className="toggle">
                        <input
                          type="checkbox"
                          checked={c.allow_summary}
                          onChange={() => handleToggle(c.consultation_id, c.allow_summary)}
                        />
                        <span className="toggle__track" />
                        <span className="toggle__label">
                          {c.allow_summary ? 'Notes summarized' : 'Notes not summarized'}
                        </span>
                      </label>
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default PractitionerVisibilityPage;
