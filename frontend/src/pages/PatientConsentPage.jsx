import { useState, useEffect } from 'react';
import api from '../api.js';

const PatientConsentPage = ({ patientId }) => {
  const [consentData, setConsentData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchConsent = async () => {
      try {
        const response = await api.get(`/patients/${patientId}/consent`);
        setConsentData(response.data);
      } catch (err) {
        setError('Could not load consent settings.');
      }
    };
    fetchConsent();
  }, [patientId]);

  const handleToggle = async (category, currentOptedOut) => {
    try {
      const response = await api.patch(`/patients/${patientId}/consent`, {
        category,
        opted_out: !currentOptedOut,
      });
      setConsentData((prev) => ({
        ...prev,
        consent: prev.consent.map((c) =>
          c.category === category ? { ...c, opted_out: response.data.opted_out } : c
        ),
      }));
    } catch (err) {
      setError('Could not update consent setting.');
    }
  };

  return (
    <div className="consent-page">
      {error && <p className="error">{error}</p>}
      {consentData && (
        <>
          <div className="patient-header">
            <h2>{consentData.name}</h2>
            <p>Manage which sensitive categories are shared with your care team.</p>
          </div>
          <div className="summary-view">
            {consentData.consent.map(({ category, label, opted_out }) => (
              <div key={category} className="field field--visible">
                <span className="field__label">{label}</span>
                <span className="field__value consent-toggle">
                  <label className="toggle">
                    <input
                      type="checkbox"
                      checked={!opted_out}
                      onChange={() => handleToggle(category, opted_out)}
                    />
                    <span className="toggle__track" />
                    <span className="toggle__label">
                      {opted_out ? 'Restricted' : 'Shared'}
                    </span>
                  </label>
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default PatientConsentPage;
