# A11y-Robotics-Model (Exploratory)

Purpose: Map user intent and environment to simulated assistive robot skills.

Inputs: Intent text; environment (room type, obstacles/devices).

Outputs: Skills with steps and explicit safety notes.

Guardrails:
- Human-in-the-loop confirmations
- Safety first: no autonomous motion if path unclear
- Plain language, grade 6–8

LLM: OpenAI `gpt-4o-mini` (fallback `gpt-4o`), temperature 0.4.

Limitations: Simulation only; does not connect to physical robots. Future: ROS/Isaac adapters, smart-home hooks.
