import React from "react";
import { percent } from "../utils/format.js";

export default function MetricCard({ label, value, tone = "blue" }) {
  return (
    <article className={`metric-card tone-${tone}`}>
      <span>{label}</span>
      <strong>{percent(value)}</strong>
      <div className="meter" aria-hidden="true">
        <span style={{ width: `${value}%` }} />
      </div>
    </article>
  );
}
