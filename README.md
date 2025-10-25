
# CAS App Models (APIs)

APIs and prompts for the CAS (Cognitive & Accessibility Support) app.

## What’s Included
Two **separate Python services** (FastAPI) that power your CAS app’s AI features:

1) **CAS-Model** (`cas_model.py`)  
   - **POST `/api/cas/plan`** – builds a tiny-step daily plan from a user’s goal/context  
   - **POST `/api/cas/coach`** – Q&A coach that suggests edits to the plan (plain language)

2) **A11y-Robotics-Model** (`a11y_robotics_model.py`)  
   - **POST `/api/robotics/skills`** – simulates accessibility-robotics “skills” from intent + environment (with safety notes)

These mirror the original three endpoints described previously and are designed to connect to your **Lovable** front-end.

## Quick Start (Node-free, Python version)
```bash
# 1) Environment
python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn httpx pydantic

# 2) Secrets
export OPENAI_API_KEY=sk-...
export CAS_MODEL_ID=gpt-4o-mini            # or your preferred model
export FRONTEND_ORIGIN=https://<your-lovable-app>.lovable.app   # optional

# 3a) Run CAS-Model (planning + coaching) on 8787
uvicorn cas_model:app --reload --port 8787

# 3b) Run A11y-Robotics-Model on 8788
uvicorn a11y_robotics_model:app --reload --port 8788
```

Open the interactive docs:
- CAS-Model: http://localhost:8787/docs  
- A11y-Robotics-Model: http://localhost:8788/docs

## Environment Variables
- `OPENAI_API_KEY` – OpenAI secret used by both services  
- `CAS_MODEL_ID` – model name (default `gpt-4o-mini`)  
- `FRONTEND_ORIGIN` – optional CORS allowlist origin (e.g., your Lovable URL)

## Connect from Lovable
Point your front-end to these endpoints:
- `/api/cas/plan` and `/api/cas/coach` (port 8787 if running locally)  
- `/api/robotics/skills` (port 8788 if running locally)

## What the Models Do
- **CAS-Model**: Turns goals and context into **short, friendly daily plans** and answers user questions with **plain-language coaching**. Built for users with **high cognitive and accessibility needs**—suggests small steps, shows “why,” and encourages progress.
- **A11y-Robotics-Model**: Maps user intent + environment into **assistive robot skills** (simulated). Returns steps and **safety constraints**; future work can connect to real robots or smart-home devices.

## Legacy (JS) Quick Start
If you prefer the original Node service layout, see the previous README section:
```bash
git clone <your-repo-url>
cd cas-app-models
cp .env.example .env       # add your OPENAI_API_KEY
npm i
npm run dev
# Open http://localhost:8787/api/health -> {"status":"ok"}
```
