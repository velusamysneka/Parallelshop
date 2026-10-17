import type { SubstitutionFlow } from "../types";

export default function SubstitutionTable({ flows }: { flows: SubstitutionFlow[] }) {
  if (!flows.length) return <p className="muted">No substitutions - shoppers kept their usual products.</p>;

  return (
    <table className="flows">
      <thead>
        <tr><th>From</th><th /><th>To</th><th>Share of switchers</th></tr>
      </thead>
      <tbody>
        {flows.slice(0, 8).map((f) => (
          <tr key={`${f.source}->${f.target}`}>
            <td>{f.source}</td>
            <td className="arrow">→</td>
            <td>{f.target}</td>
            <td>
              <div className="bar-cell">
                <div className="bar" style={{ width: `${f.percentage}%` }} />
                <span>{f.percentage}% <small className="muted">({f.count})</small></span>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
