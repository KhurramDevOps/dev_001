// import React, { useEffect, useState } from "react";
// import axios from "axios";

// const ImageModelsList = () => {
//   const [models, setModels] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState("");

//   useEffect(() => {
//     const fetchImageModels = async () => {
//       setLoading(true);
//       try {
//         const resp = await axios.get("http://localhost:8000/wrapper-list-image-models");
//         // resp.data likely is an array of model names
//         setModels(resp.data || []);
//       } catch (err) {
//         console.error("Error loading image models:", err);
//         setError("Failed to fetch image models: " + (err.response?.data?.detail || err.message));
//       } finally {
//         setLoading(false);
//       }
//     };
//     fetchImageModels();
//   }, []);

//   return (
//     <div style={{ padding: "1rem", marginTop: "1rem", borderTop: "1px solid #ccc" }}>
//       <h3>Available Image Models</h3>
//       {loading && <p>Loading image models…</p>}
//       {error && <p style={{ color: "red" }}>{error}</p>}
//       {!loading && !error && models.length === 0 && <p>No image models found.</p>}
//       <ul>
//         {models.map((m, idx) => (
//           <li key={idx}>{m}</li>
//         ))}
//       </ul>
//     </div>
//   );
// };

// export default ImageModelsList;

import React, { useEffect, useState } from "react";
import axios from "axios";

const ToggleImageModels = () => {
  const [models, setModels] = useState([]);
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchModels = async () => {
    setLoading(true);
    setError("");
    try {
      const resp = await axios.get("http://localhost:8000/wrapper-list-image-models");
      setModels(resp.data || []);
    } catch (err) {
      console.error("Error fetching image models:", err);
      setError("Failed to fetch image models: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const toggleShow = () => {
    if (!show) {
      // about to show, fetch if not yet fetched
      if (models.length === 0 && !loading && !error) {
        fetchModels();
      }
    }
    setShow(!show);
  };

  return (
    <div style={{ marginTop: "1rem" }}>
      <button onClick={toggleShow}>
        {show ? "Hide Image Models" : "Show Image Models"}
      </button>

      {show && (
        <div style={{ marginTop: "0.5rem", padding: "0.5rem", border: "1px solid #ccc" }}>
          {loading && <p>Loading …</p>}
          {error && <p style={{ color: "red" }}>{error}</p>}
          {!loading && !error && models.length === 0 && <p>No models found</p>}
          <ul>
            {models.map((m, idx) => (
              <li key={idx}>{m}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ToggleImageModels;

