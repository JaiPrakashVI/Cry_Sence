import { Menu, ShieldCheck, X } from "lucide-react";
import React, { useState } from "react";
import { navItems } from "../App.jsx";

export default function Shell({ activePage, setActivePage, children }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const selectPage = (page) => {
    setActivePage(page);
    setMenuOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <button className="brand" onClick={() => selectPage("home")} aria-label="Go to home">
          <span className="brand-mark"><ShieldCheck size={20} /></span>
          <span>CrySense</span>
          <span className="status-pill">Clinical AI</span>
        </button>

        <nav className="desktop-nav" aria-label="Primary navigation">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={activePage === item.id ? "nav-link active" : "nav-link"}
              onClick={() => selectPage(item.id)}
            >
              <item.icon size={16} />
              {item.label}
            </button>
          ))}
        </nav>

        <button className="icon-button mobile-only" onClick={() => setMenuOpen((value) => !value)} aria-label="Open menu">
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </header>

      {menuOpen && (
        <nav className="mobile-nav" aria-label="Mobile navigation">
          {navItems.map((item) => (
            <button key={item.id} className="mobile-nav-link" onClick={() => selectPage(item.id)}>
              <item.icon size={18} />
              {item.label}
            </button>
          ))}
        </nav>
      )}

      <main>{children}</main>

      <footer className="footer">
        <div>
          <strong>CrySense</strong>
          <p>AI-assisted emotional distress detection for safer audio triage workflows.</p>
        </div>
        <div className="footer-links">
          <button onClick={() => selectPage("docs")}>Documentation</button>
          <button onClick={() => selectPage("contact")}>Contact</button>
          <button onClick={() => selectPage("about")}>Privacy</button>
        </div>
      </footer>
    </div>
  );
}
