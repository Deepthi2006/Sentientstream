# SentientStream 🎬✨

SentientStream is a fully AI-driven, TikTok-style infinite scrolling video platform. Instead of simply relying on what users explicitly click, SentientStream dynamically curates, categorizes, and streams videos based entirely on **emotional resonance and mood tracking**. 

The system operates completely autonomously—from hitting external APIs to download royalty-free stock footage, to physically "watching" and categorizing the videos using advanced Large Multimodal Models (Vision LLMs), to constantly optimizing a user's mathematical embedding space to serve them personalized, continuously buffering content.

---

## 🌟 Core Features

- **TikTok-Style Seamless Interface:** A responsive React (Vite) frontend utilizing `framer-motion` and native Intersection Observers for an endless, snap-scrolling viewing experience.
- **Autonomous Video Ingestion:** Background scripts automatically communicate with the Pexels Video API to actively hunt and download new video content locally to scale the platform dataset.
- **Multimodal AI Vision Pipeline:** As new videos are ingested, the backend utilizes `cv2` (OpenCV) to extract keyframes and sends them to Groq (`llama-4-scout-17b-16e-instruct` / `llama-3.2-11b-vision-preview`). The AI acts as a human moderator, visually dissecting the scenes, deciphering what is happening natively, and assigning emotional labels (Happy, Sad, Calm, Dark, Energetic, Romantic, Inspirational).
- **Semantic Vector Storage (FAISS):** The AI-generated mood descriptions and titles are fed completely locally into `sentence-transformers` (`all-MiniLM-L6-v2`). This generates 384-dimensional mathematical arrays of the video's context, mapping them instantly into a blazing-fast memory vector index powered by Meta's FAISS library.
- **Dynamic Content Injection:** The algorithmic feed calculates cosine similarity between the mathematical query array and the video arrays, seamlessly appending ~30% random unseen content globally into the feed to completely break repetitive filter bubbles.
- **Deep Authentication & Behavioral Tracking:** Leverages PostgreSQL and JWT hashing to securely register user accounts. The frontend deeply monitors engagement parameters—such as exact partial-second watch percentages, intentional pauses, raw loop playbacks, and explicit likes.
- **Autonomous "Surprise Me" (Auto-Mode):** When heavily authenticated users browse in "Auto Mode," SentientStream continually updates their personalized neural fingerprint (User Embedding Matrix). If a user skips a video early, the matrix punishes that semantic weight. If they loop or like a video, the mathematical vectors shift closer to that specific mood.

---

## ⚙️ Architecture & Data Flow

SentientStream is structured into a distinct Backend Pipeline and a Live API/Frontend.

### 1. The Autonomous Ingestion Pipeline
1. **Fetching (`run_ingestion.py`):** The chron-job orchestrator requests `N` videos from Pexels, parses strict metadata directly into the PostgreSQL Database asynchronously, and downloads the raw `.mp4` chunks into `storage/videos/`.
2. **AI Processing (`run_ai_pipeline.py`):** The system isolates new `pending` videos in the database. It samples exact screenshot frames at mathematically optimal timestamp intervals, shipping them through API boundaries to Groq. Groq then returns JSON parameters containing precise mood matrices and detailed semantic scene descriptions.
3. **FAISS Indexing (`run_indexer.py`):** Prepares the final text embeddings locally (avoiding expensive cloud embedding API costs) and locks the numerical vectors into `faiss.index`.

### 2. The Live Streaming & Recommendation Loop
1. **User Request:** The React client opens the app and executes `GET /feed?mode=auto` carrying their secure JWT token.
2. **Behavioral Assembly:** 
   - The FastAPI backend authenticates the user.
   - It performs an emergency check to identify all previously watched `Interaction` IDs and removes them from the primary query layer so users rarely see dead duplicate reruns.
   - It extracts the `User.user_embedding` (a 384-length float array representing their historical watch preferences).
3. **Similarity Calculation:** FAISS performs an instantaneous inner-product (cosine similarity) search across the entire index to find the Top K highest scoring mathematical video matches.
4. **Byte-Range Delivery:** The frontend mounts physical HTML5 `<video>` elements. As the user scrubs through the UI, FastAPI delivers flawless HTTP `206 Partial Content` offsets utilizing Starlette's native ASGI `FileResponse` framework. Your OS receives raw streams directly to hardware acceleration.
5. **Real-Time Matrix Shifting:** As the user scrolls away, React silently fires a telemetry post to `POST /interactions`. The backend consumes the `watch_duration` metric. Before completing the request, SentientStream permanently refines the user's base identity embedding against the exact matrix of the video they just skipped/liked, creating an organically evolving AI loop.

---

## 🛠️ Technology Stack

**Frontend**
- **React (TypeScript):** Component architecture.
- **Vite:** Blazing fast HMR and optimized building.
- **Tailwind CSS & Lucide Icons:** Responsive, zero-config utility styling and modern SVG iconography.

**Backend**
- **Python (FastAPI):** Next-gen, async-first, extremely fast ASGI web framework.
- **SQLAlchemy (AsyncPG) & PostgreSQL:** Primary persistent, transactional, relational schema layer.
- **FAISS (Facebook AI Similarity Search):** CPU-optimized vector calculations.
- **Sentence-Transformers:** Generates state-of-the-art sentence text embeddings natively inside the machine.
- **Groq API:** Cloud-scale inferences operating Llama Vision architectures for millisecond visual analysis.

---

## 🚀 Running the Platform

1. **Activate Environment & PostgreSQL:** Ensure your virtual environment is active and Postgres (`:5432`) is securely hosting the `sentistream` root schema.
2. **Feed the AI (Ingestion Tools):**
   ```bash
   python -m scripts.run_ingestion
   python -m scripts.run_ai_pipeline
   python -m scripts.run_indexer
   ```
3. **Boot the Backend (Port 8000):**
   ```bash
   python -m backend.main
   ```
4. **Boot the App (Port 5173):**
   ```bash
   cd frontend
   npm run dev
   ```



final
