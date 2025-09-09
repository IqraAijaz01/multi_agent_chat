import sys, os
from .coordinator import Coordinator
from .logger import TraceLogger

def main():
    tracer = TraceLogger()
    coord = Coordinator(memory_dir=os.path.join(os.path.dirname(__file__), "data"), tracer=tracer)
    print("\n=== Simple Multi-Agent Chat System ===\nType your question. Type 'exit' to quit.\n")
    while True:
        try:
            q = input("You> ").strip()
        except EOFError:
            break
        if q.lower() in {"exit","quit"}:
            break
        result = coord.handle(q)
        print("\n--- Answer ---\n" + result["answer"] + "\n----------------\n")

if __name__ == "__main__":
    main()
