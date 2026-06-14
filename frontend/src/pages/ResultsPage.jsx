import React from "react";
import ResultPanel from "../components/ResultPanel.jsx";

export default function ResultsPage({ result }) {
  return (
    <section className="page-wrap">
      <ResultPanel result={result} />
    </section>
  );
}
