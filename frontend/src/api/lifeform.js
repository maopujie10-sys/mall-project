import { agentApi } from "./index"

export function getLifeformStatus() { return agentApi.get("/agent/lifeform/status") }
export function getLifeformMood() { return agentApi.get("/agent/lifeform/mood") }
export function getLifeformInsights() { return agentApi.get("/agent/lifeform/insights") }
export function getLifeformDreams() { return agentApi.get("/agent/lifeform/dreams") }
export function getLifeformReflection() { return agentApi.get("/agent/lifeform/reflection") }
export function forceLifeformCycle() { return agentApi.post("/agent/lifeform/cycle") }

export function executeWorkflow(message) { return agentApi.post("/agent/workflow/execute", { message }) }
export function getWorkflowHistory() { return agentApi.get("/agent/workflow/history") }
export function getWorkflowTemplates() { return agentApi.get("/agent/workflow/templates") }

export function getMemoryDecay() { return agentApi.post("/memory/cleanup", { days_old: 30 }) }
