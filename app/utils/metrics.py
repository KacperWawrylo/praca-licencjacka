
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
