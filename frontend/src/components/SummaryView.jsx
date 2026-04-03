import SensitiveField from './SensitiveField';

const SummaryView = ({ summary }) => {
  if (!summary || Object.keys(summary).length === 0) {
    return <p className="summary-empty">No summary available.</p>;
  }

  return (
    <div className="summary-view">
      {Object.entries(summary).map(([category, field]) => (
        <SensitiveField key={category} field={field} />
      ))}
    </div>
  );
};

export default SummaryView;
