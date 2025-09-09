import math, statistics, os
from typing import List, Dict, Any
from .memory import MemoryLayer, utcnow
from .knowledge_base import CORPUS

class ResearchAgent:
    def __init__(self, memory: MemoryLayer, tracer):
        self.memory = memory
        self.tracer = tracer

    def run(self, query: str, topic_hint: str = "") -> Dict[str, Any]:
        # Simulate information retrieval using the mock KB + memory knowledge
        self.tracer.log("ResearchAgent", "start", {"query": query, "topic_hint": topic_hint})
        # Search in KB first
        matches = []
        q = topic_hint or query
        for doc in CORPUS:
            # simple keyword match
            if any(tok in (doc["topic"] + " " + doc["text"]).lower() for tok in q.lower().split()):
                matches.append(doc)
        # Also search previous knowledge memory
        prior = self.memory.search("knowledge", q, top_k=3)
        for rec in prior:
            matches.append({"id": rec.get("source","mem:"+rec["id"]), "topic": rec.get("topic",""), "text": rec.get("text",""), "source": "memory"})

        if not matches:
            # fallback: take top from KB by vector sim (naive: just include all)
            matches = CORPUS[:2]

        # Confidence heuristic based on number of matches
        conf = min(0.9, 0.5 + 0.1*len(matches))
        result_text = "\n".join(f"- [{m['id']}] {m['text']}" for m in matches)
        out = {
            "summary": result_text,
            "matches": matches,
            "confidence": conf
        }
        self.tracer.log("ResearchAgent", "done", out)
        # Write to agent_state
        self.memory.add_record("agent_state", {
            "topic": topic_hint or "general",
            "text": f"Research completed for query: {query}",
            "source": "ResearchAgent",
            "agent": "ResearchAgent",
            "confidence": conf,
            "tags": ["research","retrieval"]
        })
        return out

class AnalysisAgent:
    def __init__(self, memory: MemoryLayer, tracer):
        self.memory = memory
        self.tracer = tracer

    def run(self, prompt: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        self.tracer.log("AnalysisAgent", "start", {"prompt": prompt, "inputs_keys": list(inputs.keys())})
        matches = inputs.get("matches", [])
        # Simple analysis: bullet comparison + heuristic ranking
        bullets = []
        score_map = {}
        for m in matches:
            txt = m.get("text","").lower()
            score = 0
            for kw in ["efficient","efficiency","sparse","linear","distillation","momentum","adam","sgd","rnn","cnn","transformer"]:
                if kw in txt:
                    score += 1
            score_map[m["id"]] = score
            bullets.append(f"* {m.get('topic', 'topic')}: {m.get('text','')} (score={score})")

        # Recommendation (highest score)
        best = None
        if score_map:
            best = max(score_map.items(), key=lambda kv: kv[1])[0]

        summary = "Analysis Summary:\n" + "\n".join(bullets)
        if best:
            summary += f"\n\nPreliminary recommendation: prioritize sources around `{best}`."
        conf = 0.6 + 0.1*bool(best)
        out = {"analysis": summary, "confidence": conf}
        self.tracer.log("AnalysisAgent", "done", out)
        self.memory.add_record("agent_state", {
            "topic": "analysis",
            "text": f"Analysis run for: {prompt[:80]}",
            "source": "AnalysisAgent",
            "agent": "AnalysisAgent",
            "confidence": conf,
            "tags": ["analysis","reasoning"]
        })
        return out

class MemoryAgent:
    def __init__(self, memory: MemoryLayer, tracer):
        self.memory = memory
        self.tracer = tracer

    def remember(self, record: Dict[str, Any]) -> Dict[str, Any]:
        self.tracer.log("MemoryAgent", "remember", record)
        rec = self.memory.add_record("knowledge", record)
        return rec

    def recall(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        self.tracer.log("MemoryAgent", "recall", {"query": query})
        return self.memory.search("knowledge", query, top_k=top_k)
