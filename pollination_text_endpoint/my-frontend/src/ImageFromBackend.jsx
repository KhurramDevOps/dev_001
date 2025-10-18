import React, { useState } from 'react';

function ImageFromBackend() {
  const [prompt, setPrompt] = useState("");
  const [imgUrl, setImgUrl] = useState("");

  const generateImage = async () => {
    try {
      const resp = await fetch("http://localhost:8000/wrapper-generate-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      });
      const json = await resp.json();
      if (!resp.ok) {
        console.error("Error:", json);
        return;
      }
      // suppose backend returns { filename }
      const filename = json.filename;
      // Construct the URL to fetch the image
      const imageUrl = `http://localhost:8000/wrapper-images/${filename}`;
      setImgUrl(imageUrl);
    } catch (err) {
      console.error("Fetch failed:", err);
    }
  };

  return (
    <div>
      <h3>Generate Image</h3>
      <input
        type="text"
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        placeholder="Type prompt here"
      />
      <button onClick={generateImage}>Generate</button>
      {imgUrl && <img src={imgUrl} alt="Generated" />}
    </div>
  );
}

export default ImageFromBackend;
