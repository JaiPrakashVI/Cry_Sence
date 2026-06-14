import React from "react";

export default function AboutPage() {
  return (
    <section className="content-page">
      <span className="eyebrow">About CrySense</span>
      <h1>Clinical-grade thinking for emotional audio intelligence.</h1>
      <p>
        CrySense is designed as an AI decision-support platform. It does not replace clinicians or caregivers;
        it provides structured audio signals, confidence values, and risk categories that help teams respond faster.
      </p>
      <p>
        The architecture separates user experience, API validation, feature extraction, model inference, storage,
        observability, and feedback loops so the product can scale without turning into a fragile demo.
      </p>
    </section>
  );
}
