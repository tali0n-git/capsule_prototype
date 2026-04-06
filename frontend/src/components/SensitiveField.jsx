const REASON_LABELS = {
  no_record: 'No record',
  role_restricted: 'Not available to your role — consult with patient if needed',
  patient_restricted: 'Patient has restricted access to this field',
  practitioner_restricted: 'Full practitioner notes would be shown here',
};

const SensitiveField = ({ field }) => {
  if (field.visible) {
    const entries = Array.isArray(field.value) ? field.value : null;

    const renderEntry = (entry, i) => {
      if (entry.restricted) {
        return (
          <li key={i} className="field__note field__note--restricted">
            <span className="field__note-date">{entry.date}</span>
            {" — "}
            <span className="field__reason">Full practitioner notes would be shown here</span>
          </li>
        );
      }
      return (
        <li key={i} className="field__note">
          <span className="field__note-date">{entry.date}</span>
          {" — "}
          <span>{entry.value}</span>
        </li>
      );
    };

    return (
      <div className="field field--visible">
        <span className="field__label">{field.label}</span>
        {entries ? (
          <ul className="field__notes-list">
            {entries.map(renderEntry)}
          </ul>
        ) : (
          <span className="field__value">{field.value}</span>
        )}
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
