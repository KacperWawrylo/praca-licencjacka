#!/usr/bin/env python3
"""Density sweep – weryfikacja hipotezy H5.

Bada jak gęstość przeszkód wpływa na stosunek rozwinięć A*/Dijkstra
oraz na effective branching factor b* algorytmu A*.
"""

import csv
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.benchmark.runner import TrialConfig, run_bench

DENSITIES = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
OUT_DIR = Path(__file__).resolve().parent.parent / "density_sweep"

CSV_COLUMNS = [
    "wall_density", "mean_expanded_dijkstra", "mean_expanded_astar",
    "ratio", "mean_bstar_astar", "n_successful",
]


def valid_trials(trials: list[dict]) -> list[dict]:
    return [r for r in trials if "error" not in r and r.get("found")]


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    rows: list[dict] = []

    for wd in DENSITIES:
        print(f"\n--- wall_density = {wd:.2f} ---")
        cfg = TrialConfig(
            cols=100, rows=100, diag=False,
            wall_density=wd, weight_density=0.0,
            trials=30, seed=123,
        )
        results = run_bench(cfg)

        dij = valid_trials(results["Dijkstra"])
        ast = valid_trials(results["A*"])

        n_ok = min(len(dij), len(ast))
        if n_ok == 0:
            print(f"  Brak udanych prób – pomijam.")
            continue

        mean_exp_d = statistics.mean(r["expanded"] for r in dij)
        mean_exp_a = statistics.mean(r["expanded"] for r in ast)
        ratio = mean_exp_a / mean_exp_d if mean_exp_d > 0 else float("inf")
        mean_bstar = statistics.mean(r["b_star"] for r in ast)

        rows.append({
            "wall_density": wd,
            "mean_expanded_dijkstra": mean_exp_d,
            "mean_expanded_astar": mean_exp_a,
            "ratio": ratio,
            "mean_bstar_astar": mean_bstar,
            "n_successful": n_ok,
        })

    # --- CSV ---
    csv_path = OUT_DIR / "results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"\nCSV zapisany do {csv_path}")

    # --- Tabelka stdout ---
    print(f"\n{'='*80}")
    print(f"{'wall_density':>13s} {'exp_Dijkstra':>13s} {'exp_A*':>13s} "
          f"{'ratio':>8s} {'b*_A*':>8s} {'n_ok':>5s}")
    print(f"{'-'*80}")
    for r in rows:
        print(f"{r['wall_density']:13.2f} {r['mean_expanded_dijkstra']:13.1f} "
              f"{r['mean_expanded_astar']:13.1f} {r['ratio']:8.4f} "
              f"{r['mean_bstar_astar']:8.4f} {r['n_successful']:5d}")
    print(f"{'='*80}")

    # --- Wykres 1: ratio vs density ---
    densities = [r["wall_density"] for r in rows]
    ratios = [r["ratio"] for r in rows]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(densities, ratios, marker="o", linewidth=2, color="#2563eb")
    ax.axhline(y=1.0, linestyle="--", color="gray", linewidth=1, label="brak przewagi (R=1)")
    ax.set_xlabel("Gęstość przeszkód (wall_density)")
    ax.set_ylabel("R = expanded A* / expanded Dijkstra")
    ax.set_title("Stosunek rozwinięć A*/Dijkstra vs gęstość przeszkód")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ratio_vs_density.png", dpi=180)
    plt.close(fig)
    print(f"Wykres ratio zapisany do {OUT_DIR / 'ratio_vs_density.png'}")

    # --- Wykres 2: b* vs density ---
    bstars = [r["mean_bstar_astar"] for r in rows]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(densities, bstars, marker="s", linewidth=2, color="#dc2626")
    ax.set_xlabel("Gęstość przeszkód (wall_density)")
    ax.set_ylabel("Effective branching factor b* (A*)")
    ax.set_title("b* A* vs gęstość przeszkód")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "bstar_vs_density.png", dpi=180)
    plt.close(fig)
    print(f"Wykres b* zapisany do {OUT_DIR / 'bstar_vs_density.png'}")


if __name__ == "__main__":
    main()
