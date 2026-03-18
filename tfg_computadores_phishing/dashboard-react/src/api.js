const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "";

async function fetchJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "X-API-Key": API_KEY,
    },
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`API ${response.status} ${response.statusText}: ${detail}`);
  }
  return response.json();
}

export function getHealth() {
  return fetchJson("/api/v1/health");
}

export function getRuns() {
  return fetchJson("/api/v1/runs");
}

export function getRunSummary(runId) {
  return fetchJson(`/api/v1/runs/${runId}/summary`);
}

export function getRunThresholds(runId) {
  return fetchJson(`/api/v1/runs/${runId}/thresholds`);
}

export function getRunConfusion(runId) {
  return fetchJson(`/api/v1/runs/${runId}/confusion-matrix`);
}

export function getTrainingMetadata() {
  return fetchJson("/api/v1/training/metadata");
}

export function getMessages({ runId, limit = 100, offset = 0, pred = "", scoreMin = "" }) {
  const params = new URLSearchParams();
  if (runId) params.set("run_id", runId);
  if (pred !== "") params.set("pred", pred);
  if (scoreMin !== "") params.set("score_min", scoreMin);
  params.set("limit", String(limit));
  params.set("offset", String(offset));
  return fetchJson(`/api/v1/messages?${params.toString()}`);
}
