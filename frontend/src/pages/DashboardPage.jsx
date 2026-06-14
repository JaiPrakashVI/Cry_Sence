import { Clock, CheckCircle, HelpCircle, Heart, Star, Sparkles } from "lucide-react";
import React, { useEffect, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function DashboardPage() {
  const [engineReady, setEngineReady] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await fetch(`${API_BASE_URL}/health`).then(res => res.json()).catch(() => null);
        setEngineReady(!!res);
      } catch (e) {
        setEngineReady(false);
      } finally {
        setLoading(false);
      }
    }
    checkHealth();
  }, []);

  const recentLogs = [
    { time: "Today, 2:15 PM", state: "Hunger", confidence: "88%", distress: "Moderate (55%)", color: "var(--brand)" },
    { time: "Yesterday, 9:30 PM", state: "Sleepy", confidence: "75%", distress: "Low (22%)", color: "var(--accent)" },
    { time: "Yesterday, 3:45 PM", state: "Discomfort", confidence: "70%", distress: "Moderate (42%)", color: "var(--gold)" },
    { time: "June 12, 11:10 AM", state: "Pain", confidence: "92%", distress: "High (88%)", color: "var(--danger)" }
  ];

  return (
    <section className="page-wrap">
      <div className="section-heading align-left" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <span className="eyebrow">Insights Dashboard</span>
          <h1 style={{ marginBottom: "0.25rem" }}>Child Well-being & Cry Analytics</h1>
          <p style={{ margin: 0 }}>Review analysis history, distress patterns, and soothing protocols.</p>
        </div>
        <div>
          <span className="status-pill" style={{
            background: engineReady ? "rgba(16, 185, 129, 0.08)" : "rgba(245, 158, 11, 0.08)",
            color: engineReady ? "var(--accent)" : "var(--gold)",
            borderColor: engineReady ? "rgba(16, 185, 129, 0.2)" : "rgba(245, 158, 11, 0.2)"
          }}>
            <Sparkles size={13} style={{ marginRight: "4px", verticalAlign: "middle" }} />
            {loading ? "Initializing..." : engineReady ? "CrySense AI: Calibrated & Ready" : "CrySense AI: Standby Mode"}
          </span>
        </div>
      </div>

      <div className="dashboard-grid" style={{ marginTop: "1.5rem" }}>
        <article className="glass-card metric-card">
          <span>Total Cries Analyzed</span>
          <strong>18</strong>
          <div className="meter" style={{ height: "0.35rem" }}>
            <span style={{ width: "65%", backgroundColor: "var(--brand)" }} />
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.5rem", fontWeight: "600" }}>
            +4 recorded in the last 24 hours
          </div>
        </article>

        <article className="glass-card metric-card">
          <span>Primary Cry Need</span>
          <strong>Hunger</strong>
          <div className="meter" style={{ height: "0.35rem" }}>
            <span style={{ width: "64%", backgroundColor: "var(--brand-2)" }} />
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.5rem", fontWeight: "600" }}>
            Identified in 64% of weekly sessions
          </div>
        </article>

        <article className="glass-card metric-card">
          <span>Average Distress Level</span>
          <strong>Moderate</strong>
          <div className="meter" style={{ height: "0.35rem" }}>
            <span style={{ width: "42%", backgroundColor: "var(--gold)" }} />
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.5rem", fontWeight: "600" }}>
            Calculated weekly average: 42%
          </div>
        </article>
      </div>

      <div className="ops-grid" style={{ marginTop: "1.5rem", gridTemplateColumns: "1.2fr 0.8fr" }}>
        <div className="glass-card" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <span className="eyebrow">Recent Activity</span>
          <h2 style={{ fontSize: "1.25rem", color: "var(--ink)", margin: 0 }}>Vocal Analysis Logs</h2>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginTop: "0.5rem" }}>
            {recentLogs.map((log, idx) => (
              <div key={idx} style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "0.85rem 1rem",
                borderRadius: "0.75rem",
                background: "rgba(241, 245, 249, 0.4)",
                border: "1px solid #e2e8f0"
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <Clock size={16} style={{ color: "var(--muted)" }} />
                  <div>
                    <strong style={{ fontSize: "0.9rem", color: "var(--ink)", display: "block" }}>
                      Baby is displaying {log.state}
                    </strong>
                    <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>{log.time}</span>
                  </div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <span className="status-pill" style={{
                    fontSize: "0.7rem",
                    fontWeight: "800",
                    background: "white",
                    color: log.color,
                    borderColor: "rgba(0,0,0,0.05)"
                  }}>{log.confidence} Conf.</span>
                  <span style={{ display: "block", fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.2rem" }}>
                    Distress: {log.distress}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <span className="eyebrow">Soothing Protocols</span>
          <h2 style={{ fontSize: "1.25rem", color: "var(--ink)", margin: 0 }}>Expert Care Guides</h2>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.95rem", marginTop: "0.5rem", maxHeight: "17rem", overflowY: "auto", paddingRight: "0.25rem" }}>
            <div style={{ display: "flex", gap: "0.65rem", alignItems: "flex-start" }}>
              <Heart size={16} style={{ color: "var(--brand-2)", marginTop: "0.15rem", flexShrink: 0 }} />
              <div>
                <strong style={{ fontSize: "0.88rem", color: "#1e293b" }}>Hunger Soothing</strong>
                <p style={{ margin: "0.15rem 0 0 0", fontSize: "0.8rem", color: "var(--muted)", lineHeight: 1.55 }}>
                  Feed baby slowly. Rhythmic cries accompanied by sucking sounds indicate feeding readiness.
                </p>
              </div>
            </div>
            <div style={{ display: "flex", gap: "0.65rem", alignItems: "flex-start" }}>
              <Star size={16} style={{ color: "var(--gold)", marginTop: "0.15rem", flexShrink: 0 }} />
              <div>
                <strong style={{ fontSize: "0.88rem", color: "#1e293b" }}>Sleep Sleepiness</strong>
                <p style={{ margin: "0.15rem 0 0 0", fontSize: "0.8rem", color: "var(--muted)", lineHeight: 1.55 }}>
                  Dim the lights. Whimpering, yawns, and eye rubbing signal the sleep window is closing.
                </p>
              </div>
            </div>
            <div style={{ display: "flex", gap: "0.65rem", alignItems: "flex-start" }}>
              <HelpCircle size={16} style={{ color: "var(--brand)", marginTop: "0.15rem", flexShrink: 0 }} />
              <div>
                <strong style={{ fontSize: "0.88rem", color: "#1e293b" }}>Addressing Discomfort</strong>
                <p style={{ margin: "0.15rem 0 0 0", fontSize: "0.8rem", color: "var(--muted)", lineHeight: 1.55 }}>
                  Burp the baby or adjust room temperature. Grunting signals gas or clothing/diaper chafing.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
