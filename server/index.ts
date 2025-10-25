import express from "express";
import cors from "cors";
import rateLimit from "express-rate-limit";
import { postPlan, postCoach, postRobotSkills } from "./routes";

const app = express();
app.use(express.json());
app.use(cors({ origin: process.env.FRONTEND_ORIGIN || true }));

app.use(rateLimit({ windowMs: 60_000, max: 60 }));

app.get("/api/health", (_req, res) => res.json({ status: "ok" }));
app.post("/api/cas/plan", postPlan);
app.post("/api/cas/coach", postCoach);
app.post("/api/robotics/skills", postRobotSkills);

const port = Number(process.env.PORT || 8787);
app.listen(port, () => console.log(`CAS server on :${port}`));
