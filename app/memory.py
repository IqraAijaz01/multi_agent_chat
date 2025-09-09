import json, os, uuid, datetime
from typing import List, Dict, Any, Optional, Tuple
from .vectorstore import InMemoryVectorStore

def utcnow():
    return datetime.datetime.utcnow().isoformat() + "Z"

class MemoryLayer:
    """Structured memory with three stores and vector search:
    - conversation (chronological messages)
    - knowledge (learned facts/findings)
    - agent_state (per-task achievements)
    Records are persisted to JSON files for demonstration.
    """
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.files = {
            "conversation": os.path.join(self.data_dir, "conversation.json"),
            "knowledge": os.path.join(self.data_dir, "knowledge.json"),
            "agent_state": os.path.join(self.data_dir, "agent_state.json"),
        }
        self._init_files()
        # Vector stores
        self.vstores = {
            "conversation": InMemoryVectorStore(),
            "knowledge": InMemoryVectorStore(),
            "agent_state": InMemoryVectorStore(),
        }
        self._load_into_vectors()

    def _init_files(self):
        for k, f in self.files.items():
            if not os.path.exists(f):
                with open(f, "w") as fp:
                    json.dump([], fp)

    def _read(self, name: str) -> List[Dict[str, Any]]:
        with open(self.files[name], "r") as fp:
            return json.load(fp)

    def _write(self, name: str, records: List[Dict[str, Any]]):
        with open(self.files[name], "w") as fp:
            json.dump(records, fp, indent=2)

    def _load_into_vectors(self):
        for name in self.files.keys():
            for rec in self._read(name):
                self.vstores[name].upsert(rec["id"], rec.get("text",""))

    def add_record(self, store: str, record: Dict[str, Any]) -> Dict[str, Any]:
        recs = self._read(store)
        rec = {
            "id": record.get("id", str(uuid.uuid4())),
            "timestamp": record.get("timestamp", utcnow()),
            "type": record.get("type", store),
            "topic": record.get("topic", ""),
            "text": record.get("text", ""),
            "source": record.get("source", ""),
            "agent": record.get("agent", ""),
            "confidence": float(record.get("confidence", 0.5)),
            "tags": record.get("tags", []),
            "extras": record.get("extras", {}),
        }
        recs.append(rec)
        self._write(store, recs)
        self.vstores[store].upsert(rec["id"], rec["text"] + " " + " ".join(rec.get("tags",[])))
        return rec

    def search(self, store: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        results = []
        for doc_id, score in self.vstores[store].search(query, top_k=top_k):
            for rec in self._read(store):
                if rec["id"] == doc_id:
                    r = dict(rec)
                    r["_score"] = score
                    results.append(r)
        # recency/confidence boost
        results.sort(key=lambda r: (r["_score"], r.get("confidence",0), r.get("timestamp","")), reverse=True)
        return results

    def get_all(self, store: str) -> List[Dict[str, Any]]:
        return self._read(store)
