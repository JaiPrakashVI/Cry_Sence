import { AlertCircle, CheckCircle2, FileAudio, Loader2, Mic, PlayCircle, RotateCcw, Square, UploadCloud } from "lucide-react";
import React, { useEffect, useMemo, useState } from "react";
import Button from "./Button.jsx";
import { analyzeAudioWithProgress, createDemoPrediction } from "../services/api.js";
import { useRecorder } from "../hooks/useRecorder.js";

function formatTimer(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}

export default function AudioAnalyzer({ setResult, goTo }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("");
  const [progress, setProgress] = useState(0);
  const [lastSource, setLastSource] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const { recording, recordedBlob, durationSeconds, error, startRecording, stopRecording } = useRecorder();

  const selectedSource = file ?? recordedBlob;
  const previewUrl = useMemo(() => {
    if (!selectedSource) {
      return "";
    }
    return URL.createObjectURL(selectedSource);
  }, [selectedSource]);

  useEffect(() => () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
  }, [previewUrl]);

  function mapPrediction(prediction) {
    const distressScore = prediction.distress_score ?? prediction.distressScore ?? 0;
    const confidenceScore = prediction.confidence_score ?? prediction.confidence ?? prediction.confidenceScore ?? 0;
    const riskCategory = prediction.risk_category ?? prediction.risk_level ?? prediction.riskCategory ?? "Low";
    return {
      distressScore,
      confidenceScore,
      emotion: prediction.emotion,
      riskCategory,
      summary: prediction.summary,
      traceId: prediction.trace_id,
      audioDetails: prediction.audio_details ?? prediction.audioDetails ?? {},
      emotionDistribution: prediction.emotion_distribution ?? prediction.emotionDistribution ?? {},
      timestamp: new Date().toISOString()
    };
  }

  function selectFile(nextFile) {
    if (!nextFile) {
      return;
    }
    console.info("[Audio Upload]", { status: "selected", name: nextFile.name, size: nextFile.size, type: nextFile.type });
    setFile(nextFile);
    setStatus("idle");
    setMessage("");
    setProgress(0);
  }

  async function runAnalysis(source) {
    if (!source) {
      setStatus("error");
      setMessage("Select or record audio before analysis.");
      return;
    }

    setLastSource(source);
    setStatus("loading");
    setProgress(8);
    setMessage("Uploading audio to CrySense API...");

    try {
      const prediction = await analyzeAudioWithProgress(source, setProgress);
      setMessage("Preprocessing, extracting features, and generating prediction...");
      setProgress(100);
      setResult(mapPrediction(prediction));
      setStatus("success");
      setMessage("Analysis complete. Review the clinical triage output.");
      setTimeout(() => goTo("results"), 700);
    } catch (analysisError) {
      const fallback = mapPrediction(createDemoPrediction(Date.now()));
      fallback.summary = `${analysisError.message} Local fallback is available for UI continuity, but API analysis should be checked.`;
      setResult(fallback);
      setStatus("error");
      setMessage(analysisError.message);
    }
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragActive(false);
    selectFile(event.dataTransfer.files?.[0]);
  }

  return (
    <section className="analyzer-grid">
      <article className="tool-panel">
        <span className="eyebrow">Audio upload</span>
        <h2>Analyze an existing recording</h2>
        <label
          className={dragActive ? "dropzone active" : "dropzone"}
          onDragOver={(event) => {
            event.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
        >
          <UploadCloud size={28} />
          <span>{file ? file.name : "Choose WAV, MP3, FLAC, M4A, or WEBM audio"}</span>
          {file && <small>{Math.round(file.size / 1024)} KB · {file.type || "audio file"}</small>}
          <input
            type="file"
            accept="audio/*,.wav,.mp3,.m4a,.mp4,.webm,.flac,.ogg"
            onChange={(event) => selectFile(event.target.files?.[0])}
          />
        </label>
        <Button onClick={() => runAnalysis(file)} disabled={!file || status === "loading"}>
          {status === "loading" ? <Loader2 className="spin" size={18} /> : <FileAudio size={18} />}
          Analyze upload
        </Button>
      </article>

      <article className="tool-panel">
        <span className="eyebrow">Browser recorder</span>
        <h2>Capture audio directly</h2>
        <div className={recording ? "recorder active" : "recorder"}>
          <Mic size={34} />
          <span>{recording ? "Recording in progress" : recordedBlob ? "Recording ready" : "Ready to record"}</span>
          <strong>{formatTimer(durationSeconds)}</strong>
        </div>
        <div className="button-row">
          {!recording ? (
            <Button variant="secondary" onClick={startRecording}><Mic size={18} /> Start</Button>
          ) : (
            <Button variant="danger" onClick={stopRecording}><Square size={18} /> Stop</Button>
          )}
          <Button onClick={() => runAnalysis(recordedBlob)} disabled={!recordedBlob || status === "loading"}>
            Analyze recording
          </Button>
        </div>
        {error && <p className="state-message error">{error}</p>}
      </article>

      {previewUrl && (
        <article className="audio-preview">
          <div>
            <PlayCircle size={22} />
            <strong>Audio preview</strong>
            <span>{selectedSource?.name ?? "Recorded audio"}</span>
          </div>
          <audio controls src={previewUrl} />
        </article>
      )}

      {status === "loading" && (
        <div className="glass-card analysis-progress-overlay" style={{ gridColumn: "1 / -1", marginTop: "1rem" }}>
          <div className="pulse-loader">
            <Loader2 className="spin" size={24} style={{ color: "var(--brand)" }} />
          </div>
          <div className="loader-status-text">Analyzing Baby Cry Acoustics</div>
          <div className="loader-sub-text">{message}</div>
          <div className="analysis-progress" aria-label="Analysis progress" style={{ width: "80%", maxWidth: "400px", marginTop: "1rem", height: "0.4rem" }}>
            <span style={{ width: `${Math.max(progress, 12)}%` }} />
          </div>
        </div>
      )}

      {message && status !== "loading" && (
        <div className={`toast ${status}`}>
          {status === "success" ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
          <span>{message}</span>
          {status === "error" && lastSource && (
            <button onClick={() => runAnalysis(lastSource)}><RotateCcw size={16} /> Retry</button>
          )}
        </div>
      )}
    </section>
  );
}
