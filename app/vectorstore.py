import math, re, collections
from typing import List, Dict, Tuple

_token_re = re.compile(r"""[A-Za-z0-9_#@]+""", re.U)

def tokenize(text: str) -> List[str]:
    return [t.lower() for t in _token_re.findall(text)]

class InMemoryVectorStore:
    """Lightweight keyword + vector similarity store.
    Stores documents as {doc_id: text}. Maintains:
      - term frequencies per doc
      - inverted index: term -> set(doc_id)
    Cosine similarity over raw term frequencies (bag-of-words).
    """
    def __init__(self):
        self.docs: Dict[str, str] = {}
        self.tf: Dict[str, collections.Counter] = {}
        self.inverted: Dict[str, set] = collections.defaultdict(set)
        self.norms: Dict[str, float] = {}

    def upsert(self, doc_id: str, text: str):
        self.docs[doc_id] = text
        tokens = tokenize(text)
        c = collections.Counter(tokens)
        self.tf[doc_id] = c
        for term in c:
            self.inverted[term].add(doc_id)
        # precompute norm
        self.norms[doc_id] = math.sqrt(sum(v*v for v in c.values())) or 1.0

    def remove(self, doc_id: str):
        if doc_id in self.docs:
            tokens = tokenize(self.docs[doc_id])
            for term in set(tokens):
                if doc_id in self.inverted.get(term, set()):
                    self.inverted[term].discard(doc_id)
        self.docs.pop(doc_id, None)
        self.tf.pop(doc_id, None)
        self.norms.pop(doc_id, None)

    def _cosine(self, q: collections.Counter, doc_id: str) -> float:
        num = 0.0
        for term, qv in q.items():
            num += qv * self.tf.get(doc_id, {}).get(term, 0)
        denom = (math.sqrt(sum(v*v for v in q.values())) or 1.0) * self.norms.get(doc_id, 1.0)
        return num / denom if denom else 0.0

    def keyword_candidates(self, query: str) -> set:
        tokens = set(tokenize(query))
        if not tokens:
            return set(self.docs.keys())
        cands = set()
        for t in tokens:
            cands |= self.inverted.get(t, set())
        return cands

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        tokens = tokenize(query)
        q = collections.Counter(tokens)
        cands = self.keyword_candidates(query)
        scored = [(doc_id, self._cosine(q, doc_id)) for doc_id in cands]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
