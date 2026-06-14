import { AlertTriangle, CalendarClock, CheckCircle2, FileAudio, Gauge, ShieldAlert, Waves, Heart } from "lucide-react";
import React from "react";
import MetricCard from "./MetricCard.jsx";

export default function ResultPanel({ result }) {
  const distribution = result.emotion_distribution ?? result.emotionDistribution ?? {};
  const details = result.audioDetails ?? {};
  const timestamp = result.timestamp ? new Date(result.timestamp).toLocaleString() : new Date().toLocaleString();

  return (
    <section className="result-panel" aria-label="Latest analysis result">
      <div className="result-header">
        <div>
          <span className="eyebrow">Model output</span>
          <h2>{result.emotion} detected</h2>
        </div>
        <span className={`risk-badge ${result.riskCategory.toLowerCase()}`}>{result.riskCategory}</span>
      </div>

      <div className="metrics-grid">
        <MetricCard label="Distress score" value={result.distressScore} tone="rose" />
        <MetricCard label="Confidence" value={result.confidenceScore} tone="green" />
      </div>

      <div className="diagnostics-grid">
        <article className="diagnostic-card gauge-card">
          <span className="eyebrow">Confidence gauge</span>
          <div className="radial-gauge" style={{ "--score": `${result.confidenceScore}%` }}>
            <strong>{Math.round(result.confidenceScore)}%</strong>
          </div>
        </article>

        <article className="diagnostic-card">
          <span className="eyebrow">Emotion distribution</span>
          <div className="distribution-chart">
            {Object.entries(distribution).map(([label, value]) => (
              <div key={label}>
                <span>{label}</span>
                <div><i style={{ width: `${Math.min(value, 100)}%` }} /></div>
                <strong>{Math.round(value)}%</strong>
              </div>
            ))}
          </div>
        </article>
      </div>

      <div className="waveform-card">
        <div><Waves size={18} /> Audio waveform visualization</div>
        <div className="mini-waveform">
          {Array.from({ length: 42 }).map((_, index) => <span key={index} style={{ "--i": index }} />)}
        </div>
      </div>

      <div className="insight-list">
        <div className="insight-list-item">
          <Heart size={18} />
          <div>
            <strong>Respond promptly to baby's needs</strong>
            <p style={{ margin: "0.1rem 0 0 0", fontSize: "0.8rem", color: "var(--muted)" }}>Check the primary indicator and apply expert soothing techniques.</p>
          </div>
        </div>
        <div className="insight-list-item">
          <ShieldAlert size={18} />
          <div>
            <strong>Escalate if cry persists</strong>
            <p style={{ margin: "0.1rem 0 0 0", fontSize: "0.8rem", color: "var(--muted)" }}>Seek pediatrician advice if high-distress cries repeat or baby cannot be settled.</p>
          </div>
        </div>
        <div className="insight-list-item">
          <CheckCircle2 size={18} style={{ color: "var(--accent)" }} />
          <div>
            <strong>Track comfort changes</strong>
            <p style={{ margin: "0.1rem 0 0 0", fontSize: "0.8rem", color: "var(--muted)" }}>Compare distress scores over successive sessions to monitor baby's comfort level.</p>
          </div>
        </div>
      </div>

      <div className="audio-details" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
        <div><FileAudio size={18} /><span>Audio File</span><strong>{details.filename ?? "Recorded Audio"}</strong></div>
        <div><CalendarClock size={18} /><span>Recorded On</span><strong>{timestamp}</strong></div>
        <div><Gauge size={18} style={{ color: "var(--brand)" }} /><span>Duration</span><strong>{details.duration_seconds ? `${Number(details.duration_seconds).toFixed(1)} seconds` : "5.0 seconds"}</strong></div>
      </div>

      <div className="result-summary">
        <AlertTriangle size={18} />
        <div>
          <strong style={{ display: "block", fontSize: "0.82rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--ink)", marginBottom: "0.15rem" }}>Analysis Summary</strong>
          <p style={{ margin: 0, fontSize: "0.9rem", color: "var(--muted)" }}>{result.summary}</p>
        </div>
      </div>
    </section>
  );
}
