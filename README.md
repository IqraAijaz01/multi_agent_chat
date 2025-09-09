# Simple Multi‑Agent Chat System

A minimal multi‑agent system where a **Coordinator (Manager)** orchestrates three worker agents—**Research**, **Analysis**, and **Memory**—to answer user questions. Includes a structured memory layer with **keyword + vector similarity search**, adaptive decision‑making, and traceable logs.

> Built to satisfy the provided *Technical Assessment — Simple Multi‑Agent Chat System* requirements.

## Architecture Overview

### Agents
- **Coordinator**: Receives user queries, performs light complexity analysis, plans a sequence (Research → Analysis → Memory), routes tasks, merges results, handles errors/fallbacks, maintains global context and agent state.
- **ResearchAgent**: Simulates retrieval from a **pre‑loaded knowledge base** (mock web). Returns passages with provenance.
- **AnalysisAgent**: Compares, summarizes, and performs simple calculations/reasoning over research results.
- **MemoryAgent**: Manages three memory stores:
  - *Conversation Memory*: chronological messages with timestamps + metadata.
  - *Knowledge Base Memory*: learned facts/findings with provenance.
  - *Agent State Memory*: what each agent learned/accomplished per task.

### Memory & Vector Search
- Keyword index (dict of terms → doc ids) + cosine vector similarity via an in‑memory vector store.
- Structured records: `id, timestamp, type, topic, text, source, agent, confidence, tags`.
- Retrieval API supports: `search_keywords()`, `search_vector()`, merged with recency + confidence ranking.
- Prior memory influences decisions: Coordinator checks for similar existing findings and can **reuse** or **refresh** to avoid redundant work.

### Decision Making & Fallbacks
- Rule‑based complexity scoring (counts verbs/entities) to choose pipeline:
  - **Simple**: Memory look‑up → Research (if needed) → Synthesis.
  - **Complex**: Research → Analysis → Memory update.
- If LLM (Groq) is available (env `GROQ_API_KEY`), the Coordinator uses it for task decomposition; otherwise a rule‑based fallback is used.

### Tracing
- Concise, pretty printed logs for every agent call: payloads, decisions, confidence scores, and memory hits.
- Each scenario run writes a transcript to `outputs/*.txt`.

## How to Run

### 1) Python (no network required)
```bash
cd app
python service.py
```
Follow the console prompts. Type `exit` to quit.

### 2) Run all sample scenarios (writes to `../outputs/`)
```bash
cd app/tests
python run_scenarios.py
```

### 3) Containerized
Build and run with Docker:
```bash
docker compose up --build
```
Then attach to container or use:
```bash
docker compose run --rm app python /app/app/tests/run_scenarios.py
```

## Files
- `app/coordinator.py` – Coordinator (manager + planner)
- `app/agents.py` – ResearchAgent, AnalysisAgent, MemoryAgent
- `app/memory.py` – MemoryLayer with structured stores
- `app/vectorstore.py` – In‑memory keyword + vector (cosine) search
- `app/knowledge_base.py` – Mock knowledge “web” corpus
- `app/logger.py` – Tracing/pretty logs
- `app/service.py` – Console app entry point
- `app/tests/run_scenarios.py` – Runs the 5 required scenarios
- `outputs/` – Scenario transcripts (generated)
- `docker/Dockerfile`, `docker-compose.yaml` – Containerization

## Requirements
Pure Python standard library. No external dependencies required.
(If you want Groq LLM assistance: set `GROQ_API_KEY`; code will still run without it.)

## Memory Design
Each record:
```json
{
  "id": "uuid",
  "timestamp": "2025-09-09T12:00:00Z",
  "type": "conversation|knowledge|agent_state",
  "topic": "transformers",
  "text": "summary or message content",
  "source": "kb:transformers#1",
  "agent": "ResearchAgent",
  "confidence": 0.87,
  "tags": ["transformers","efficiency"]
}
```
Search flow:
1. Keyword filter (OR across tokens) → candidate set.
2. Vector similarity (cosine over bag‑of‑words vectors) → re‑rank.
3. Recency + confidence boost; returns top‑k.

## Evaluation Checklist Mapping
- **System Architecture**: Four classes + cohesive interfaces.
- **Memory Design**: Structured stores + vector search + provenance.
- **Agent Coordination**: Sequenced routing, dependencies, synthesis.
- **Autonomous Reasoning**: Planning + reuse of prior results.
- **Code Quality**: Modular, documented, runnable containers.
- **Traceability**: Logs + outputs per scenario.
- **Repository Hygiene**: Outputs folder created, README provided.

---

© 2025 Multi‑Agent Chat System (assessment prototype)
