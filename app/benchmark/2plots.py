
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")  # bez okna do zapisu plików; aplikacja pokaże je osobno
import matplotlib.pyplot as plt
from typing import Dict, List, Any
import statistics as stats
from pathlib import Path

def _aggregate(series: List[float]) -> Dict[str, float]:
    if not series:
        return {"mean": float("nan"), "median": float("nan"), "p90": float("nan")}
    series_sorted = sorted(series)
    n = len(series_sorted)
    p90 = series_sorted[int(0.9 * (n-1))]
    return {
        "mean": sum(series_sorted) / n,
        "median": series_sorted[n//2] if n % 2 == 1 else 0.5*(series_sorted[n//2-1]+series_sorted[n//2]),
        "p90": p90,
    }

def _save_single_bar(metric: str, data: Dict[str, List[float]], out_dir: Path) -> Path:
    # Każdy wykres w osobnym rysunku, bez ustawiania kolorów ani stylów.
    fig = plt.figure()
    labels = []
    values = []
    for algo, values_list in data.items():
        agg = _aggregate(values_list)
        labels.append(algo)
        values.append(agg["mean"])
    plt.title(f"{metric} (średnia)")
    plt.bar(labels, values)
    plt.ylabel(metric)
    out = out_dir / f"{metric.replace(' ', '_').lower()}.png"
    fig.savefig(out, bbox_inches="tight", dpi=160)
    plt.close(fig)
    return out

def save_all_plots(results: Dict[str, List[Dict[str, Any]]], out_dir: str) -> Dict[str, str]:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    metrics = {
        "Czas [s]": {algo: [r["time_s"] for r in res if r.get("found")] for algo, res in results.items()},
        "Rozwinięcia [#]": {algo: [r["expanded"] for r in res if r.get("found")] for algo, res in results.items()},
        "Odwiedzone [#]": {algo: [r["visited"] for r in res if r.get("found")] for algo, res in results.items()},
        "Szczyt frontu [#]": {algo: [r["frontier_peak"] for r in res if r.get("found")] for algo, res in results.items()},
        "Długość ścieżki [kroki]": {algo: [r["path_len"] for r in res if r.get("found")] for algo, res in results.items()},
        "Koszt całkowity": {algo: [r["total_cost"] for r in res if r.get("found")] for algo, res in results.items()},
    }

    files = {}
    for metric, data in metrics.items():
        files[metric] = str(_save_single_bar(metric, data, out_path))
    return files
