// src/AudioTranscriptionCombined.js

import React, { useState, useRef } from "react";
import axios from "axios";

const AudioTranscriptionCombined = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [error, setError] = useState("");
  const [transcription, setTranscription] = useState("");
  const [loading, setLoading] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    setError("");
    setTranscription("");
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("getUserMedia not supported in this browser");
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, {
          type: audioChunksRef.current[0]?.type || "audio/webm",
        });
        setAudioBlob(blob);
        console.log("Recording stopped, blob:", blob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      console.log("Started recording");
    } catch (err) {
      console.error("Cannot start recording:", err);
      setError("Failed to start recording: " + err.message);
    }
  };

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current;
    if (!recorder) {
      setError("Recorder not initialized");
      return;
    }
    if (recorder.state !== "inactive") {
      recorder.stop();
    }
    setIsRecording(false);
  };

  const handleUploadFile = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    setAudioBlob(file);
    setTranscription("");  // reset previous
    setError("");
  };

  const handleSubmit = async () => {
    if (!audioBlob) {
      setError("No audio to submit (either record or upload).");
      return;
    }

    console.log("Submitting blob/file with type:", audioBlob.type, " size:", audioBlob.size);
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      // Use file name with correct extension if possible
      // If it's a Blob (recorded), name it appropriately
      const filename = audioBlob.name || "speech.webm";
      formData.append("file", audioBlob, filename);

      const resp = await axios.post(
        "http://localhost:8000/wrapper-stt",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 120000,
        }
      );
      console.log("Axios response:", resp);
      const data = resp.data;
      setTranscription(data.transcription || "");
    } catch (err) {
      console.error("Submit error full:", err);
      if (err.response) {
        console.error("Response data:", err.response.data);
        console.error("Response status:", err.response.status);
        console.error("Response headers:", err.response.headers);
      } else if (err.request) {
        console.error("Request made but no response:", err.request);
      } else {
        console.error("Other error:", err.message);
      }
      setError("Submission failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "1rem", maxWidth: "600px" }}>
      <h3>Record or Upload & Transcribe</h3>

      <div style={{ marginBottom: "1rem" }}>
        <strong>Option 1: Upload Audio File</strong><br />
        <input
          type="file"
          accept="audio/*"
          onChange={handleUploadFile}
        />
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <strong>Option 2: Live Recording</strong><br />
        {!isRecording && <button onClick={startRecording}>🎙️ Start Recording</button>}
        {isRecording && <button onClick={stopRecording}>✅ Stop Recording</button>}
      </div>

      {audioBlob && (
        <div style={{ marginBottom: "1rem" }}>
          <button onClick={handleSubmit} disabled={loading}>
            {loading ? "Transcribing..." : "Submit Audio"}
          </button>
        </div>
      )}

      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      {transcription && (
        <div style={{ marginTop: "1rem" }}>
          <h4>Transcription:</h4>
          <p>{transcription}</p>
        </div>
      )}
    </div>
  );
};

export default AudioTranscriptionCombined;
