

// import React from "react";
// import ImageFromBackend from "./ImageFromBackend";
// import TextFromBackend from "./TextFromBackend";
// import TextToSpeechPlayer from "./TextToSpeechPlayer";
// // import AudioRecorderWithVisualizer from "./AudioRecorderWithVisualizer";
// import AudioTranscriptionCombined from "./AudioTranscriptionCombined";
// import ImageAnalyzer from "./ImageAnalyzer";
// import TextModelsList from "./TextModelsList";

// function App() {
//   return (
//     <div className="App" style={{ padding: "20px" }}>
//       <h1>Pollinations / FastAPI Demo</h1>

//       <section style={{ marginBottom: "40px" }}>
//         <h2>Generate Image</h2>
//         <ImageFromBackend />
//       </section>

//       <section style={{ marginBottom: "40px" }}>
//         <h2>Generate Text</h2>
//         <TextFromBackend />
//         {/* Insert models list just after TextFromBackend */}
//         <TextModelsList />
//       </section>

//       <section style={{ marginBottom: "40px" }}>
//         <h2>Text → Speech</h2>
//         <TextToSpeechPlayer />
//       </section>

//       <section style={{ marginBottom: "40px" }}>
//         <h2>Audio → Transcription</h2>
//         <AudioTranscriptionCombined />
//       </section>

//       <section style={{ marginTop: "40px" }}>
//         <h2>Image → Description</h2>
//         <ImageAnalyzer />
//       </section>
//     </div>
//   );
// }

// export default App;

import React from "react";
import ImageFromBackend from "./ImageFromBackend";
import TextFromBackend from "./TextFromBackend";
import TextToSpeechPlayer from "./TextToSpeechPlayer";
import AudioTranscriptionCombined from "./AudioTranscriptionCombined";
import ImageAnalyzer from "./ImageAnalyzer";
import TextModelsList from "./TextModelsList";
import ImageModelsList from "./ImageModelsList";

function App() {
  return (
    <div className="App" style={{ padding: "20px" }}>
      <h1>Pollinations / FastAPI Demo</h1>

      <section style={{ marginBottom: "40px" }}>
        <h2>Generate Image</h2>
        <ImageFromBackend />
        <ImageModelsList />
      </section>

      <section style={{ marginBottom: "40px" }}>
        <h2>Generate Text</h2>
        <TextFromBackend />
        <TextModelsList />
      </section>  

      <section style={{ marginBottom: "40px" }}>
        <h2>Text → Speech</h2>
        <TextToSpeechPlayer />
      </section>

      <section style={{ marginBottom: "40px" }}>
        <h2>Audio → Transcription</h2>
        <AudioTranscriptionCombined />
      </section>

      <section style={{ marginTop: "40px" }}>
        <h2>Image → Description</h2>
        <ImageAnalyzer />
      </section>
    </div>
  );
}

export default App;