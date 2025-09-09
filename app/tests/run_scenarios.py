import os, io
from datetime import datetime
from ..coordinator import Coordinator
from ..logger import TraceLogger

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTDIR = os.path.join(ROOT, "outputs")

SCENARIOS = [
    ("simple_query.txt", "What are the main types of neural networks?"),
    ("complex_query.txt", "Research transformer architectures, analyze their computational efficiency, and summarize key trade-offs."),
    ("memory_test.txt", "What did we discuss about neural networks earlier?"),
    ("multi_step.txt", "Find recent papers on reinforcement learning, analyze their methodologies, and identify common challenges."),
    ("collaborative.txt", "Compare two machine-learning approaches and recommend which is better for our use case."),
]

def run_all():
    tracer = TraceLogger()
    coord = Coordinator(memory_dir=os.path.join(os.path.dirname(__file__), "..", "data"), tracer=tracer)
    os.makedirs(OUTDIR, exist_ok=True)
    for fname, query in SCENARIOS:
        tracer.log("TestRunner", "scenario_start", {"file": fname, "query": query})
        result = coord.handle(query)
        content = [f"# Scenario: {query}\n\n", result["answer"], "\n\n# Trace Log\n\n", tracer.dump()]
        with open(os.path.join(OUTDIR, fname), "w", encoding="utf-8") as fp:
            fp.write("".join(content))
        # reset the tracer for next scenario (but keep memory to simulate continuity)
        tracer.lines = []

if __name__ == "__main__":
    run_all()
