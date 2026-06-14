const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function analyzeAudio(fileOrBlob) {
  return analyzeAudioWithProgress(fileOrBlob);
}

export function analyzeAudioWithProgress(fileOrBlob, onProgress = () => {}) {
  const formData = new FormData();
  const filename = fileOrBlob.name ?? `recording-${Date.now()}.webm`;
  formData.append("file", fileOrBlob, filename);

  console.info("[Audio Upload]", { filename, size: fileOrBlob.size, type: fileOrBlob.type });

  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    request.open("POST", `${API_BASE_URL}/analyze`);
    request.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    };
    request.onload = () => {
      const payload = JSON.parse(request.responseText || "{}");
      if (request.status >= 200 && request.status < 300) {
        console.info("[Prediction Generated]", payload);
        resolve(payload);
      } else {
        reject(new Error(payload.detail ?? "Analysis failed."));
      }
    };
    request.onerror = () => reject(new Error("Network error while sending audio to CrySense API."));
    request.send(formData);
  });
}

export function createDemoPrediction(seed = 1) {
  const profiles = [
    ["Distress", "Elevated", 72, 91],
    ["Panic", "High", 86, 88],
    ["Sadness", "Moderate", 49, 84],
    ["Neutral", "Low", 18, 93]
  ];
  const [emotion, riskCategory, distressScore, confidenceScore] = profiles[seed % profiles.length];

  return {
    emotion,
    riskCategory,
    distressScore,
    confidenceScore,
    risk_level: riskCategory,
    confidence: confidenceScore,
    summary: `CrySense identified ${emotion.toLowerCase()} indicators with ${confidenceScore}% model confidence.`,
    audio_details: {
      filename: "demo-audio.webm",
      content_type: "audio/webm",
      duration_seconds: 5,
      sample_rate: 22050,
      channels: 1
    },
    emotion_distribution: {
      Distress: emotion === "Distress" ? confidenceScore : 8,
      Crying: 12,
      Fear: emotion === "Fear" ? confidenceScore : 9,
      Panic: emotion === "Panic" ? confidenceScore : 11,
      Sadness: emotion === "Sadness" ? confidenceScore : 15,
      Neutral: emotion === "Neutral" ? confidenceScore : 18,
      Happy: 4,
      Angry: 7
    }
  };
}
