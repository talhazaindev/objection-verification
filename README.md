# Objection Anonymous Source Verification Prototype

## Live Demo

- App: [Railway URL after deploy]
- Repository: https://github.com/talhazaindev/objection-verification

## What Was Built

A privacy-preserving evidence verification system that:

1. **Hashes evidence on intake** (SHA-256) to detect tampering
2. **Auto-extracts text** from `.txt`, `.pdf`, `.mp3`, `.wav`, `.docx`
3. **Sanitizes PII** before storage/analysis
4. **Uses Groq (Llama 3.3 70B)** to analyze consistency, corroboration, and plausibility
5. **Generates a public certificate** with zero source-identifying information
6. **Produces publication-ready attribution language**

## AI Workflow & Tools

- **Groq (Llama 3.3 70B)**: Core evidence analysis (consistency checking, corroboration detection, plausibility assessment)
- **FastAPI**: Backend API with async endpoints
- **Next.js 14**: Frontend with App Router, Tailwind CSS, react-dropzone
- **python-magic**: File type detection
- **SpeechRecognition + pydub**: Audio transcription
- **PyPDF2**: PDF text extraction
- **SHA-256**: Cryptographic hashing for tamper detection

## What Was Cut (Prioritization)

- **Database layer**: Used in-memory store for prototype speed. Production would use PostgreSQL + Redis.
- **Multi-LLM jury**: Objection uses 5+ models; prototype uses Groq only for speed/cost.
- **Real-time Fire Blanket**: Out of scope for this challenge.
- **Honor Index scoring**: Out of scope — focused on single-case verification.
- **Advanced PII detection**: Used regex-based sanitization; production would use Presidio or similar.
- **Blockchain anchoring**: Hash chain is computed but not anchored to blockchain.

## Project Structure

```
objection-prototype/
├── frontend/          # Next.js 14 App Router
├── backend/           # FastAPI
└── sample-data/       # Test evidence files
```

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy environment variables:

```bash
cp .env.example .env   # then add your Groq API key
```

Or create `backend/.env` with:

```
GROQ_API_KEY=your-groq-api-key
```

Start the API (with venv active; `.env` is loaded automatically):

```bash
uvicorn app.main:app --reload
```

Health check: http://localhost:8000/health

**Windows note:** `python-magic` requires `libmagic`. For local Windows development, use Docker (recommended) or WSL. Production Docker image includes `libmagic1`.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # or copy manually on Windows
npm run dev
```

Open http://localhost:3000

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`.

### Docker (unified frontend + backend)

Build and run from the project root:

```bash
docker build -t objection-prototype .
docker run -p 8080:8080 --env-file backend/.env objection-prototype
```

Open http://localhost:8080 — nginx routes `/` to Next.js and `/api/*` to FastAPI.

For Railway, set `PORT` (injected automatically) and `GROQ_API_KEY` as environment variables.

## Sample Data

Place evidence files in `sample-data/` and upload via the `/verify` page. Expected files:

- `journalist_intake_notes.txt`
- `email_chain_vasquez_hargrove.txt` (or `.pdf`)
- `recorded_conversation_march_19.mp3`
- `data_comparison_memo.txt`
- `vasquez_personal_notes.txt`

## Deployment (Railway)

1. Push this repo to [GitHub](https://github.com/talhazaindev/objection-verification)
2. Go to [Railway](https://railway.com) and sign in with GitHub
3. **New Project → Deploy from GitHub repo** → select `objection-verification`
4. Railway auto-detects the root [`Dockerfile`](Dockerfile) and reads [`railway.toml`](railway.toml) for health checks
5. Open your service → **Variables** and add:
   - `GROQ_API_KEY` — required (your Groq API key)
   - `GROQ_MODEL` — optional (`llama-3.3-70b-versatile`)
6. Railway assigns a public URL under **Settings → Networking → Generate Domain**

One URL serves the full app (UI + API via nginx). `PORT` is injected by Railway automatically.

**Persistence caveat:** The in-memory `certificate_store` resets on redeploy or restart. Production should use Redis or PostgreSQL.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/verify/` | Upload evidence files, run verification |
| GET | `/api/verify/certificate/{id}` | Public certificate (no analysis/extracted text) |

## Verification Checklist

- [ ] All sample files upload successfully
- [ ] SHA-256 hashes are computed and displayed
- [ ] Modifying a file and re-uploading produces a different hash
- [ ] Certificate contains ZERO extracted text or PII
- [ ] Attribution language is copy-paste ready
- [ ] Public certificate page loads without authentication
- [ ] Audio files are transcribed (graceful fallback on failure)
- [ ] Consistency conflicts are flagged when contradictory evidence is uploaded
- [ ] Corroborated claims are identified across multiple files
- [ ] Overall confidence score is between 0.0 and 1.0
- [ ] Deployed URLs are accessible and functional
