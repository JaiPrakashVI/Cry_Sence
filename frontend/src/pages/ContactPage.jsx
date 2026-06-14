import React from "react";
import Button from "../components/Button.jsx";

export default function ContactPage() {
  return (
    <section className="content-page">
      <span className="eyebrow">Contact</span>
      <h1>Bring CrySense into a pilot workflow.</h1>
      <form className="contact-form">
        <label>Name<input type="text" placeholder="Your name" /></label>
        <label>Email<input type="email" placeholder="you@example.com" /></label>
        <label>Message<textarea placeholder="Tell us about your use case" rows="5" /></label>
        <Button type="button">Request demo</Button>
      </form>
    </section>
  );
}
