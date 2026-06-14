import React from "react";

export default function DocumentationPage() {
  return (
    <section className="content-page wide">
      <span className="eyebrow">Documentation</span>
      <h1>System architecture</h1>
      <div className="docs-grid">
        {[
          ["Frontend", "React, Vite, componentized analysis workflows, responsive healthcare SaaS UI."],
          ["Backend", "FastAPI routes for upload, record, analyze, health, and model metadata."],
          ["ML pipeline", "Librosa preprocessing, spectrogram generation, CNN training, evaluation, inference."],
          ["Data", "PostgreSQL entities for users, audio files, predictions, feedback, and system logs."],
          ["Deployment", "Vercel frontend, Railway or Render backend, cloud object storage, GitHub Actions CI."]
        ].map(([title, copy]) => (
          <article className="feature-card" key={title}>
            <h3>{title}</h3>
            <p>{copy}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
