
from __future__ import annotations
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Callable, Optional
from app.algorithms.grid import Grid
from app.algorithms.bfs import bfs
from app.algorithms.dijkstra import dijkstra
from app.algorithms.astar import astar
from app.utils.heuristics import manhattan, octile, scaled

@dataclass
class TrialConfig:
    cols: int = 300
    rows: int = 200
    diag: bool = False
    wall_density: float = 0.3
    weight_density: float = 0.0
    weight_value: int = 5
    trials: int = 20
    seed: int = 123

def run_bench(cfg: TrialConfig) -> Dict[str, List[Dict[str, Any]]]:
    rng = random.Random(cfg.seed)
    results: Dict[str, List[Dict[str, Any]]] = {"BFS": [], "Dijkstra": [], "A*": []}

    successful_trials = 0
    failed_trials = 0

    for i in range(cfg.trials):
        g = Grid(cfg.cols, cfg.rows, diag=cfg.diag)
        # start/goal różne i wolne
        s = (rng.randrange(cfg.cols), rng.randrange(cfg.rows))
        t = (rng.randrange(cfg.cols), rng.randrange(cfg.rows))
        while t == s:
            t = (rng.randrange(cfg.cols), rng.randrange(cfg.rows))
        g.start, g.goal = s, t
        g.randomize_walls(cfg.wall_density, seed=rng.randrange(1_000_000))
        if cfg.weight_density > 0:
            g.randomize_weights(cfg.weight_density, cfg.weight_value, seed=rng.randrange(1_000_000))


        # Dijkstra
        rD = dijkstra(g)
        if not rD.found:
            failed_trials += 1
            continue
        successful_trials += 1
        results["Dijkstra"].append({
            "found": rD.found,
            "time_s": rD.time_s,
            "expanded": rD.expanded_count,
            "visited": rD.visited_count,
            "frontier_peak": rD.frontier_peak,
            "path_len": rD.path_length(),
            "total_cost": rD.total_cost,
        })



        # BFS tylko gdy brak wag
        if not g.weighted and not cfg.diag:
            try:
                r = bfs(g)
                results["BFS"].append({
                    "found": r.found,
                    "time_s": r.time_s,
                    "expanded": r.expanded_count,
                    "visited": r.visited_count,
                    "frontier_peak": r.frontier_peak,
                    "path_len": r.path_length(),
                    "total_cost": r.total_cost,
                })
            except Exception as e:
                results["BFS"].append({"error": str(e)})


        # A* z heurystyką zależną od sąsiedztwa
        base_h = octile if cfg.diag else manhattan
        h = scaled(base_h, scale=g.min_step_cost())
        rA = astar(g, h)
        results["A*"].append({
            "found": rA.found,
            "time_s": rA.time_s,
            "expanded": rA.expanded_count,
            "visited": rA.visited_count,
            "frontier_peak": rA.frontier_peak,
            "path_len": rA.path_length(),
            "total_cost": rA.total_cost,
        })

    print(f"\n=== STATYSTYKI BENCHMARKU ===")
    print(f"Próby zakończone sukcesem: {successful_trials}/{cfg.trials}")
    print(f"Próby nieudane (graf niespójny): {failed_trials}/{cfg.trials}")
    print(f"Udane próby BFS: {len(results['BFS'])}/{successful_trials}")
    print(f"Udane próby Dijkstra: {len(results['Dijkstra'])}/{successful_trials}")
    print(f"Udane próby A*: {len(results['A*'])}/{successful_trials}")

    return results
