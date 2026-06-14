import React from "react";
import AudioAnalyzer from "../components/AudioAnalyzer.jsx";

export default function AnalyzePage({ setResult, goTo }) {
  return (
    <section className="page-wrap">
      <div className="section-heading align-left">
        <span className="eyebrow">Audio analysis console</span>
        <h1>Upload or record audio for emotional distress inference.</h1>
      </div>
      <AudioAnalyzer setResult={setResult} goTo={goTo} />
    </section>
  );
}
