// src/AudioRecorderWithVisualizer.js

import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

const AudioRecorderWithVisualizer = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [error, setError] = useState("");
  const [transcription, setTranscription] = useState("");
  const [loading, setLoading] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // For visualization
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const canvasRef = useRef(null);
  const sourceNodeRef = useRef(null);
  const animationIdRef = useRef(null);

  const startVisualization = (stream) => {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const audioCtx = new AudioContext();
    audioContextRef.current = audioCtx;

    const analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2048;
    analyserRef.current = analyser;

    const source = audioCtx.createMediaStreamSource(stream);
    sourceNodeRef.current = source;

    source.connect(analyser);
    // You may also connect analyser to destination if you want to hear what you're saying:
    // analyser.connect(audioCtx.destination);

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    dataArrayRef.current = dataArray;

    drawVisualizer();  // kick off drawing loop
  };

  const stopVisualization = () => {
    cancelAnimationFrame(animationIdRef.current);
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    audioContextRef.current = null;
    analyserRef.current = null;
    dataArrayRef.current = null;
    sourceNodeRef.current = null;
  };

  const drawVisualizer = () => {
    const canvas = canvasRef.current;
    const analyser = analyserRef.current;
    const dataArray = dataArrayRef.current;
    if (!canvas || !analyser || !dataArray) {
      return;
    }

    const canvasCtx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    analyser.getByteTimeDomainData(dataArray);

    canvasCtx.fillStyle = "#f5f5f5";
    canvasCtx.fillRect(0, 0, width, height);

    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = "blue";
    canvasCtx.beginPath();

    const sliceWidth = (width * 1.0) / dataArray.length;
    let x = 0;

    for (let i = 0; i < dataArray.length; i++) {
      const v = dataArray[i] / 128.0;  // between ~0 and 2
      const y = (v * height) / 2;

      if (i === 0) {
        canvasCtx.moveTo(x, y);
      } else {
        canvasCtx.lineTo(x, y);
      }
      x += sliceWidth;
    }

    canvasCtx.lineTo(width, height / 2);
    canvasCtx.stroke();

    animationIdRef.current = requestAnimationFrame(drawVisualizer);
  };

  const startRecording = async () => {
    setError("");
    setTranscription("");
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("getUserMedia not supported");
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
      startVisualization(stream);
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
    stopVisualization();
  };

  const handleSubmit = async () => {
    if (!audioBlob) {
      setError("No audio recorded to submit");
      return;
    }

    console.log("Submit: blob type:", audioBlob.type);
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      const filename = audioBlob.name || "speech.webm";
      formData.append("file", audioBlob, filename);

      const resp = await axios.post(
        "http://localhost:8000/wrapper-stt",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 120000,
        }
      );
      console.log("Response:", resp);
      setTranscription(resp.data.transcription || "");
    } catch (err) {
      console.error("Submit error:", err);
      setError("Submission failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "1rem", maxWidth: "600px" }}>
      <h3>Record & Transcribe</h3>
      <div>
        {!isRecording && <button onClick={startRecording}>🎙️ Start Recording</button>}
        {isRecording && <button onClick={stopRecording}>✅ Stop Recording</button>}
      </div>

      <div style={{ margin: "10px 0" }}>
        {isRecording ? (
          <span style={{ color: "red", fontWeight: "bold" }}>Recording...</span>
        ) : (
          <span>Not recording</span>
        )}
      </div>

      <canvas
        ref={canvasRef}
        width={300}
        height={100}
        style={{
          border: "1px solid #ddd",
          backgroundColor: "#f5f5f5",
        }}
      />

      {audioBlob && !isRecording && (
        <div style={{ marginTop: "1rem" }}>
          <button onClick={handleSubmit} disabled={loading}>
            {loading ? "Transcribing..." : "Submit Recording"}
          </button>
        </div>
      )}

      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {transcription && (
        <div style={{ marginTop: "1rem" }}>
          <strong>Transcription:</strong>
          <p>{transcription}</p>
        </div>
      )}
    </div>
  );
};

export default AudioRecorderWithVisualizer;
