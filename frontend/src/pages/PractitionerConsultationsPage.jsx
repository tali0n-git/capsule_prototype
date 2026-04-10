import { useState, useEffect } from 'react';
import api from '../api.js';
import RoleSwitcher from '../components/RoleSwitcher';

// Categories each role has FULL (write) access to — mirrors ROLE_DEFAULTS in permissions.py
const ROLE_WRITABLE_CATEGORIES = {
  GP:           ['medications', 'allergies', 'mental_health', 'musculoskeletal', 'nutrition', 'substance_use', 'sexual_health'],
  PHYSIO:       ['medications', 'allergies', 'musculoskeletal'],
  DIETITIAN:    ['medications', 'allergies', 'nutrition'],
  PSYCHOLOGIST: ['medications', 'allergies', 'mental_health', 'substance_use'],
};

const CATEGORY_LABELS = {
  medications:     'Medications',
  allergies:       'Allergies',
  mental_health:   'Mental Health',
  musculoskeletal: 'Musculoskeletal',
  nutrition:       'Nutrition & Dietetics',
  substance_use:   'Substance Use',
  sexual_health:   'Sexual Health',
};

const PractitionerConsultationsPage = ({ patientId, practitioner, practitioners, onPractitionerChange }) => {
  const [notes, setNotes] = useState({});
  const [status, setStatus] = useState(null);

  // Clear notes when practitioner or patient changes
  useEffect(() => {
    setNotes({});
    setStatus(null);
  }, [practitioner?.id, patientId]);

  const writableCategories = ROLE_WRITABLE_CATEGORIES[practitioner?.role] || [];

  const handleChange = (category, value) => {
    setNotes(prev => ({ ...prev, [category]: value }));
  };

  const handleSubmit = async () => {
    const noteEntries = writableCategories
      .filter(cat => notes[cat] && notes[cat].trim())
      .map(cat => ({ category: cat, note: notes[cat].trim() }));

    if (noteEntries.length === 0) {
      setStatus({ type: 'error', message: 'Please enter at least one note before submitting.' });
      return;
    }

    try {
      await api.post('/notes', {
        patient_id: patientId,
        practitioner_id: practitioner.id,
        notes: noteEntries,
      });
      setNotes({});
      setStatus({ type: 'success', message: `${noteEntries.length} note(s) saved and will appear in the patient summary.` });
    } catch (err) {
      setStatus({ type: 'error', message: 'Could not save notes. Please try again.' });
    }
  };

  return (
    <div className="consent-page">
      <RoleSwitcher
        practitioners={practitioners}
        currentPractitioner={practitioner}
        onPractitionerChange={onPractitionerChange}
      />
      {practitioner && (
        <div className="patient-header">
          <h2>{practitioner.name}</h2>
          <p>Enter consultation notes below. Only filled fields will be saved. Notes appear in the patient summary immediately.</p>
        </div>
      )}
      <div className="summary-view">
        {writableCategories.map(category => (
          <div key={category} className="field field--visible">
            <span className="field__label">{CATEGORY_LABELS[category]}</span>
            <span className="field__value note-field">
              <textarea
                className="note-input"
                value={notes[category] || ''}
                onChange={e => handleChange(category, e.target.value)}
                placeholder={`Enter ${CATEGORY_LABELS[category].toLowerCase()} note...`}
                rows={3}
              />
            </span>
          </div>
        ))}
      </div>
      {status && (
        <p className={status.type === 'success' ? 'success-message' : 'error'}>
          {status.message}
        </p>
      )}
      <button className="submit-btn" onClick={handleSubmit}>
        Submit Notes
      </button>
    </div>
  );
};

export default PractitionerConsultationsPage;
