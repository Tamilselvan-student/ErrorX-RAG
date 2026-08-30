/**
 * Thin API client for the ErrorLens backend.
 * All calls are proxied through the Vite dev server (`/api`).
 */

const BASE = "/api";

async function request(path, options = {}) {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  // Handle non-JSON or empty bodies gracefully.
  const contentType = resp.headers.get("content-type") || "";
  let body = null;
  if (contentType.includes("application/json")) {
    body = await resp.json();
  } else {
    body = await resp.text();
  }

  if (!resp.ok) {
    const message =
      (body && (body.detail || body.message)) ||
      body ||
      `Request failed with status ${resp.status}`;
    const error = new Error(message);
    error.status = resp.status;
    error.code = body?.error_code;
    throw error;
  }
  return body;
}

export function health() {
  return request("/health");
}

export function analyze(payload) {
  return request("/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function search(payload) {
  return request("/search", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getExamples() {
  return request("/examples");
}

export function listDocuments() {
  return request("/documents");
}

export function getDocument(filename) {
  return request(`/documents/${encodeURIComponent(filename)}`);
}

export const LANGUAGES = [
  { value: "auto", label: "Auto Detect" },
  { value: "java", label: "Java" },
  { value: "python", label: "Python" },
  { value: "javascript", label: "JavaScript" },
  { value: "sql", label: "SQL" },
  { value: "react", label: "React" },
];