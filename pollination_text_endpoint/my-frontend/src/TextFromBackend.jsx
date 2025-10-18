// src/TextFromBackend.jsx

import React, { useState } from "react";

function TextFromBackend() {
  const [prompt, setPrompt] = useState("");
  const [textResult, setTextResult] = useState("");
  const [error, setError] = useState(null);

  const generateText = async () => {
    setError(null);
    try {
      const resp = await fetch("http://localhost:8000/wrapper-generate-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      const json = await resp.json();
      if (!resp.ok) {
        setError(json.detail || "Error generating text");
        return;
      }
      setTextResult(json.result);
    } catch (err) {
      console.error("Text fetch error:", err);
      setError("Failed to fetch text");
    }
  };

  return (
    <div>
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter prompt for text"
        style={{ width: "100%", marginBottom: "8px" }}
      />
      <button onClick={generateText}>Generate Text</button>
      {error && <div style={{ color: "red" }}>Error: {error}</div>}
      {textResult && (
        <div style={{ marginTop: "16px", whiteSpace: "pre-wrap" }}>
          <strong>Result:</strong>
          <div>{textResult}</div>
        </div>
      )}
    </div>
  );
}

export default TextFromBackend;
