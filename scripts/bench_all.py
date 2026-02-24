#!/usr/bin/env python3
"""Uruchamia benchmark dla 4 scenariuszy i zapisuje wykresy + CSV."""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.benchmark.runner import TrialConfig, run_bench
from app.benchmark.plots import save_all_plots

SCENARIOS = {
    "S1": TrialConfig(
        cols=100, rows=100, trials=30, seed=123,
        diag=False, wall_density=0.25, weight_density=0.0,
    ),
    "S2": TrialConfig(
        cols=100, rows=100, trials=30, seed=123,
        diag=True, wall_density=0.25, weight_density=0.0,
    ),
    "S3": TrialConfig(
        cols=100, rows=100, trials=30, seed=123,
        diag=False, wall_density=0.25, weight_density=0.10, weight_value=5,
    ),
    "S4": TrialConfig(
        cols=100, rows=100, trials=30, seed=123,
        diag=True, wall_density=0.25, weight_density=0.10, weight_value=5,
    ),
}

CSV_COLUMNS = [
    "scenario", "algorithm", "trial",
    "found", "time_s", "expanded", "visited",
    "frontier_peak", "path_len", "total_cost", "b_star",
]


def save_csv(scenario_name: str, results: dict, out_dir: Path) -> None:
    csv_path = out_dir / "results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for algo, trials in results.items():
            for i, row in enumerate(trials, start=1):
                if "error" in row:
                    continue
                writer.writerow({
                    "scenario": scenario_name,
                    "algorithm": algo,
                    "trial": i,
                    "found": row["found"],
                    "time_s": row["time_s"],
                    "expanded": row["expanded"],
                    "visited": row["visited"],
                    "frontier_peak": row["frontier_peak"],
                    "path_len": row["path_len"],
                    "total_cost": row["total_cost"],
                    "b_star": row["b_star"],
                })


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    summary: dict[str, dict[str, dict[str, int]]] = {}

    for name, cfg in SCENARIOS.items():
        print(f"\n{'='*60}")
        print(f"  Scenariusz {name}: diag={cfg.diag}, "
              f"wall={cfg.wall_density}, weight={cfg.weight_density}")
        print(f"{'='*60}")

        results = run_bench(cfg)

        out_dir = base_dir / f"bench_{name}"
        out_dir.mkdir(exist_ok=True)

        save_all_plots(results, str(out_dir))
        save_csv(name, results, out_dir)
        print(f"  Wyniki zapisane do {out_dir}/")

        summary[name] = {}
        for algo, trials in results.items():
            ok = sum(1 for r in trials if "error" not in r and r.get("found"))
            fail = len(trials) - ok
            summary[name][algo] = {"ok": ok, "fail": fail}

    print(f"\n{'='*60}")
    print("  PODSUMOWANIE")
    print(f"{'='*60}")
    for name, algos in summary.items():
        total_ok = sum(a["ok"] for a in algos.values())
        total_fail = sum(a["fail"] for a in algos.values())
        print(f"\n  {name}: udane={total_ok}, nieudane={total_fail}")
        for algo, counts in algos.items():
            print(f"    {algo:10s}: udane={counts['ok']}, nieudane={counts['fail']}")


if __name__ == "__main__":
    main()
