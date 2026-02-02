
from __future__ import annotations
import heapq
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

def dijkstra(grid: Grid) -> SearchResult:
    if grid.start is None or grid.goal is None:
        raise ValueError("Brak punktów start/cel")
    s, t = grid.start, grid.goal

    dist: Dict[Coord, float] = {s: 0.0}
    came_from: Dict[Coord, Optional[Coord]] = {s: None}
    visited: Set[Coord] = set()
    pq: List[Tuple[float, Coord]] = [(0.0, s)]
    open_set: Set[Coord] = {s}

    expanded = 0
    explored_order = []
    frontier_peak = 1

    with Timer() as tm:
        while pq:
            du, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)
            # węzeł zdjęty z OPEN → usuń z open_set (jeśli był)
            if u in open_set:
                open_set.remove(u)
            explored_order.append(u)
            expanded += 1
            if u == t:
                break
            for v in grid.neighbors(u):
                if v in visited:
                    continue
                alt = dist[u] + grid.cost(u, v)
                if alt < dist.get(v, float('inf')):
                    dist[v] = alt
                    came_from[v] = u
                    heapq.heappush(pq, (alt, v))
                    if v not in open_set:
                        open_set.add(v)
                    frontier_peak = max(frontier_peak, len(open_set))

    path = reconstruct(came_from, s, t)
    found = (path[-1] == t) if path else False
    total_cost = dist.get(t, float('inf'))

    return SearchResult(
        path=path,
        found=found,
        visited_count=len(visited),
        expanded_count=expanded,
        frontier_peak=frontier_peak,
        time_s=tm.elapsed,
        total_cost=total_cost,
        explored_order=explored_order,
        came_from=came_from
    )
