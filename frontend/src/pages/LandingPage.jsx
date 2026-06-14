import { ArrowRight, AudioWaveform, BrainCircuit, LockKeyhole, Upload } from "lucide-react";
import React from "react";
import AudioAnalyzer from "../components/AudioAnalyzer.jsx";
import Button from "../components/Button.jsx";

const features = [
  ["Multimodal audio intake", "Upload recordings or capture browser audio with the same analysis pipeline.", Upload],
  ["CNN spectrogram classifier", "Transforms speech, crying, and distress sounds into model-ready visual features.", BrainCircuit],
  ["Privacy-first triage", "Separates product workflows from protected storage and audit logging.", LockKeyhole]
];

export default function LandingPage({ goTo, setResult }) {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">AI-powered emotional distress detection</span>
          <h1>CrySense turns urgent audio signals into explainable distress insights.</h1>
          <p>
            A healthcare AI SaaS prototype for analyzing crying, panic sounds, emotional speech,
            and distress recordings with clear risk scoring and production-ready architecture.
          </p>
          <div className="button-row">
            <Button onClick={() => goTo("analyze")}>Start analysis <ArrowRight size={18} /></Button>
            <Button variant="secondary" onClick={() => goTo("docs")}>View architecture</Button>
          </div>
        </div>
        <div className="hero-visual" aria-label="CrySense live workflow preview">
          <div className="wave-card">
            <AudioWaveform size={44} />
            <div className="wave-bars">
              {Array.from({ length: 22 }).map((_, index) => <span key={index} style={{ "--i": index }} />)}
            </div>
            <strong>Distress score: 72</strong>
            <p>Confidence 91% · Risk elevated</p>
          </div>
        </div>
      </section>

      <AudioAnalyzer setResult={setResult} goTo={goTo} />

      <section className="section">
        <div className="section-heading">
          <span className="eyebrow">Platform capabilities</span>
          <h2>Built like a funded healthcare AI product</h2>
        </div>
        <div className="feature-grid">
          {features.map(([title, copy, Icon]) => (
            <article className="feature-card" key={title}>
              <Icon size={24} />
              <h3>{title}</h3>
              <p>{copy}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="workflow">
        {["Collect", "Clean", "Extract", "Train", "Deploy"].map((step, index) => (
          <div key={step}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <strong>{step}</strong>
          </div>
        ))}
      </section>

      <section className="testimonials">
        <blockquote>“CrySense makes model output understandable enough for product, clinical, and engineering teams to discuss the same risk signal.”</blockquote>
        <blockquote>“The workflow feels like a real triage console, not a classroom demo.”</blockquote>
      </section>
    </>
  );
}
