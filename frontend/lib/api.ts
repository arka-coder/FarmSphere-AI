/**
 * FarmSphere AI — API Client
 * Typed interface to the FastAPI backend.
 */

const rawApiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_BASE = rawApiBase.endsWith('/') ? rawApiBase.slice(0, -1) : rawApiBase;

export interface ChatRequest {
  message: string;
  farmer_id?: string;
  farmer_name?: string;
  location?: string;
  district?: string;
  crop_type?: string;
  season?: string;
  language?: "en" | "hi" | "bn";
  image_base64?: string;
}

export interface DiseaseInfo {
  name: string;
  confidence: number;
  severity: "mild" | "moderate" | "severe" | "none" | "unknown";
  symptoms: string[];
  alternatives: { name: string; confidence: number }[];
  hitl_required: boolean;
}

export interface AgentTrace {
  agent: string;
  display_name: string;
  duration_ms: number;
  status: "success" | "error" | "skipped";
  status_icon: string;
  output_summary: string;
  started_at: number;
}

export interface SourceDocument {
  title: string;
  source: string;
  relevance_score: number;
  excerpt: string;
}

export interface RiskScores {
  disease_risk: number;
  pest_risk: number;
  weather_risk: number;
  irrigation_risk: number;
  market_risk: number;
  overall_risk: number;
}

export interface WeatherData {
  location: string;
  temperature: number;
  feels_like: number;
  humidity: number;
  wind_speed: number;
  weather_condition: string;
  rainfall_24h: number;
  pressure: number;
  forecast: {
    day: string;
    condition: string;
    temp_max: number;
    temp_min: number;
    humidity: number;
    rain_chance: number;
  }[];
  source: string;
}

export interface Alert {
  type: "weather" | "disease" | "pest" | "market";
  severity: "low" | "medium" | "high" | "critical";
  title: string;
  message: string;
  action: string;
}

export interface ChatResponse {
  session_id: string;
  response: string;
  intent: string;
  agents_invoked: string[];
  execution_timeline: AgentTrace[];
  reasoning_chain: string[];
  confidence_breakdown: Record<string, number>;
  explanation: string;
  disease: DiseaseInfo | null;
  weather: WeatherData | null;
  weather_advice: string;
  risk_scores: RiskScores | null;
  risk_summary: string;
  preventive_actions: string[];
  active_alerts: Alert[];
  applicable_schemes: object[];
  market_prices: object | null;
  upcoming_tasks: object[];
  satellite_data: object | null;
  simulation_results: object | null;
  source_documents: SourceDocument[];
  evaluation: {
    overall_score: number;
    passed_checks: number;
    total_checks: number;
    evaluation_summary: string;
    metrics: object[];
  };
  total_latency_ms: number;
  errors: string[];
}

// ── API Functions ─────────────────────────────────────────────────────────────

export async function sendChat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function streamChat(
  req: ChatRequest,
  onAgentProgress: (agent: string, message: string) => void,
  onResult: (data: ChatResponse) => void,
  onError: (error: string) => void,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.type === "agent_progress") {
            onAgentProgress(data.agent, data.message);
          } else if (data.type === "result") {
            onResult(data as ChatResponse);
          } else if (data.type === "error") {
            onError(data.message);
          }
        } catch {}
      }
    }
  }
}

export async function uploadImage(
  file: File,
  cropType: string,
  language: string = "en",
  farmerName: string = "Farmer",
): Promise<ChatResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("crop_type", cropType);
  formData.append("language", language);
  formData.append("farmer_name", farmerName);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getWeather(): Promise<WeatherData> {
  const res = await fetch(`${API_BASE}/api/weather`);
  return res.ok ? res.json() : Promise.reject("Weather unavailable");
}

export async function getAlerts(): Promise<{ alerts: Alert[] }> {
  const res = await fetch(`${API_BASE}/api/alerts`);
  return res.ok ? res.json() : { alerts: [] };
}

export async function getMarketData(crop?: string): Promise<object> {
  const url = crop ? `${API_BASE}/api/market?crop=${crop}` : `${API_BASE}/api/market`;
  const res = await fetch(url);
  return res.ok ? res.json() : {};
}

export async function getSchemes(): Promise<{ schemes: object[] }> {
  const res = await fetch(`${API_BASE}/api/schemes`);
  return res.ok ? res.json() : { schemes: [] };
}

export async function getSatelliteData(crop: string = "tomato"): Promise<object> {
  const res = await fetch(`${API_BASE}/api/satellite?crop=${crop}`);
  return res.ok ? res.json() : {};
}

export async function getCalendar(crop: string = "tomato"): Promise<object> {
  const res = await fetch(`${API_BASE}/api/calendar?crop=${crop}`);
  return res.ok ? res.json() : {};
}

export async function getHealth(): Promise<object> {
  const res = await fetch(`${API_BASE}/health`);
  return res.ok ? res.json() : { status: "unknown" };
}
