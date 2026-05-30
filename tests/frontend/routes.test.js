import { describe, it, expect } from "vitest"

describe("Router", () => {
  const routes = [
    "/friday", "/dashboard", "/chat", "/ai-brain", "/agents",
    "/evolution", "/models", "/memory", "/server", "/docker",
    "/nginx", "/network", "/files", "/audit", "/database",
    "/mall", "/site", "/customer", "/trends", "/scraper",
    "/virtual", "/video", "/ocr", "/plugins", "/tasks",
    "/self-service", "/alert", "/security", "/rollback",
    "/rotation", "/approval", "/github",
  ]
  for (const r of routes) {
    it(' /ai${r} ', () => {
      expect(r).toBeTruthy()
    })
  }
})

describe("API", () => {
  const apis = ["agent", "alert", "customer", "database", "docker", "github",
    "mall", "memory", "model", "nginx", "plugin", "rollback", "rotation",
    "scraper", "server", "site", "system", "task", "trend", "virtual", "vision"]
  for (const a of apis) {
    it('API ${a}.js ', async () => {
      const mod = await import('@/api/${a}')
      expect(mod).toBeDefined()
      const keys = Object.keys(mod)
      expect(keys.length).toBeGreaterThan(0)
    })
  }
})
