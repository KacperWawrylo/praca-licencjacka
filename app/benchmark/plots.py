from __future__ import annotations
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict, List, Any
import statistics as stats
from pathlib import Path
import numpy as np


def _aggregate(series: List[float]) -> Dict[str, float]:
    """Oblicza szczegółowe statystyki dla serii danych."""
    if not series:
        return {
            "mean": float("nan"),
            "median": float("nan"),
            "std": float("nan"),
            "min": float("nan"),
            "max": float("nan"),
            "p25": float("nan"),
            "p75": float("nan"),
            "p90": float("nan")
        }

    series_sorted = sorted(series)
    n = len(series_sorted)

    # Oblicz statystyki
    mean_val = sum(series_sorted) / n
    median_val = series_sorted[n // 2] if n % 2 == 1 else 0.5 * (series_sorted[n // 2 - 1] + series_sorted[n // 2])

    # Odchylenie standardowe
    if n > 1:
        variance = sum((x - mean_val) ** 2 for x in series_sorted) / (n - 1)
        std_val = variance ** 0.5
    else:
        std_val = 0.0

    return {
        "mean": mean_val,
        "median": median_val,
        "std": std_val,
        "min": series_sorted[0],
        "max": series_sorted[-1],
        "p25": series_sorted[int(0.25 * (n - 1))],
        "p75": series_sorted[int(0.75 * (n - 1))],
        "p90": series_sorted[int(0.9 * (n - 1))],
        "n": n
    }


def _save_single_bar(metric: str, data: Dict[str, List[float]], out_dir: Path) -> Path:
    """Tworzy szczegółowy wykres słupkowy z error bars i statystykami."""
    fig, ax = plt.subplots(figsize=(10, 6))

    labels = []
    means = []
    stds = []
    medians = []
    n_samples = []

    # Kolory dla każdego algorytmu
    colors = {'BFS': '#3498db', 'Dijkstra': '#e74c3c', 'A*': '#2ecc71'}

    for algo, values_list in data.items():
        if not values_list:
            continue
        agg = _aggregate(values_list)
        labels.append(algo)
        means.append(agg["mean"])
        stds.append(agg["std"])
        medians.append(agg["median"])
        n_samples.append(agg["n"])

    if not labels:
        # Brak danych do wykresu
        ax.text(0.5, 0.5, 'Brak danych', ha='center', va='center', transform=ax.transAxes)
        out = out_dir / f"{metric.replace(' ', '_').lower()}.png"
        fig.savefig(out, bbox_inches="tight", dpi=160)
        plt.close(fig)
        return out

    x_pos = np.arange(len(labels))

    # Rysuj słupki z kolorami
    bars = ax.bar(x_pos, means,
                  yerr=stds,
                  capsize=5,
                  color=[colors.get(lbl, '#95a5a6') for lbl in labels],
                  alpha=0.8,
                  edgecolor='black',
                  linewidth=1.2)

    # Dodaj punkty mediany
    ax.scatter(x_pos, medians, color='red', s=100, zorder=5,
               marker='D', label='Mediana', edgecolors='darkred', linewidths=1.5)

    # Formatowanie
    ax.set_ylabel(metric, fontsize=12, fontweight='bold')
    ax.set_title(f"{metric}\n(słupki: średnia ± odch. std., romby: mediana)",
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=11)

    # Dodaj siatkę
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.7)
    ax.set_axisbelow(True)

    # Dodaj etykiety z liczbą prób na słupkach
    for i, (bar, n) in enumerate(zip(bars, n_samples)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height + stds[i],
                f'n={n}',
                ha='center', va='bottom', fontsize=9, color='dimgray')

    # Legenda
    ax.legend(loc='upper right', fontsize=10)

    # Dostosuj marginesy
    plt.tight_layout()

    out = out_dir / f"{metric.replace(' ', '_').lower()}.png"
    fig.savefig(out, bbox_inches="tight", dpi=180)
    plt.close(fig)
    return out


def _save_comparison_table(data: Dict[str, List[float]], out_dir: Path, metric_name: str) -> Path:
    """Tworzy tabelę ze szczegółowymi statystykami."""
    fig, ax = plt.subplots(figsize=(12, 3 + len(data) * 0.5))
    ax.axis('tight')
    ax.axis('off')

    # Przygotuj dane do tabeli
    table_data = []
    headers = ['Algorytm', 'Średnia', 'Mediana', 'Odch. std', 'Min', 'Max', 'P25', 'P75', 'P90', 'n']

    for algo, values_list in data.items():
        if not values_list:
            continue
        agg = _aggregate(values_list)
        row = [
            algo,
            f"{agg['mean']:.4f}",
            f"{agg['median']:.4f}",
            f"{agg['std']:.4f}",
            f"{agg['min']:.4f}",
            f"{agg['max']:.4f}",
            f"{agg['p25']:.4f}",
            f"{agg['p75']:.4f}",
            f"{agg['p90']:.4f}",
            f"{agg['n']}"
        ]
        table_data.append(row)

    if not table_data:
        ax.text(0.5, 0.5, 'Brak danych', ha='center', va='center', transform=ax.transAxes)
    else:
        table = ax.table(cellText=table_data, colLabels=headers,
                         cellLoc='center', loc='center',
                         colWidths=[0.12, 0.1, 0.1, 0.1, 0.08, 0.08, 0.08, 0.08, 0.08, 0.06])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)

        # Koloruj nagłówki
        for i in range(len(headers)):
            table[(0, i)].set_facecolor('#40466e')
            table[(0, i)].set_text_props(weight='bold', color='white')

        # Koloruj wiersze na przemian
        for i in range(1, len(table_data) + 1):
            for j in range(len(headers)):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#f0f0f0')

    plt.title(f"Szczegółowe statystyki: {metric_name}",
              fontsize=13, fontweight='bold', pad=20)

    out = out_dir / f"{metric_name.replace(' ', '_').lower()}_tabela.png"
    fig.savefig(out, bbox_inches="tight", dpi=180)
    plt.close(fig)
    return out


def save_all_plots(results: Dict[str, List[Dict[str, Any]]], out_dir: str) -> Dict[str, str]:
    """Generuje wszystkie wykresy i tabele ze statystykami."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    metrics = {
        "Czas [s]": {algo: [r["time_s"] for r in res if r.get("found")]
                     for algo, res in results.items()},
        "Rozwinięcia [#]": {algo: [r["expanded"] for r in res if r.get("found")]
                            for algo, res in results.items()},
        "Odwiedzone [#]": {algo: [r["visited"] for r in res if r.get("found")]
                           for algo, res in results.items()},
        "Szczyt frontu [#]": {algo: [r["frontier_peak"] for r in res if r.get("found")]
                              for algo, res in results.items()},
        "Długość ścieżki [kroki]": {algo: [r["path_len"] for r in res if r.get("found")]
                                    for algo, res in results.items()},
        "Koszt całkowity": {algo: [r["total_cost"] for r in res if r.get("found")]
                            for algo, res in results.items()},
    }

    files = {}

    # Generuj wykresy słupkowe
    for metric, data in metrics.items():
        files[f"{metric} (wykres)"] = str(_save_single_bar(metric, data, out_path))

    # Generuj tabele ze statystykami
    for metric, data in metrics.items():
        files[f"{metric} (tabela)"] = str(_save_comparison_table(data, out_path, metric))

    return files