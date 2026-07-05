# GuardianAI

**"Trust Every Decision. Verify Every Action."**

GuardianAI is a runtime cybersecurity guardrail gateway layer designed for autonomous AI agents. Unlike typical static content filtering systems that screen text inputs, GuardianAI continuously monitors runtime behavioral sequences, enforces deterministic access policies, sanitizes outbound data egress using shadow tokenization, and provides dual independent kill paths to isolate compromised agent runtimes.

---

## 🗺️ System Architecture Diagram

```
User Request
    │
    ▼
[Gateway app.py] ──► [Rate Limiter] ──► [Cascade Inspector] ──► [Policy Engine] 
                         (Throttling)       (Regex/Embeddings)       (YAML ACL)
                                                                          │
                                                                          ▼
Agent Output ◄── [Output Inspector] ◄── [Tool Monitor] ◄── [Risk Aggregator] 
                   (Redaction Check)    (Argument Scans)      (Threat Score)
                         │
                         ▼
             [Behavioral Detector] (Z-Score Rate anomaly check -> Revoke active session)
```

---

## 📂 Repository File Structure

```
guardian-ai/
├── gateway/
│   └── app.py                     (FastAPI Gateway, HTTP routers, sliding-window rate checks)
├── policy/
│   ├── policy.yaml                (YAML Access Control List mapping agent-to-tool rules)
│   └── engine.py                  (YAML parser enforcing fail-closed authorizations)
├── risk/
│   └── orchestrator.py            (Aggregates cascade & policy scores into 0-100 index)
├── action/
│   └── controller.py              (Verdict thresholds & Kill Path 1 session isolation)
├── tools/
│   └── monitor.py                 (Post-execution scope check & Kill Path 2 trigger)
├── logger/
│   └── app.py                     (Writes signed audit events to database)
├── agents/
│   └── config.py                  (Queries SQLite agent configs)
├── database/
│   ├── connection.py              (SQLite schemas, pre-seeded agent rules, and baseline metrics)
│   └── guardian.db                (SQLite Database file)
├── dashboard/
│   └── server.py                  (WebSocket server hub for dashboard UI events)
├── notifications/
│   └── dispatcher.py              (Outbound notification webhook stub)
├── agent/
│   └── client.py                  (Importable GatewayClient helper wrapping calls)
├── detectors/
│   ├── cascade.py                 (Layer A Regex, Layer B Embeddings, Layer C LLM Judge)
│   ├── behavior_detector.py       (Z-Score count calculations, cold-start guard, stddev floor)
│   └── output_inspector.py        (PII scans, shadow tokenization, redaction block overrides)
├── demo/
│   ├── scenario_clean.py             (Verify safe request flow)
│   ├── scenario_direct_injection.py  (Verify Layer A/B prompt injection block - 403)
│   ├── scenario_subtle_injection.py  (Verify z-score anomaly rates lockdown - 401)
│   ├── scenario_burst.py             (Verify sliding-window rate block - 429)
│   ├── scenario_output_leak.py       (Verify shadow tokenization credential redaction)
│   ├── benign_test_set.json          (Reference benign queries)
│   └── baseline_seed_data.json       (Historical baseline metrics)
├── src/                           (Next.js React Frontend files)
├── Dockerfile.backend             (FastAPI container configuration)
├── Dockerfile.frontend            (Next.js container configuration)
├── docker-compose.yml             (Orchestrator linking split Dockerfiles)
└── requirements.txt               (Python dependencies: FastAPI, PyYAML, NumPy, sentence-transformers)
```

---

## 🛠️ Technology Stack
- **Core Engine:** Python 3.10, FastAPI, Uvicorn, SQLite
- **Security NLP:** SentenceTransformers (`all-MiniLM-L6-v2`), NumPy, PyYAML
- **Frontend Dashboard:** Next.js 16 (React 19), TailwindCSS, Recharts, GSAP, Lenis, React Three Fiber (Three.js WebGL Canvas)
- **Containerization:** Docker, Docker Compose

---

## ⚙️ Quick Start Installation

### Option 1: Running Locally (Recommended for development)

1. **Start the FastAPI Backend:**
   ```bash
   pip install -r requirements.txt
   uvicorn gateway.app:app --reload --port 8000
   ```
2. **Start the Next.js Frontend:**
   ```bash
   npm run build
   npm run dev
   ```
   Open **[http://localhost:3000](http://localhost:3000)** in your browser. The frontend dashboard connects via WebSockets to port 8000 automatically.

### Option 2: Running via Docker Compose

```bash
docker compose build
docker compose up -d
```
This builds and launches the frontend on port 3000 and the backend on port 8000.

---

## 🧪 Running Scenario Tests

Verify the gateway's defenses using the test files in the `demo/` folder:
```bash
python demo/scenario_clean.py
python demo/scenario_direct_injection.py
python demo/scenario_subtle_injection.py
python demo/scenario_burst.py
python demo/scenario_output_leak.py
```

---

## 📈 System Benchmarks (docs/results.md)
Running `python demo/run_benchmarks.py` produces measured results stored at `docs/results.md`.

Summary (from `docs/results.md`) — **30 benign + 30 adversarial prompts**:
- **Detection Rate (Recall):** 100.00%
- **False Positive Rate (FPR):** 0.00%
- **Precision:** 100.00%
- **Average Threat Detection Time:** 22.86 ms
- **Blocked Prompt Injections:** 28 / 30
- **Rate-Limited Request Bursts Intercepted:** 5

See [docs/results.md](docs/results.md) for full metrics and dataset details.

## 🔐 Status Code Semantics
- `403`: Blocked before execution by prompt inspection or policy rules.
- `401`: Session isolated after behavioral anomaly or tool-monitor kill; the runtime was shut down as a defense.
- `429`: Rate limited before inspection, stopping floods early and preserving the gateway.

## ⚠️ Prototype Layer C Note
- Layer C currently uses a lightweight heuristic for the prototype. In production, replace it with a dedicated safety classifier such as Llama Guard or a similar model-backed safety layer.

---

## 🛑 Known Limitations & Production Roadmap

### 1. Hybrid Semantic Reasoning Layer
- **Current Limitation:** The offline Semantic Judge uses a structured heuristic rule parser that outputs a JSON schema to mirror an LLM.
- **Production Roadmap:** Transition to a hosted LLM (e.g. Llama Guard 3, Gemini Flash) or custom fine-tuned safety adapters returning identical JSON responses `{ "decision", "reason", "confidence" }`.

### 2. In-Memory Session Rate Cache
- **Current Limitation:** Rate limiting counters, agent tokens, and sliding-window timestamp histories are tracked in Python process memory.
- **Production Roadmap:** Migrate to a centralized Redis cache cluster to ensure horizontal scalability across multiple gateway nodes.

### 3. Static Behavioral Baseline Seeding
- **Current Limitation:** Baseline operational Z-scores rely on pre-populated historical metrics loaded during sqlite startup.
- **Production Roadmap:** Implement a continuous profiling pipeline that updates agent behavioral metrics asynchronously using real-time operational flows.

### 4. GPU-Accelerated Embeddings
- **Current Limitation:** SentenceTransformer runs on local CPU, which can cause latency spikes on cold starts.
- **Production Roadmap:** Deploy embedding models on dedicated GPU clusters (or utilize hosted APIs) to guarantee sub-15ms inference latencies.
