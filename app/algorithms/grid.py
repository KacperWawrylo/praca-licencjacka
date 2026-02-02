
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Iterable, Optional
import math
import random

Coord = Tuple[int, int]

@dataclass
class Grid:
    cols: int
    rows: int
    diag: bool = False
    walls: set[Coord] = field(default_factory=set)
    weighted: dict[Coord, int] = field(default_factory=dict)  # koszt wejścia na pole
    start: Optional[Coord] = None
    goal: Optional[Coord] = None

    def in_bounds(self, c: Coord) -> bool:
        x, y = c
        return 0 <= x < self.cols and 0 <= y < self.rows

    def passable(self, c: Coord) -> bool:
        return c not in self.walls

    def cost(self, c_from: Coord, c_to: Coord) -> float:
        """Koszt ruchu z c_from -> c_to. Podstawowo 1 (lub sqrt(2) po skosie), plus waga pola docelowego."""
        (x1, y1), (x2, y2) = c_from, c_to
        base = math.sqrt(2.0) if (x1 != x2 and y1 != y2) else 1.0
        return base + float(self.weighted.get(c_to, 0))

    def neighbors(self, c: Coord) -> Iterable[Coord]:
        (x, y) = c
        # 4-neigh
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        if self.diag:
            dirs += [(1,1), (1,-1), (-1,1), (-1,-1)]
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            nc = (nx, ny)
            if self.in_bounds(nc) and self.passable(nc):
                # (opcjonalnie) można zabronić "przeciskania" po skosie między dwiema ścianami
                if self.diag and dx != 0 and dy != 0:
                    # nie pozwalaj przecinać narożników jeśli oba boki są ścianami
                    if not (self.passable((x+dx, y)) or self.passable((x, y+dy))):
                        continue
                yield nc

    def randomize_walls(self, density: float, seed: int | None = None):
        rng = random.Random(seed)
        self.walls.clear()
        for x in range(self.cols):
            for y in range(self.rows):
                if rng.random() < density:
                    self.walls.add((x,y))
        # nie blokuj startu/celu
        if self.start: self.walls.discard(self.start)
        if self.goal: self.walls.discard(self.goal)

    def clear_weights(self):
        self.weighted.clear()

    def randomize_weights(self, density: float, weight_value: int = 5, seed: int | None = None):
        rng = random.Random(seed)
        self.weighted.clear()
        for x in range(self.cols):
            for y in range(self.rows):
                if rng.random() < density and (x,y) not in self.walls:
                    self.weighted[(x,y)] = weight_value
        if self.start: self.weighted.pop(self.start, None)
        if self.goal: self.weighted.pop(self.goal, None)

    def min_step_cost(self) -> float:
        # minimalny koszt ruchu: 1 po prostych (albo sqrt(2) po skosie, ale minimum to 1)
        return 1.0
