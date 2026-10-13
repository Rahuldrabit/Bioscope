import type { components } from "@/shared/api/generated/schema";

type ReliabilityReport = components["schemas"]["ReliabilityReportResponse"];

export function ReliabilityPanel({ report }: { report: ReliabilityReport }) {
  return (
    <section aria-label="Reliability assessment" className="reliability-panel">
      <p className="eyebrow">Reliability status</p>
      <h3>Transparent evidence limits</h3>
      <dl>
        {Object.entries(report.dimensions).map(([key, value]) => (
          <div key={key}>
            <dt>{key.replaceAll("_", " ")}</dt>
            <dd>{value.replaceAll("_", " ")}</dd>
          </div>
        ))}
      </dl>
      <p>No numeric probability is shown because no calibrated estimator is enabled.</p>
      <ul>
        {report.critical_gaps.map((gap) => <li key={gap}>{gap}</li>)}
      </ul>
      <small>{report.disclaimer}</small>
    </section>
  );
}
