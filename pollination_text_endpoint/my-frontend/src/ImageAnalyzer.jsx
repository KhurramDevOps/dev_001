import React, { useState } from "react";
import axios from "axios";

const ImageAnalyzer = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setError("");
    setDescription("");
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setSelectedFile(null);
      setPreviewUrl(null);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError("Please select an image first.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("image", selectedFile, selectedFile.name);

      const resp = await axios.post(
        "http://localhost:8000/wrapper-image-analyze",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log("Image analyze response:", resp);
      setDescription(resp.data.description || "");
    } catch (err) {
      console.error("Image analyze error:", err);
      setError("Analysis failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "1rem", maxWidth: "600px" }}>
      <h3>Image → Analyze / Describe</h3>
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
      />
      {previewUrl && (
        <div style={{ margin: "1rem 0" }}>
          <img
            src={previewUrl}
            alt="Selected"
            style={{ maxWidth: "100%", height: "auto", border: "1px solid #ddd" }}
          />
        </div>
      )}
      {selectedFile && (
        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "Analyzing..." : "Analyze Image"}
        </button>
      )}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {description && (
        <div style={{ marginTop: "1rem" }}>
          <strong>Description:</strong>
          <p>{description}</p>
        </div>
      )}
    </div>
  );
};

export default ImageAnalyzer;
