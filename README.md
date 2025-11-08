# CompanionAI

CompanionAI is a multilingual, empathy-first companion that blends natural conversation, lightweight emotion modelling, and a mood-tracking dashboard. The project now ships with a FastAPI backend, a browser-based client, and a SQLite database that remembers conversations only when the user opts in.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Data Model](#data-model)
- [Getting Started](#getting-started)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Environment Variables](#environment-variables)
  - [Running Locally](#running-locally)
- [API Overview](#api-overview)
- [Privacy Controls](#privacy-controls)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

## Features
- **Multilingual replies** — the AI answers in English, Hindi, Spanish, or French by inspecting each message.
- **Emotion-aware tone** — a rules-based sentiment engine adjusts responses and animates the avatar’s expression.
- **Pixi.js avatar** — a friendly face reacts to the detected mood right in the browser.
- **Voice and text chat** — the Web Speech API enables speech-to-text capture alongside classic text input.
- **Secure accounts** — FastAPI, JWT, and Passlib manage registration, login, and personal settings.
- **Mood tracker dashboard** — Chart.js visualises daily moods derived from conversations or optional facial cues.
- **User choice** — people can disable history storage at any time; when disabled, no conversations or moods are stored.

## Architecture

### Backend
- Built with **FastAPI** and served with Uvicorn.
- Uses **SQLAlchemy** on top of SQLite (async) for persistence.
- Passwords are hashed with **Passlib** (`bcrypt` scheme) and authenticated with JWT tokens.
- Conversation logic combines language detection, sentiment scoring, and mood classification.
- Provides REST endpoints for auth, chat, mood history, and user profile management.

### Frontend
- Vanilla **HTML/CSS/JavaScript** experience optimised for quick prototyping.
- **Pixi.js** renders a 2D avatar that changes mood in real time.
- **Chart.js** displays a mood timeline that updates after each conversation.
- **Web Speech API** powers optional speech-to-text for message input.
- Uses the Fetch API to interact with the FastAPI backend.

### Data Model
- `User` — account with email, hashed password, display name, and a `history_enabled` flag.
- `ChatMessage` — saved messages (user + AI) with language, sentiment, and timestamp metadata.
- `MoodEntry` — per-day mood summaries sourced from chat sentiment or facial cues.

## Getting Started

### Backend Setup
```bash
# From the repository root
python -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate

pip install -r backend/requirements.txt
```

### Frontend Setup
The frontend is static. You can open `frontend/index.html` directly in the browser or serve it using any local HTTP server:
```bash
# Example using Python's built-in server
cd frontend
python -m http.server 5173
```

### Environment Variables
Create a `.env` file in the repository root if you need to override defaults:
```
COMPANIONAI_SECRET_KEY=change-me
COMPANIONAI_DATABASE_URL=sqlite+aiosqlite:///./companionai.db
COMPANIONAI_ALLOWED_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```
The defaults already allow common localhost origins, so the file is optional for local development.

### Running Locally
1. **Start the backend API** (from the repository root with the virtual environment activated):
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

2. **Open a second terminal for the frontend** and serve the static files using any simple HTTP server. For example:
   ```bash
   cd frontend
   python -m http.server 5173
   ```

3. **Visit the app** at [http://localhost:5173](http://localhost:5173). The frontend is pre-configured to talk to the backend at `http://localhost:8000`.

4. **(Optional) Run the API test suite** from the repository root:
   ```bash
   pytest
   ```
   If FastAPI or its dependencies are missing, the tests will gracefully skip instead of failing.

## API Overview
- `POST /auth/register` — create a new account.
- `POST /auth/login` — obtain a JWT access token.
- `GET /users/me` — fetch the current profile.
- `PATCH /users/me` — update the display name or toggle history storage.
- `POST /chat/respond` — submit a message and receive the AI reply + mood inference.
- `GET /chat/history` — retrieve the most recent messages (skipped when history is disabled).
- `GET /mood/entries` — list saved mood entries.
- `POST /mood/entries` — add a manual mood entry (e.g., from facial analysis).
- `DELETE /mood/entries/{id}` — remove an entry.

All non-auth routes require a valid bearer token.

## Privacy Controls
- History storage is opt-in by default and can be disabled from the settings toggle.
- When history is disabled, new messages and moods are not persisted.
- All facial emotion detection is expected to run client-side; no video data is uploaded.
- Passwords use bcrypt hashing, and JWTs include expiration claims.

## Project Structure
```
companionai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   └── requirements.txt
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
└── README.md
```

## Roadmap
- Expand language detection with statistical models and add more languages.
- Integrate TensorFlow.js + Face API.js for real facial mood detection.
- Introduce push-to-talk responses via Web Speech API text-to-speech.
- Harden authentication with refresh tokens and device management.
- Build automated tests for API contracts and frontend flows.

## Contributing
Issues and pull requests are welcome! Please include clear reproduction steps, tests where practical, and empathy-driven UX considerations.
