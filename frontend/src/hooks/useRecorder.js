import { useEffect, useRef, useState } from "react";

const MIME_CANDIDATES = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/mp4",
  "audio/wav"
];

function supportedMimeType() {
  if (!window.MediaRecorder) {
    return "";
  }
  return MIME_CANDIDATES.find((type) => MediaRecorder.isTypeSupported(type)) ?? "";
}

export function useRecorder() {
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [durationSeconds, setDurationSeconds] = useState(0);
  const [error, setError] = useState("");

  async function startRecording() {
    setError("");
    setRecordedBlob(null);
    setDurationSeconds(0);
    try {
      if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
        throw new Error("This browser does not support microphone recording.");
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = supportedMimeType();
      chunksRef.current = [];
      mediaRecorderRef.current = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };
      mediaRecorderRef.current.onstop = () => {
        const type = mimeType || "audio/webm";
        setRecordedBlob(new File(chunksRef.current, `crysense-recording-${Date.now()}.webm`, { type }));
        stream.getTracks().forEach((track) => track.stop());
      };
      mediaRecorderRef.current.start(1000);
      timerRef.current = window.setInterval(() => setDurationSeconds((value) => value + 1), 1000);
      setRecording(true);
      console.info("[Audio Capture]", { status: "started", mimeType: mimeType || "browser-default" });
    } catch (captureError) {
      setError(captureError.message || "Microphone access is unavailable. Check browser permissions and try again.");
    }
  }

  function stopRecording() {
    mediaRecorderRef.current?.stop();
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setRecording(false);
    console.info("[Audio Capture]", { status: "stopped", durationSeconds });
  }

  useEffect(() => () => {
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
    }
  }, []);

  return { recording, recordedBlob, durationSeconds, error, startRecording, stopRecording };
}
