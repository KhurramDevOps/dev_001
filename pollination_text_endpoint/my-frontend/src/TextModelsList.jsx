

import React, { useEffect, useState } from "react";
import axios from "axios";

const ToggleTextModels = () => {
  const [models, setModels] = useState([]);
  const [showModels, setShowModels] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchModels = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get("http://localhost:8000/wrapper-list-text-models");
      const data = response.data;
      let arr = [];
      if (Array.isArray(data)) {
        arr = data;
      } else if (typeof data === "object") {
        arr = Object.values(data);
      }
      setModels(arr);
    } catch (err) {
      console.error("Error fetching models:", err);
      setError("Failed to fetch models: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const toggleModels = () => {
    setShowModels((prev) => {
      if (!prev && models.length === 0 && !loading && !error) {
        fetchModels();
      }
      return !prev;
    });
  };

  return (
    <div style={{ padding: "1rem", marginTop: "2rem", borderTop: "1px solid #ccc" }}>
      <h3>Available Text / Vision / Audio Models</h3>
      <button onClick={toggleModels} style={{ marginBottom: "1rem" }}>
        {showModels ? "Hide Models" : "Show Models"}
      </button>

      {showModels && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))", gap: "1rem" }}>
          {loading && <p>Loading models…</p>}
          {error && <p style={{ color: "red" }}>{error}</p>}
          {!loading && !error && models.length === 0 && <p>No models found.</p>}
          {models.map((m, idx) => (
            <div key={idx} style={{ border: "1px solid #ddd", borderRadius: "8px", padding: "0.75rem" }}>
              <h4 style={{ margin: "0 0 0.5rem 0" }}>{m.name}</h4>
              <p style={{ margin: "0.25rem 0" }}>
                <strong>Description:</strong> {m.description || "—"}
              </p>
              <p style={{ margin: "0.25rem 0" }}>
                <strong>Modalities:</strong> {m.input_modalities?.join(", ")} → {m.output_modalities?.join(", ")}
              </p>
              <p style={{ margin: "0.25rem 0" }}>
                <strong>Tier:</strong> {m.tier}
              </p>
              {m.voices && (
                <p style={{ margin: "0.25rem 0" }}>
                  <strong>Voices:</strong> {m.voices.join(", ")}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ToggleTextModels;