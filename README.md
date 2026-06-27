# 🌾 FarmSphere AI

## Explainable Multi-Agent Agricultural Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-orange)](https://langchain-ai.github.io/langgraph/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-purple)](https://ai.google.dev)

> **FarmSphere AI** is not a chatbot. It is a long-term agricultural companion powered by 17 specialized AI agents that collaborate through LangGraph to provide explainable, multimodal, and proactive agricultural intelligence.

---

## 🏆 Competition Highlights

| Feature | Implementation |
|---|---|
| ✅ Multi-agent orchestration | LangGraph StateGraph with 17 agents |
| ✅ Gemini Vision | Disease detection from leaf/fruit images |
| ✅ ChromaDB RAG | ICAR document retrieval with source citations |
| ✅ Long-term memory | PostgreSQL conversation history |
| ✅ Explainability | Full reasoning chain + confidence breakdown |
| ✅ Human-in-the-Loop | Auto-triggered when confidence < 75% |
| ✅ Satellite intelligence | NDVI vegetation health via GEE |
| ✅ Scenario Simulation ⭐ | "What if rainfall doubles?" predictive modeling |
| ✅ Multilingual | English, Hindi, Bengali |
| ✅ Evaluation framework | Faithfulness, RAG quality, hallucination detection |
| ✅ Observability | Prometheus metrics, structured logs, execution traces |

---

## 🏗️ Architecture

```
User Request
     ↓
Orchestrator Agent (Intent Classification)
     ↓
┌─────────────────────────────────────────────┐
│          Layer 1: Core Agents               │
│  Disease Agent    →  Gemini Vision          │
│  Knowledge Agent  →  ChromaDB RAG           │
│  Weather Agent    →  OpenWeatherMap         │
│  Seasonal Agent   →  Crop Calendar Logic   │
│  Risk Agent       →  Multi-factor Scoring  │
│  Recommendation   →  Gemini Synthesis      │
│  Explainability   →  Reasoning Chain       │
└─────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│       Layer 2: Supporting Agents            │
│  Translation · Memory · Scheme              │
│  Market · Crop Calendar · Alert             │
└─────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────┐
│       Layer 3: Advanced Modules             │
│  Satellite (GEE/NDVI) · Community          │
│  Sustainability · Scenario Simulation ⭐   │
└─────────────────────────────────────────────┘
     ↓
Final Response with:
  • Diagnosis + Confidence Score
  • Reasoning Chain
  • Source Citations
  • Risk Scores
  • Execution Timeline
```

---

## ⭐ Hidden Feature: Scenario Simulation

Ask **"What if rainfall doubles next week?"** and FarmSphere simulates:

| Factor | Current | Simulated | Change |
|---|---|---|---|
| Disease Risk | 35% | 72% | **+106%** |
| Pest Risk | 25% | 45% | **+80%** |
| Est. Yield | 100% | 93% | **-7%** |
| Water Stress | Normal | HIGH | — |

With adapted action plan and critical window identification.

---

## 📂 Project Structure

