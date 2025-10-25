import type { Request, Response } from "express";
import { chatLLM, safeJson } from "./llm";

const SYS = `You are CAS-Model. Write JSON only.
Rules: short sentences, grade 6–8 reading level, list 3–7 tiny steps, add 1-sentence rationale, and a brief safety note when relevant. Not medical advice.`;

export async function postPlan(req: Request, res: Response) {
  const { goal = "", friction = "", strengths = "", sleepHours = null, mood = null, focus = null } = req.body || {};
  const user = `Build a plan from:
Goal:${goal}
Friction:${friction}
Strengths:${strengths}
Sleep:${sleepHours}h Mood:${mood}/5 Focus:${focus}/5

Return JSON:
{"summary":"", "items":[{"title":"","why":"","durationMin":5,"difficulty":"easy"}], "explanations":[""]}`;
  const data = await chatLLM(user, SYS);
  const text = data?.choices?.[0]?.message?.content as string | undefined;
  res.json(safeJson(text, { summary: "Plan ready.", items: [], explanations: [] }));
}

export async function postCoach(req: Request, res: Response) {
  const { question = "", plan = {} } = req.body || {};
  const user = `Question:${question}
Plan JSON:${JSON.stringify(plan).slice(0, 4000)}
Return JSON:
{"answer":"", "suggestedEdits":[{"index":0,"newTitle":"","newWhy":""}]}`;
  const data = await chatLLM(user, SYS);
  const text = data?.choices?.[0]?.message?.content as string | undefined;
  res.json(safeJson(text, { answer: "Here is a simpler way.", suggestedEdits: [] }));
}

export async function postRobotSkills(req: Request, res: Response) {
  const { intent = "", environment = {} } = req.body || {};
  const user = `Map intent to accessibility-robotics skills.
Input:${JSON.stringify({ intent, environment })}
Return JSON:
{"skillsSuggested":[{"name":"","steps":"1) ...","safety":""}]}`;
  const data = await chatLLM(user, SYS);
  const text = data?.choices?.[0]?.message?.content as string | undefined;
  res.json(safeJson(text, { skillsSuggested: [] }));
}
