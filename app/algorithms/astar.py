
from __future__ import annotations
import heapq
from typing import Tuple, List, Dict, Set, Optional, Callable
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

def astar(grid: Grid, h: Callable[[Coord, Coord], float]) -> SearchResult:
    if grid.start is None or grid.goal is None:
        raise ValueError("Brak punktów start/cel")
    s, t = grid.start, grid.goal

    g: Dict[Coord, float] = {s: 0.0}
    f: Dict[Coord, float] = {s: h(s, t)}
    came_from: Dict[Coord, Optional[Coord]] = {s: None}
    closed: Set[Coord] = set()
    pq: List[Tuple[float, Coord]] = [(f[s], s)]
    open_set: Set[Coord] = {s}


    expanded = 0
    explored_order = []
    frontier_peak = 1

    with Timer() as tm:
        while pq:
            fu, u = heapq.heappop(pq)
            if u in closed:
                continue
            closed.add(u)
            if u in open_set:
                open_set.remove(u)

            explored_order.append(u)
            expanded += 1
            if u == t:
                break
            for v in grid.neighbors(u):
                tentative = g[u] + grid.cost(u, v)
                if v in closed:
                    continue
                if tentative < g.get(v, float('inf')):
                    g[v] = tentative
                    f[v] = tentative + h(v, t)
                    came_from[v] = u
                    heapq.heappush(pq, (f[v], v))
                    if v not in open_set:
                        open_set.add(v)
                    frontier_peak = max(frontier_peak, len(open_set))

    path = reconstruct(came_from, s, t)
    found = (path[-1] == t) if path else False
    total_cost = g.get(t, float('inf'))

    return SearchResult(
        path=path,
        found=found,
        visited_count=len(closed),
        expanded_count=expanded,
        frontier_peak=frontier_peak,
        time_s=tm.elapsed,
        total_cost=total_cost,
        explored_order=explored_order,
        came_from=came_from
    )
