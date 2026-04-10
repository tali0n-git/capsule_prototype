const RoleSwitcher = ({ practitioners, currentPractitioner, onPractitionerChange }) => {
  const handleChange = (e) => {
    const selected = practitioners.find((p) => p.id === Number(e.target.value));
    if (selected) onPractitionerChange(selected);
  };

  return (
    <div className="patient-switcher">
      <label htmlFor="role-select">Practitioner:</label>
      <select
        id="role-select"
        value={currentPractitioner?.id ?? ''}
        onChange={handleChange}
      >
        {practitioners.map((p) => (
          <option key={p.id} value={p.id}>{p.name} — {p.role}</option>
        ))}
      </select>
    </div>
  );
};

export default RoleSwitcher;
