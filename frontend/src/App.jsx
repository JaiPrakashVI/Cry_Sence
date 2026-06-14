import React, { useMemo, useState } from "react";
import { Brain, FileAudio, Home, Info, LayoutDashboard, Mail, ScrollText } from "lucide-react";
import Shell from "./layouts/Shell.jsx";
import LandingPage from "./pages/LandingPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import AnalyzePage from "./pages/AnalyzePage.jsx";
import ResultsPage from "./pages/ResultsPage.jsx";
import AboutPage from "./pages/AboutPage.jsx";
import ContactPage from "./pages/ContactPage.jsx";
import DocumentationPage from "./pages/DocumentationPage.jsx";

export const navItems = [
  { id: "home", label: "Home", icon: Home },
  { id: "dashboard", label: "Overview", icon: LayoutDashboard },
  { id: "analyze", label: "Cry Analyzer", icon: FileAudio },
  { id: "results", label: "Latest Results", icon: Brain },
  { id: "about", label: "About", icon: Info },
  { id: "contact", label: "Support", icon: Mail }
];

const defaultResult = {
  distressScore: 65,
  confidenceScore: 88,
  emotion: "Hunger",
  riskCategory: "Elevated",
  summary: "The model identified rhythmic high-frequency patterns and acoustic envelope modulations consistent with hunger-induced crying.",
  timestamp: new Date().toISOString(),
  audioDetails: {
    filename: "demo-audio.webm",
    content_type: "audio/webm",
    duration_seconds: 5,
    sample_rate: 22050,
    channels: 1
  },
  emotion_distribution: {
    Hunger: 88,
    Discomfort: 8,
    Pain: 3,
    Sleepy: 1,
    Neutral: 0
  }
};

export default function App() {
  const [activePage, setActivePage] = useState("home");
  const [analysisResult, setAnalysisResult] = useState(defaultResult);

  const page = useMemo(() => {
    const shared = { goTo: setActivePage, result: analysisResult, setResult: setAnalysisResult };

    return {
      home: <LandingPage {...shared} />,
      dashboard: <DashboardPage {...shared} />,
      analyze: <AnalyzePage {...shared} />,
      results: <ResultsPage {...shared} />,
      about: <AboutPage {...shared} />,
      docs: <DocumentationPage {...shared} />,
      contact: <ContactPage {...shared} />
    }[activePage];
  }, [activePage, analysisResult]);

  return (
    <Shell activePage={activePage} setActivePage={setActivePage}>
      {page}
    </Shell>
  );
}
