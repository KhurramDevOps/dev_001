// TextToSpeechPlayer.jsx
import React, { useState, useRef } from "react";

export default function TextToSpeechPlayer() {
  const [text, setText] = useState("");
  const [voice, setVoice] = useState("alloy");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const audioRef = useRef(null);

  const handleGenerate = async () => {
    if (!text.trim()) {
      setError("Text is empty");
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const resp = await fetch("http://localhost:8000/wrapper-tts-save", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // you don’t send the token here from frontend (token is used in backend),
          // but if you’re doing direct calls to Pollinations from the browser, you might use a referrer-based auth
        },
        body: JSON.stringify({ text, voice })
      });

      if (!resp.ok) {
        const msg = await resp.text();
        throw new Error(`TTS error: ${resp.status} ${msg}`);
      }

      // get the binary audio file (blob)
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);

      if (audioRef.current) {
        audioRef.current.src = url;
        await audioRef.current.play().catch(err => {
          console.warn("Autoplay blocked or other play error:", err);
        });
      }
    } catch (err) {
      console.error("Error generating or playing audio:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "auto" }}>
      <h3>Text → Speech</h3>
      <textarea
        rows={4}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text..."
        style={{ width: "100%", padding: 8 }}
      />
      <div style={{ marginTop: 8 }}>
        <label>
          Voice:{" "}
          <select value={voice} onChange={(e) => setVoice(e.target.value)}>
            <option value="alloy">alloy</option>
            <option value="nova">nova</option>
            <option value="echo">echo</option>
            <option value="fable">fable</option>
            <option value="onyx">onyx</option>
            <option value="shimmer">shimmer</option>
          </select>
        </label>
      </div>
      <div style={{ marginTop: 12 }}>
        <button onClick={handleGenerate} disabled={loading}>
          {loading ? "Generating..." : "Generate & Play"}
        </button>
      </div>
      {error && (
        <div style={{ color: "red", marginTop: 8 }}>Error: {error}</div>
      )}
      <div style={{ marginTop: 16 }}>
        <audio ref={audioRef} controls style={{ width: "100%" }} />
      </div>
    </div>
  );
}
