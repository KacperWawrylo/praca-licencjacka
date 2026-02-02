
from __future__ import annotations
from collections import deque
from typing import Tuple, List, Dict, Set, Optional
from .grid import Grid, Coord
from app.utils.metrics import SearchResult
from app.utils.timer import Timer

def reconstruct(came_from: Dict[Coord, Optional[Coord]], start: Coord, goal: Coord) -> List[Coord]:
    path = []
    cur = goal
    while cur is not None and cur in came_from:
        path.append(cur)
        if cur == start:
            break
        cur = came_from[cur]
    path.reverse()
    return path

def bfs(grid: Grid) -> SearchResult:
    if grid.start is None or grid.goal is None:
        raise ValueError("Brak punktów start/cel")
    s, t = grid.start, grid.goal
    # BFS jest poprawny (optymalny kosztowo) tylko dla grafów o równych kosztach krawędzi.
    # W naszej siatce koszty różnią się przy ruchach po skosie i/lub przy wagach pól.
    if grid.weighted or grid.diag:
        raise ValueError("BFS działa tylko dla grafów o równych kosztach krawędzi (bez wag i bez ruchów po skosie).")

    visited: Set[Coord] = set([s])
    came_from: Dict[Coord, Optional[Coord]] = {s: None}
    q = deque([s])

    expanded = 0
    explored_order = []
    frontier_peak = 1

    with Timer() as tm:
        while q:
            u = q.popleft()
            explored_order.append(u)
            expanded += 1
            if u == t:
                break
            for v in grid.neighbors(u):
                if v not in visited:
                    visited.add(v)
                    came_from[v] = u
                    q.append(v)
                    frontier_peak = max(frontier_peak, len(q))

    path = reconstruct(came_from, s, t)
    found = (path[-1] == t) if path else False
    if found:
        total_cost = 0.0
        for i in range(len(path) - 1):
            total_cost += grid.cost(path[i], path[i+1])
    else:
        total_cost = float('inf')


    return SearchResult(
        path=path,
        found=found,
        # Ujednolicenie semantyki: "visited_count" jako liczba węzłów przetworzonych (closed)
        # spójnie z Dijkstrą/A* (to również liczba expanded).
        visited_count=len(explored_order),
        expanded_count=expanded,
        frontier_peak=frontier_peak,
        time_s=tm.elapsed,
        total_cost=total_cost,
        explored_order=explored_order,
        came_from=came_from
    )
