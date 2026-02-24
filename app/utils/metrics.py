
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class SearchResult:
    path: List[Tuple[int, int]]
    found: bool
    visited_count: int
    expanded_count: int
    frontier_peak: int
    time_s: float
    total_cost: float
    explored_order: List[Tuple[int, int]]  # do animacji
    came_from: dict  # do rekonstrukcji/visual debug

    def path_length(self) -> int:
        return max(0, len(self.path) - 1)

    def effective_branching_factor(self) -> float:
        """Oblicza effective branching factor b* metodą bisekcji.
        b* jest rozwiązaniem: sum(b*^i for i in 0..d) = N
        gdzie d = path_length(), N = expanded_count.
        Wartość b* bliska 1.0 oznacza doskonałą heurystykę.
        """
        d = self.path_length()
        N = self.expanded_count
        if d == 0 or N <= 1:
            return 1.0
        lo, hi = 1.0, float(N)
        for _ in range(100):
            mid = (lo + hi) / 2.0
            if abs(mid - 1.0) < 1e-10:
                val = d + 1.0
            else:
                try:
                    val = (mid ** (d + 1) - 1.0) / (mid - 1.0)
                except OverflowError:
                    val = float("inf")
            if val < N:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2.0
