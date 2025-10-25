
    """
    cas_model.py
    FastAPI service for the CAS-Model (planning + coaching) used by the CAS app.
    Endpoints:
      - POST /api/cas/plan   : tiny-step daily plan generator
      - POST /api/cas/coach  : Q&A coach that suggests small plan edits

    Quick start:
      pip install fastapi uvicorn httpx pydantic
      export OPENAI_API_KEY=sk-...   # set your key
      export CAS_MODEL_ID=gpt-4o-mini
      uvicorn cas_model:app --reload --port 8787
      # http://localhost:8787/docs
    """
    import os, json
    from typing import List, Optional, Dict, Any
    import httpx
    from fastapi import FastAPI, Body, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_ID = os.getenv("CAS_MODEL_ID", "gpt-4o-mini")
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")

    app = FastAPI(title="CAS-Model Service", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_ORIGIN] if FRONTEND_ORIGIN != "*" else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    async def llm_chat(prompt: str, temperature: float = 0.4) -> str:
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
        payload = {
            "model": MODEL_ID,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post("https://api.openai.com/v1/chat/completions",
                                  headers=headers, json=payload)
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=r.status_code, detail=r.text) from e
            return r.json()["choices"][0]["message"]["content"]

    class PlanItem(BaseModel):
        title: str
        why: str
        durationMin: Optional[int] = Field(5, ge=1, le=120)
        difficulty: Optional[str] = "easy"

    class PlanRequest(BaseModel):
        goal: str
        friction: Optional[str] = ""
        strengths: Optional[str] = ""
        sleepHours: Optional[float] = None
        mood: Optional[int] = Field(None, ge=1, le=5)
        focus: Optional[int] = Field(None, ge=1, le=5)

    class PlanResponse(BaseModel):
        summary: str
        items: List[PlanItem] = []
        explanations: List[str] = []

    class CoachRequest(BaseModel):
        question: str
        plan: PlanResponse

    class CoachResponse(BaseModel):
        answer: str
        suggestedEdits: List[Dict[str, Any]] = []

    def _repair_json(text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start, end = text.find("{"), text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start:end+1])
            raise

    @app.get("/api/health")
    async def health():
        return {"status": "ok", "model": MODEL_ID, "service": "cas"}

    @app.post("/api/cas/plan", response_model=PlanResponse)
    async def build_plan(req: PlanRequest = Body(...)):
        prompt = f"""
You are CAS-Model for users with high cognitive and accessibility needs.
Input:
- Goal: {req.goal}
- Friction: {req.friction}
- Strengths: {req.strengths}
- Sleep: {req.sleepHours}h, Mood: {req.mood}/5, Focus: {req.focus}/5

Output JSON:
{{
  "summary":"one-sentence plain-language summary",
  "items":[
    {{"title":"short action","why":"simple reason","durationMin":5,"difficulty":"easy"}},
    {{"title":"short action","why":"simple reason","durationMin":5,"difficulty":"easy"}}
  ],
  "explanations":["1-sentence rationale for plan"]
}}
Return JSON only.
""".strip()
        text = await llm_chat(prompt)
        try:
            data = _repair_json(text)
        except Exception:
            data = {"summary": "Plan ready.", "items": [], "explanations": []}
        return data

    @app.post("/api/cas/coach", response_model=CoachResponse)
    async def coach(req: CoachRequest = Body(...)):
        safe_plan = json.dumps(req.plan.dict())[:4000]
        prompt = f"""
You are CAS-Model Coach. Be brief, kind, concrete. Reading level grade 6-8.
Question: {req.question}
Current plan JSON: {safe_plan}

Answer with JSON:
{{"answer":"plain-language answer","suggestedEdits":[{{"index":0,"newTitle":"","newWhy":""}}]}}
""".strip()
        text = await llm_chat(prompt)
        try:
            data = _repair_json(text)
        except Exception:
            data = {"answer": "I simplified that for you.", "suggestedEdits": []}
        return data
