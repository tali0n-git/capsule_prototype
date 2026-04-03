const REASON_LABELS = {
  no_record: 'No record',
  role_restricted: 'Not available to your role',
  patient_restricted: 'Patient has restricted access to this field',
  practitioner_restricted: 'Practitioner has chosen not to share this field',
};

const SensitiveField = ({ field }) => {
  if (field.visible) {
    return (
      <div className="field field--visible">
        <span className="field__label">{field.label}</span>
        <span className="field__value">{field.value}</span>
      </div>
    );
  }

  return (
    <div className="field field--unavailable">
      <span className="field__label">{field.label}</span>
      <span className="field__reason">{REASON_LABELS[field.reason] ?? field.reason}</span>
    </div>
  );
};

export default SensitiveField;