```
farmsphere-ai/
├── backend/
│   ├── main.py                      # FastAPI entry point
│   ├── config.py                    # Settings management
│   ├── agents/
│   │   ├── orchestrator.py          # Intent routing (Layer 1)
│   │   ├── disease_agent.py         # Gemini Vision diagnosis (Layer 1)
│   │   ├── weather_agent.py         # OpenWeather integration (Layer 1)
│   │   ├── knowledge_agent.py       # ChromaDB RAG (Layer 1)
│   │   ├── seasonal_agent.py        # Crop lifecycle (Layer 1)
│   │   ├── risk_agent.py            # Risk scoring (Layer 1)
│   │   ├── recommendation_agent.py  # Final synthesis (Layer 1)
│   │   ├── explainability_agent.py  # Reasoning chain (Layer 1)
│   │   ├── supporting_agents.py     # Layer 2 (6 agents)
│   │   ├── advanced_agents.py       # Layer 3 (3 agents)
│   │   └── scenario_simulation_agent.py  # ⭐ Hidden feature
│   ├── graph/
│   │   ├── state.py                 # LangGraph FarmSphereState
│   │   └── workflow.py              # StateGraph definition
│   ├── database/
│   │   ├── postgres.py              # SQLAlchemy models
│   │   └── chromadb_client.py       # Vector DB + demo data
│   ├── evaluation/
│   │   └── evaluator.py             # 5 evaluation metrics
│   └── observability/
│       └── observability.py         # Prometheus + Redis + logging
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Landing page
│   │   ├── dashboard/page.tsx       # Main dashboard
│   │   ├── chat/page.tsx            # AI chat interface
│   │   ├── disease/page.tsx         # Disease detection
│   │   ├── simulation/page.tsx      # ⭐ Scenario simulator
│   │   ├── schemes/page.tsx         # Government schemes
│   │   └── satellite/page.tsx       # NDVI satellite view
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatWindow.tsx       # SSE streaming chat
│   │   │   ├── MessageBubble.tsx    # Rich message with panels
│   │   │   ├── ConfidenceGauge.tsx  # Animated confidence display
│   │   │   ├── AgentTimeline.tsx    # Deep Research-style timeline
│   │   │   ├── SourceCards.tsx      # Citation cards
│   │   │   └── ChatInput.tsx        # Drag-drop + language switcher
│   │   └── layout/
│   │       └── Sidebar.tsx
│   └── lib/
│       └── api.ts                   # Typed API client
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### Option A: Docker (Recommended)

```bash
# 1. Clone and configure
git clone <repo-url>
cd farmsphere-ai
cp .env.example .env
# Edit .env with your API keys

# 2. Start all services
docker-compose up -d

# 3. Open browser
open http://localhost:3000
```

### Option B: Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your API keys

uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## 🔑 API Keys Setup

| Key | Where to get | Required? |
|---|---|---|
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com) | ✅ Core agents |
| `OPENWEATHER_API_KEY` | [OpenWeatherMap](https://openweathermap.org/api) | ✅ Weather |
| `TAVILY_API_KEY` | [Tavily](https://tavily.com) | Optional |
| GEE Service Account | [Google Cloud](https://console.cloud.google.com) | Optional (mock works) |

> Without API keys, the system runs in **Demo Mode** with realistic mock data. All UI features work.

---

## 📊 Evaluation Framework

FarmSphere includes a built-in evaluation suite:

| Metric | Description | Threshold |
|---|---|---|
| **Faithfulness** | Answer grounded in ICAR sources | ≥ 75% |
| **RAG Quality** | Retrieval relevance + diversity | ≥ 65% |
| **Latency** | End-to-end response time | < 5 seconds |
| **Confidence Quality** | Disease diagnosis calibration | ≥ 75% |
| **Hallucination Risk** | Unsupported claim detection | < 20% |

Access at: `GET /api/metrics/evaluation`

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat` | Main multi-agent chat |
| POST | `/api/chat/stream` | SSE streaming chat |
| POST | `/api/upload` | Image disease detection |
| GET | `/api/weather` | Current weather |
| GET | `/api/alerts` | Proactive alerts |
| GET | `/api/market` | Crop market prices |
| GET | `/api/schemes` | Government schemes |
| GET | `/api/satellite` | NDVI satellite data |
| GET | `/api/calendar` | Crop calendar |
| GET | `/health` | Service health check |
| GET | `/metrics` | Prometheus metrics |

---

## 🧪 Testing

```bash
# Backend
cd backend
pytest tests/ -v

# API test
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "My tomato leaves have brown spots", "crop_type": "tomato"}'
```

---

## 🏛️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Gemini 2.0 Flash |
| Vision | Gemini Vision |
| Agent Framework | LangGraph 0.2 |
| Backend | FastAPI + Uvicorn |
| Frontend | Next.js 15 + Tailwind CSS |
| Vector DB | ChromaDB |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Search | Tavily |
| Satellite | Google Earth Engine |
| Observability | Prometheus + structlog |
| Deployment | Docker Compose |

---

## 👨‍💻 Author

Built for the **Agents for Good** hackathon track.

FarmSphere AI — Helping Indian farmers make better decisions through explainable AI.
