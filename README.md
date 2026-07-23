<div align="center">

# 🌾 FarmSphere AI

### Explainable Multi-Agent Agricultural Intelligence Platform

*Empowering India's 140 million farmers with a team of 17 specialized AI agents — collaborating in real-time to deliver precision agricultural intelligence.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-FF6B35?style=flat-square&logo=chainlink&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-8B5CF6?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-E94560?style=flat-square&logo=databricks&logoColor=white)](https://www.trychroma.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

<br/>

> **FarmSphere AI** is not a chatbot. It is a **long-term agricultural companion** powered by 17 specialized AI agents collaborating through LangGraph — delivering explainable, multimodal, and proactive agricultural intelligence, built for the farmers of India.

<br/>

[🚀 Quick Start](#-quick-start) · [🏗️ Architecture](#️-architecture) · [⭐ Features](#-features-deep-dive) · [📡 API Reference](#-api-reference) · [📊 Evaluation](#-evaluation-framework) · [🤝 Contributing](#-contributing)

---

</div>

## 🌟 What Makes FarmSphere AI Different?

Most agricultural apps give farmers a lookup table. FarmSphere AI gives them **an intelligent team of specialists** — an agronomist, plant pathologist, meteorologist, data scientist, and government scheme expert — available 24/7, in their own language.

| Traditional Apps | FarmSphere AI |
|---|---|
| Static crop guides | 17 AI agents collaborating in real-time |
| Single-source answers | RAG-backed ICAR citations with confidence scores |
| English-only | Hindi · Bengali · English multilingual support |
| Upload photo → get a name | Gemini Vision diagnosis + treatment plan + risk assessment |
| No memory | Long-term PostgreSQL conversation history per farmer |
| "It might rain" | NDVI satellite analysis + scenario simulation |

---

## 🏆 Platform Capabilities

| Capability | Implementation | Status |
|---|---|---|
| **Multi-agent orchestration** | LangGraph `StateGraph` with 17 agents in 3 layers | ✅ Live |
| **Vision AI disease diagnosis** | Gemini Vision — leaf & fruit disease detection | ✅ Live |
| **Knowledge retrieval (RAG)** | ChromaDB vector store with ICAR document citations | ✅ Live |
| **Long-term farmer memory** | PostgreSQL conversation history per farmer ID | ✅ Live |
| **Explainable AI** | Full reasoning chain + per-agent confidence breakdown | ✅ Live |
| **Human-in-the-Loop (HITL)** | Auto-triggered escalation when confidence < 75% | ✅ Live |
| **Satellite intelligence** | NDVI vegetation health mapping via Google Earth Engine | ✅ Live |
| **Scenario Simulation ⭐** | *"What if rainfall doubles?"* — predictive risk modeling | ✅ Live |
| **Multilingual NLP** | Seamless English ↔ Hindi ↔ Bengali | ✅ Live |
| **Plant Science Engine** | Deep botanical, physiological & agronomic knowledge | ✅ Live |
| **Evaluation framework** | Faithfulness · RAG quality · Hallucination detection | ✅ Live |
| **Observability** | Prometheus metrics · Structured logs · Agent traces | ✅ Live |

---

## 🏗️ Architecture

FarmSphere uses a **3-layer LangGraph `StateGraph`** that routes queries intelligently through specialized agents before synthesizing a final, explainable response.

```
┌─────────────────────────────────────────────────────────────┐
│                      USER REQUEST                           │
│           (Text · Image · Multilingual)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  Orchestrator Agent │  ← Intent classification
                │  (Intent + Routing) │    & query decomposition
                └──────────┬──────────┘
                           │
          ┌────────────────▼────────────────┐
          │        LAYER 1: CORE            │
          │                                 │
          │  🔬 Disease Agent               │ ← Gemini Vision multimodal
          │  📚 Knowledge Agent             │ ← ChromaDB ICAR RAG
          │  🌤️ Weather Agent               │ ← OpenWeatherMap live data
          │  📅 Seasonal Agent              │ ← Crop lifecycle logic
          │  ⚠️  Risk Agent                 │ ← Multi-factor risk scoring
          │  💡 Recommendation Agent       │ ← Gemini synthesis
          │  🧠 Explainability Agent       │ ← Reasoning chain builder
          │  🌿 Plant Science Agent        │ ← Deep botanical engine
          └────────────────┬────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │      LAYER 2: SUPPORTING        │
          │                                 │
          │  🌐 Translation Agent           │ ← Hindi · Bengali · English
          │  💾 Memory Agent               │ ← PostgreSQL history
          │  🏛️  Scheme Agent               │ ← Government program lookup
          │  📈 Market Agent               │ ← Real-time crop prices
          │  📆 Calendar Agent             │ ← Sowing/harvest windows
          │  🚨 Alert Agent                │ ← Proactive notifications
          └────────────────┬────────────────┘
                           │
          ┌────────────────▼────────────────┐
          │      LAYER 3: ADVANCED          │
          │                                 │
          │  🛰️  Satellite Agent             │ ← GEE / NDVI analysis
          │  👥 Community Agent            │ ← Crowd wisdom insights
          │  ♻️  Sustainability Agent        │ ← Eco-impact scoring
          │  🔮 Scenario Simulation ⭐     │ ← "What if?" predictions
          └────────────────┬────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     FINAL RESPONSE                          │
│                                                             │
│  📋 Diagnosis        → Disease name + confidence %         │
│  🔗 Reasoning Chain  → Per-agent decision audit trail      │
│  📑 Source Citations → ICAR document references            │
│  📊 Risk Scores      → Numeric multi-factor breakdown      │
│  ⏱️  Execution Trace  → Agent timeline (ms per step)        │
└─────────────────────────────────────────────────────────────┘
```

### Shared Agent State

Every agent reads and writes to a single `FarmSphereState` TypedDict — enabling seamless, context-aware collaboration:

```python
FarmSphereState = {
    "user_message":       str,         # Original query
    "crop_type":          str,         # Detected / specified crop
    "location":           str,         # Farmer's region
    "season":             str,         # Current agricultural season
    "image_base64":       str | None,  # Uploaded leaf/crop image
    "language":           str,         # en | hi | bn
    "knowledge_context":  str,         # RAG-retrieved ICAR excerpts
    "weather_context":    dict,        # Live weather conditions
    "risk_scores":        dict,        # Disease / pest / yield risk %
    "diagnosis":          str,         # Disease/condition identified
    "confidence_score":   float,       # 0.0 – 1.0 diagnosis certainty
    "reasoning_chain":    list,        # Agent-by-agent reasoning steps
    "source_documents":   list,        # Cited sources with relevance scores
    "hitl_required":      bool,        # Human expert escalation flag
    "agent_traces":       list,        # Execution timeline per agent
    "final_response":     str,         # Synthesized final answer
}
```

---

## ⭐ Features Deep Dive

### 🔬 AI-Powered Disease Detection

Upload a photo of a diseased leaf or fruit. Gemini Vision analyzes visual symptoms, cross-references against the ICAR plant pathology knowledge base, and returns:

- **Disease name** with taxonomic classification
- **Confidence score** (triggers HITL escalation if < 75%)
- **Stage of infection** — early, moderate, or severe
- **Treatment protocol** — chemical + organic options with dosages
- **Preventive measures** tailored to the current season

```bash
# Example — image-based diagnosis
curl -X POST http://localhost:8000/api/upload \
  -F "file=@tomato_leaf.jpg" \
  -F "crop_type=tomato" \
  -F "location=Punjab"
```

---

### 🔮 Scenario Simulation Engine ⭐

FarmSphere's standout capability. Ask *"What if rainfall doubles next week?"* and the simulation engine models cascading effects across your entire crop ecosystem:

| Factor | Current | Simulated | Δ Change |
|---|---|---|---|
| Disease Risk | 35% | 72% | **+106% ↑** |
| Pest Risk | 25% | 45% | **+80% ↑** |
| Estimated Yield | 100% | 93% | **-7% ↓** |
| Water Stress | Normal | HIGH | 🔴 Critical |
| Fungal Pressure | Low | Very High | 🔴 Critical |
| Irrigation Need | 40 mm | 0 mm | **-100% ↓** |

Returns an **adapted action plan** with critical intervention windows and priority-ranked recommendations.

---

### 🌿 Plant Science Expert Engine

A deep botanical knowledge engine backed by 77,000+ bytes of curated agronomic data. Adapts its depth to the user — simple analogies for farmers, full biochemistry for researchers:

- **Photosynthesis pathways** — C3, C4, CAM mechanisms + Hatch-Slack cycle
- **Plant hormones** — IAA, GA₃, Cytokinins, ABA, Ethylene, Brassinosteroids
- **Soil biology** — Mycorrhizae (AM/ECM), Rhizobium, Azospirillum, PSB
- **Biofertilizers** — Mechanism and application of 8+ microbial inoculants
- **Stress physiology** — Drought, salinity, heat, waterlogging response pathways
- **Allelopathy & companion planting** — Intercropping synergy tables

---

### 🛰️ Satellite Intelligence (NDVI)

Real-time vegetation health analysis via Google Earth Engine:

- **Field-scale NDVI maps** with stress zone detection
- **Historical trend analysis** for yield forecasting
- **Rainfall anomaly overlays** for proactive alerts

> 💡 Works in **mock mode** without GEE credentials — ideal for development and demos.

---

### 🧠 Full Explainability & Audit Trail

Every answer includes a complete, per-agent reasoning chain:

```json
{
  "reasoning_chain": [
    { "agent": "orchestrator",        "decision": "Disease query detected",                    "confidence": 0.94 },
    { "agent": "disease_agent",       "decision": "Brown spots + yellow halo → Late Blight",   "confidence": 0.87 },
    { "agent": "knowledge_agent",     "decision": "Retrieved 3 ICAR docs on P. infestans",     "sources": 3       },
    { "agent": "risk_agent",          "decision": "High humidity + 18°C → spread risk: 82%",   "confidence": 0.91 },
    { "agent": "recommendation_agent","decision": "Mancozeb 75% WP @ 2.5 g/L recommended",    "confidence": 0.88 }
  ],
  "execution_time_ms": 2847,
  "hitl_triggered": false
}
```

---

## 📂 Project Structure

```
farmsphere-ai/
│
├── 📁 backend/
│   ├── main.py                          # FastAPI entry point + all API routes
│   ├── config.py                        # Pydantic settings from environment
│   ├── requirements.txt                 # Python dependencies
│   ├── Dockerfile
│   │
│   ├── 📁 agents/
│   │   ├── orchestrator.py              # Intent classification & routing
│   │   ├── disease_agent.py             # Gemini Vision disease diagnosis
│   │   ├── weather_agent.py             # OpenWeatherMap integration
│   │   ├── knowledge_agent.py           # ChromaDB RAG retrieval
│   │   ├── plant_science_agent.py       # Deep botanical knowledge engine
│   │   ├── seasonal_agent.py            # Crop lifecycle + sowing calendar
│   │   ├── risk_agent.py                # Multi-factor risk scoring
│   │   ├── recommendation_agent.py      # Final Gemini synthesis
│   │   ├── explainability_agent.py      # Reasoning chain builder
│   │   ├── supporting_agents.py         # Layer 2: 6 supporting agents
│   │   ├── advanced_agents.py           # Layer 3: Satellite + Community
│   │   ├── scenario_simulation_agent.py # ⭐ "What if?" simulation engine
│   │   ├── agriculture_kb.py            # Curated agronomic knowledge base (77KB)
│   │   └── llm_helper.py                # Gemini thinking-mode wrapper
│   │
│   ├── 📁 graph/
│   │   ├── state.py                     # FarmSphereState TypedDict definition
│   │   └── workflow.py                  # LangGraph StateGraph compilation
│   │
│   ├── 📁 database/
│   │   ├── postgres.py                  # SQLAlchemy models + session factory
│   │   └── chromadb_client.py           # Vector DB client + ICAR seed data
│   │
│   ├── 📁 evaluation/
│   │   └── evaluator.py                 # 5-metric evaluation framework
│   │
│   └── 📁 observability/
│       └── observability.py             # Prometheus + structlog + Redis
│
├── 📁 frontend/
│   ├── 📁 app/
│   │   ├── page.tsx                     # Landing page
│   │   ├── dashboard/page.tsx           # Main analytics dashboard
│   │   ├── chat/page.tsx                # SSE streaming AI chat
│   │   ├── disease/page.tsx             # Disease detection upload UI
│   │   ├── simulation/page.tsx          # ⭐ Interactive scenario simulator
│   │   ├── schemes/page.tsx             # Government scheme browser
│   │   └── satellite/page.tsx           # NDVI satellite map viewer
│   │
│   ├── 📁 components/
│   │   ├── 📁 chat/
│   │   │   ├── ChatWindow.tsx           # Real-time SSE streaming chat
│   │   │   ├── MessageBubble.tsx        # Rich messages with embedded panels
│   │   │   ├── ConfidenceGauge.tsx      # Animated confidence ring
│   │   │   ├── AgentTimeline.tsx        # Deep Research-style agent timeline
│   │   │   ├── ReasoningChain.tsx       # Expandable reasoning audit trail
│   │   │   ├── LiveContextPanel.tsx     # Live weather + crop context
│   │   │   ├── SourceCards.tsx          # ICAR citation cards with relevance
│   │   │   └── ChatInput.tsx            # Drag-drop upload + language picker
│   │   └── 📁 layout/
│   │       ├── Sidebar.tsx              # Navigation sidebar
│   │       └── DigitalClock.tsx         # Live IST clock
│   │
│   └── 📁 lib/
│       └── api.ts                       # Fully typed API client
│
├── docker-compose.yml                   # Full-stack orchestration
├── .env.example                         # Environment variable template
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | Backend runtime |
| Node.js | 20+ | Frontend runtime |
| Docker | Latest | Recommended for full stack |

### Option A: Docker (Recommended — One Command)

```bash
# 1. Clone the repository
git clone https://github.com/your-username/farmsphere-ai.git
cd farmsphere-ai

# 2. Configure environment
cp .env.example .env
# → Edit .env with your API keys (see section below)

# 3. Launch everything
docker-compose up -d

# 4. Open the dashboard
open http://localhost:3000
```

Docker spins up: FastAPI backend · Next.js frontend · PostgreSQL · ChromaDB · Redis · Prometheus

---

### Option B: Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env with your API keys

python -m uvicorn main:app --reload --port 8000
# API Docs → http://localhost:8000/docs
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Dashboard → http://localhost:3000
```

> 💡 **No API keys?** The system runs in **Demo Mode** with realistic mock data. All UI pages, agent flows, and visualizations work out of the box.

---

## 🔑 API Keys & Environment Setup

Copy `.env.example` to `.env` and fill in your credentials:

```env
# ── Required for AI Intelligence ─────────────────────────────────
GOOGLE_API_KEY=your_google_ai_studio_key       # Gemini models + embeddings

# ── Required for Weather Intelligence ────────────────────────────
OPENWEATHER_API_KEY=your_openweather_key       # Live weather + 5-day forecast

# ── Optional (enhances web search capability) ────────────────────
TAVILY_API_KEY=your_tavily_key                 # Real-time web search

# ── Optional (enables real satellite NDVI data) ──────────────────
GEE_MODE=real                                  # Set to "mock" for demo mode
GEE_SERVICE_ACCOUNT=your-sa@project.iam.gserviceaccount.com
GEE_KEY_FILE=gee-key.json

# ── Infrastructure ────────────────────────────────────────────────
DATABASE_URL=postgresql://user:pass@localhost:5432/farmsphere_db
REDIS_URL=redis://localhost:6379/0
```

| Key | Source | Required | Capability Unlocked |
|---|---|---|---|
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com) | ✅ Core | All 17 agents + Vision AI |
| `OPENWEATHER_API_KEY` | [OpenWeatherMap](https://openweathermap.org/api) | ✅ Core | Live weather + forecasts |
| `TAVILY_API_KEY` | [Tavily](https://tavily.com) | Optional | Web search augmentation |
| GEE Service Account | [Google Cloud Console](https://console.cloud.google.com) | Optional | Real NDVI satellite data |

---

## 📡 API Reference

### Core Chat Endpoints

```bash
# Text-based multi-agent chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My tomato leaves have brown spots with yellow halos",
    "crop_type": "tomato",
    "location": "Punjab",
    "language": "en",
    "farmer_id": "farmer_001"
  }'

# Image-based disease detection
curl -X POST http://localhost:8000/api/upload \
  -F "file=@diseased_leaf.jpg" \
  -F "crop_type=rice" \
  -F "location=West Bengal"

# Scenario simulation
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What if rainfall doubles next week?", "crop_type": "wheat"}'
```

### All Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Main multi-agent chat |
| `POST` | `/api/chat/stream` | Server-Sent Events streaming chat |
| `POST` | `/api/upload` | Multipart image disease detection |
| `POST` | `/api/plant-science` | Direct plant science expert query |
| `GET` | `/api/weather` | Current conditions + 5-day forecast |
| `GET` | `/api/alerts` | Proactive pest/disease/weather alerts |
| `GET` | `/api/market` | Real-time crop market prices |
| `GET` | `/api/schemes` | Government scheme lookup + eligibility |
| `GET` | `/api/satellite` | NDVI vegetation health data |
| `GET` | `/api/calendar` | Crop sowing & harvest calendar |
| `GET` | `/health` | Service health check (all dependencies) |
| `GET` | `/metrics` | Prometheus metrics (latency, throughput) |
| `GET` | `/api/metrics/evaluation` | AI quality evaluation report |
| `GET` | `/docs` | Interactive Swagger API documentation |

---

## 📊 Evaluation Framework

FarmSphere includes a built-in, automated evaluation suite that measures AI quality after every inference:

| Metric | Description | Target |
|---|---|---|
| **Faithfulness** | Answer grounded in cited ICAR/IARI sources, not hallucinated | ≥ 75% |
| **RAG Quality** | Retrieval relevance + document diversity score | ≥ 65% |
| **Latency** | End-to-end response generation time | < 5 seconds |
| **Confidence Calibration** | Disease diagnosis accuracy vs. ground truth | ≥ 75% |
| **Hallucination Risk** | Fraction of unsupported claims detected | < 20% |

```bash
# Access live evaluation report
curl http://localhost:8000/api/metrics/evaluation

# Example response
{
  "faithfulness": 0.82,
  "rag_quality": 0.78,
  "avg_latency_ms": 2340,
  "confidence_calibration": 0.86,
  "hallucination_risk": 0.12,
  "overall_score": 0.81
}
```

---

## 🧪 Testing

```bash
# Run backend test suite
cd backend
pytest tests/ -v --tb=short

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Quick live API smoke test
curl http://localhost:8000/health
```

---

## 🏛️ Tech Stack

### AI & Intelligence

| Component | Technology | Purpose |
|---|---|---|
| **LLM** | Gemini 2.0 Flash | Agent reasoning + synthesis |
| **Vision AI** | Gemini Vision | Disease diagnosis from images |
| **Agent Framework** | LangGraph 0.2 | StateGraph orchestration |
| **Embeddings** | `text-embedding-004` | ICAR document vectorization |
| **Vector DB** | ChromaDB | Semantic retrieval + RAG |

### Backend

| Component | Technology | Purpose |
|---|---|---|
| **API** | FastAPI + Uvicorn | High-performance async HTTP |
| **Database** | PostgreSQL 16 / SQLite | Farmer memory + history |
| **Cache** | Redis 7 | Session state + rate limiting |
| **Search** | Tavily API | Real-time web augmentation |
| **Satellite** | Google Earth Engine | NDVI + vegetation mapping |
| **Observability** | Prometheus + structlog | Metrics + structured logging |

### Frontend

| Component | Technology | Purpose |
|---|---|---|
| **Framework** | Next.js 15 (App Router) | SSR + React Server Components |
| **Styling** | Tailwind CSS | Utility-first design system |
| **Language** | TypeScript | End-to-end type safety |
| **Streaming** | Server-Sent Events (SSE) | Real-time agent output |

### Infrastructure

| Component | Technology |
|---|---|
| Containerization | Docker Compose |
| Deployment Target | Any Docker-capable host |

---

## 🌐 Multilingual Support

FarmSphere AI supports three languages via the Translation Agent. Pass `"language"` in any API request or let the system auto-detect from user input:

| Language | Code | Script |
|---|---|---|
| English | `en` | Latin |
| हिंदी (Hindi) | `hi` | Devanagari |
| বাংলা (Bengali) | `bn` | Bengali |

---

## 🤝 Contributing

We welcome contributions from agronomists, ML engineers, and full-stack developers!

```bash
# Fork → clone → branch
git checkout -b feature/your-feature-name

# Make changes, add tests, commit
git commit -m "feat: add soil pH recommendation agent"

# Push and open a Pull Request
git push origin feature/your-feature-name
```

**Priority areas for contribution:**

- 🌾 **More crop data** — extend `agriculture_kb.py` knowledge base
- 🤖 **New specialized agents** — soil health, precision irrigation, pest life cycles
- 🌍 **More languages** — Tamil, Telugu, Marathi, Kannada
- 🧪 **Test coverage** — unit + integration tests for all 17 agents

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for the Agents for Good Hackathon**

*FarmSphere AI — Helping India's farmers make better decisions through explainable, transparent AI.*

</div>
