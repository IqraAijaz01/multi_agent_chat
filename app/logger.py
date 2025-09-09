import json, datetime, pprint

def ts():
    return datetime.datetime.utcnow().isoformat() + "Z"

def pretty(obj):
    return pprint.pformat(obj, indent=2, compact=True, width=100)

class TraceLogger:
    def __init__(self, sink=None):
        self.sink = sink  # optional file-like
        self.lines = []

    def log(self, where, event, payload=None):
        record = {
            "time": ts(),
            "where": where,
            "event": event,
            "payload": payload or {}
        }
        line = f"[{record['time']}] {where}: {event}\n{pretty(payload)}\n"
        self.lines.append(line)
        print(line, end="")
        if self.sink:
            self.sink.write(line)

    def dump(self):
        return "".join(self.lines)
