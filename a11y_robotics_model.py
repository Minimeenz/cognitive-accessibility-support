
    """
    a11y_robotics_model.py
    FastAPI service for the A11y-Robotics-Model (simulated accessibility-robotics skills).
    Endpoint:
      - POST /api/robotics/skills : maps intent + environment to safe assistive skills

    Quick start:
      pip install fastapi uvicorn httpx pydantic
      export OPENAI_API_KEY=sk-...
      export CAS_MODEL_ID=gpt-4o-mini
      uvicorn a11y_robotics_model:app --reload --port 8788
      # http://localhost:8788/docs
    """
    import os, json
    from typing import Optional, Dict, Any, List
    import httpx
    from fastapi import FastAPI, Body, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_ID = os.getenv("CAS_MODEL_ID", "gpt-4o-mini")
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")

    app = FastAPI(title="A11y-Robotics-Model Service", version="1.0.0")

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

    class RoboticsRequest(BaseModel):
        intent: str
        roomType: Optional[str] = ""
        devices: Optional[str] = ""

    class RoboticsResponse(BaseModel):
        skillsSuggested: List[Dict[str, Any]] = []

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
        return {"status": "ok", "model": MODEL_ID, "service": "robotics"}

    @app.post("/api/robotics/skills", response_model=RoboticsResponse)
    async def skills(req: RoboticsRequest = Body(...)):
        prompt = f"""
You are A11y-Robotics-Model. Map user intent + environment to safe assistive robot skills.
Constraints: human-in-the-loop, voice confirmation before motion, low-cost devices.
Input:
- Intent: {req.intent}
- Room: {req.roomType}
- Devices: {req.devices}

Output JSON:
{{
  "skillsSuggested": [
    {{
      "name": "Guided Pick-and-Place",
      "steps": "1) highlight item 2) voice confirm 3) route 4) place",
      "safety": "voice confirm before motion"
    }},
    {{
      "name": "Reminder + Navigation Cue",
      "steps": "1) audio cue 2) visual arrow 3) vibration prompt",
      "safety": "no autonomous motion if path unclear"
    }}
  ]
}}
Return JSON only.
""".strip()
        text = await llm_chat(prompt)
        try:
            data = _repair_json(text)
        except Exception:
            data = {"skillsSuggested": []}
        return data
