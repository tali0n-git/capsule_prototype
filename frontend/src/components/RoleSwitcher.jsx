const ROLES = ['GP', 'PHYSIO', 'DIETITIAN', 'PSYCHOLOGIST'];

const RoleSwitcher = ({ currentRole, onRoleChange }) => {
  return (
    <div className="role-switcher">
      <label htmlFor="role-select">Viewing as:</label>
      <select
        id="role-select"
        value={currentRole}
        onChange={(e) => onRoleChange(e.target.value)}
      >
        {ROLES.map((role) => (
          <option key={role} value={role}>{role}</option>
        ))}
      </select>
    </div>
  );
};

export default RoleSwitcher;
