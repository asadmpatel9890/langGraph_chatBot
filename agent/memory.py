from collections import deque

class ShortMemory:
    """Lightweight conversation memory for LangGraph."""
    def __init__(self, max_turns=10):
        self.buf = deque(maxlen=max_turns)

    def add(self, role, text):
        self.buf.append((role, text))

    def as_text(self):
        return "\n".join([f"{r.upper()}: {t}" for r, t in self.buf])
