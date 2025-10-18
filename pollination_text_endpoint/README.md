Here’s the enhanced version of your instructions in proper Markdown format:

---

# How to Run Backend with Frontend for Testing

## 🧪 Backend Setup

1. Navigate to the `pollinations_text_endpoint` directory and create a virtual environment (venv).
2. Install the following dependencies:

   ```
   fastapi>=0.118.2
   httpx>=0.28.1
   packaging>=25.0
   pollinations>=4.5.1
   pollinations-ai>=4.5.1
   pydub>=0.25.1
   python-dotenv>=1.1.1
   python-multipart>=0.0.20
   requests>=2.32.5
   uvicorn>=0.37.0
   ```
3. Then change into the `wrapper` directory and run:

   ```bash
   uv run uvicorn index1:app --reload
   ```

   This will start the backend application with hot-reload enabled.

---

## 🌐 Frontend Setup

1. Navigate back (if needed) and then go into the `my-frontend` directory:

   ```bash
   cd .. 
   cd my-frontend
   ```
2. Install the required front-end packages:

   ```json
   {
     "axios": "^1.12.2",
     "react": "^19.2.0",
     "react-audio-visualize": "^1.2.0",
     "react-dom": "^19.2.0",
     "react-scripts": "5.0.1",
     "web-vitals": "^2.1.4"
   }
   ```

   (Run `npm install` to install these.)
3. Change into the `src` folder and then start the front-end development server:

   ```bash
   npm start
   ```

   The React front-end will now run on `http://localhost:3000` and will make API calls to the backend endpoints of the Pollinations API wrapper.

---

## ✅ Summary

* Backend runs via `uvicorn` with `--reload` so changes are reflected live.
* Front-end runs on port 3000, making calls to the backend API.
* Make sure both backend and front-end are running simultaneously for full end-to-end testing.

---


