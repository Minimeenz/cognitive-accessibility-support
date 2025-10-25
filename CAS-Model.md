# CAS-Model (Cognitive & Accessibility Support)

Purpose: Generate short daily plans and plain-language coaching for users with high cognitive and accessibility needs.

Inputs: Goal, frictions, strengths, optional biomarkers (sleep, mood, focus).

Outputs: 3–7 tiny tasks with “why,” a 1-sentence summary, optional suggested edits.

Guardrails:
- Grade 6–8 reading level
- Short sentences, simple words
- Include brief safety note when relevant
- Not medical advice

LLM: OpenAI `gpt-4o-mini` (fallback `gpt-4o`), temperature 0.4.

Limitations: Not a clinical tool; users should consult clinicians for care decisions; hallucinations mitigated via JSON-only responses and strict prompts.
