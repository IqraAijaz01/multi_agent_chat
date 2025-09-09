import os, re, json, random
from typing import Dict, Any
from .agents import ResearchAgent, AnalysisAgent, MemoryAgent
from .memory import MemoryLayer, utcnow
from .logger import TraceLogger

def estimate_complexity(text: str) -> int:
    # naive: verbs + entities cues
    verbs = len(re.findall(r"\b(find|analyze|compare|identify|summarize|research)\b", text, re.I))
    ands = text.count(" and ")
    commas = text.count(",")
    return verbs + ands + (1 if commas else 0)

class Coordinator:
    def __init__(self, memory_dir: str, tracer: TraceLogger):
        self.memory = MemoryLayer(memory_dir)
        self.tracer = tracer
        self.research = ResearchAgent(self.memory, tracer)
        self.analysis = AnalysisAgent(self.memory, tracer)
        self.memorizer = MemoryAgent(self.memory, tracer)

    def plan(self, user_query: str) -> Dict[str, Any]:
        cx = estimate_complexity(user_query)
        self.tracer.log("Coordinator", "complexity", {"score": cx})
        if cx <= 1:
            return {"pipeline": ["memory_lookup", "research_optional", "synthesis"], "reason": "simple"}
        else:
            return {"pipeline": ["research", "analysis", "memory_update", "synthesis"], "reason": "complex"}

    def memory_lookup(self, query: str):
        hits = self.memorizer.recall(query, top_k=3)
        return hits

    def handle(self, user_query: str) -> Dict[str, Any]:
        self.tracer.log("Coordinator", "start", {"query": user_query})
        # conversation memory
        self.memory.add_record("conversation", {
            "topic": "user_query",
            "text": user_query,
            "source": "user",
            "agent": "user",
            "confidence": 1.0,
            "tags": []
        })
        plan = self.plan(user_query)
        pipeline = plan["pipeline"]
        context: Dict[str, Any] = {"query": user_query, "mem_hits": []}

        if pipeline[0] == "memory_lookup":
            hits = self.memory_lookup(user_query)
            context["mem_hits"] = hits
            if hits:
                self.tracer.log("Coordinator", "reuse_memory", {"hit_ids": [h['id'] for h in hits]})
            # optionally research if low coverage
            if len(hits) < 2:
                r = self.research.run(user_query, topic_hint=user_query)
                context["research"] = r
        else:
            r = self.research.run(user_query, topic_hint=user_query)
            context["research"] = r
            a = self.analysis.run("Analyze research results", r)
            context["analysis"] = a
            # memory update with synthesized finding
            self.memorizer.remember({
                "topic": "auto_finding",
                "text": (a.get("analysis","")[:500] or r.get("summary","")),
                "source": "synthesis",
                "agent": "Coordinator",
                "confidence": 0.75,
                "tags": ["finding","auto"]
            })

        # Synthesis for final answer
        final = self.synthesize(context)
        self.tracer.log("Coordinator", "done", {"confidence": final.get("confidence",0.6)})
        # log assistant reply to conversation memory
        self.memory.add_record("conversation", {
            "topic": "assistant_reply",
            "text": final.get("answer",""),
            "source": "assistant",
            "agent": "Coordinator",
            "confidence": final.get("confidence",0.6),
            "tags": ["reply"]
        })
        return final

    def synthesize(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        parts = [f"User asked: {ctx['query']}\n"]
        conf = 0.6
        if ctx.get("mem_hits"):
            parts.append("From memory (most relevant):\n")
            for h in ctx["mem_hits"]:
                parts.append(f"- [{h['timestamp']}] {h['text']} (conf={h.get('confidence',0):.2f})\n")
                conf = max(conf, 0.65)
        if ctx.get("research"):
            parts.append("\nResearch findings:\n" + ctx["research"].get("summary",""))
            conf = max(conf, ctx["research"].get("confidence", 0.6))
        if ctx.get("analysis"):
            parts.append("\n\nAnalysis:\n" + ctx["analysis"].get("analysis",""))
            conf = max(conf, ctx["analysis"].get("confidence", 0.6))

        answer = "\n".join(parts)
        return {"answer": answer, "confidence": conf}
