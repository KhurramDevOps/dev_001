import React, { useState } from "react";
import axios from "axios";

const AudioTranscription = () => {
  const [file, setFile] = useState(null);
  const [transcription, setTranscription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setTranscription("");
    setError("");
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select an audio file first.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      // Adjust the “file” field name if your FastAPI expects a different name
      formData.append("file", file);

      const resp = await axios.post(
        "http://localhost:8000/wrapper-stt",  // change to your endpoint
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      // Expecting something like: { filename: "...", transcription: "..." }
      setTranscription(resp.data.transcription || "No transcription received");
    } catch (err) {
      console.error("Upload / transcription error:", err);
      setError("Failed to transcribe. " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "1rem", maxWidth: "500px" }}>
      <h2>Audio Transcription</h2>
      <input
        type="file"
        accept="audio/*"
        onChange={handleFileChange}
      />
      <br />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Transcribing…" : "Upload & Transcribe"}
      </button>

      {error && (
        <p style={{ color: "red" }}>Error: {error}</p>
      )}

      {transcription && (
        <div style={{ marginTop: "1rem" }}>
          <h4>Transcription:</h4>
          <p>{transcription}</p>
        </div>
      )}
    </div>
  );
};

export default AudioTranscription;
