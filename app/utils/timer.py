
import time

class Timer:
    """Prosty miernik czasu ściennego (monotonicznego)."""
    def __init__(self):
        self._start = None
        self.elapsed = 0.0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._start is not None:
            self.elapsed = time.perf_counter() - self._start
            self._start = None
