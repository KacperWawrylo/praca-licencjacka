W ramach pracy licencjakiej - aplikacja w Pythonie do wizualizacji i porównywania algorytmów najkrótszej ścieżki:
**BFS**, **Dijkstra** oraz **A***. Interfejs oparty o **pygame**, wykresy generowane w **matplotlib**.

## Wymagania

- Python 3.9+
- `pip install -r requirements.txt`

## Uruchomienie

```bash
python run.py
```

## Skróty klawiszowe (w oknie pygame)

- **Lewy klik** – stawianie/usuwanie przeszkód
- **Prawy klik** – ustawianie **START** (pierwszy) i **CEL** (drugi)
- **1** – uruchom **BFS** (tylko grafy nieważone)
- **2** – uruchom **Dijkstra**
- **3** – uruchom **A\***
- **H** – przełącz sąsiedztwo **4**/8 (wpływa też na heurystykę A\*)
- **W** – generuj losowy labirynt (przeszkody)
- **G** – tryb malowania pól **ważonych** (wag=5); BFS zostaje zablokowany dla wag
- **R** – reset planszy (zostawia rozmiar/tryb)
- **Spacja** – pauza/wznów animację
- **S** – krok pojedynczy (gdy pauza)
- **+ / -** – szybsza / wolniejsza animacja
- **B** – **benchmark** (seria losowa, wyniki + wykresy w `matplotlib`)
- **M** – pokaż ostatnie wykresy (jeśli istnieją)
- **ESC** – wyjście

## Skrypty benchmarkowe

```bash
# 4 scenariusze (diag × wagi), wykresy + CSV
python scripts/bench_all.py

# Density sweep – wpływ gęstości przeszkód na A*/Dijkstra
python scripts/density_sweep.py
```

Wyniki zapisywane do `bench_S1/`–`bench_S4/` oraz `density_sweep/`.

## Struktura projektu

```
shortest_path_viz/
├── app/
│   ├── algorithms/
│   │   ├── astar.py
│   │   ├── bfs.py
│   │   ├── dijkstra.py
│   │   └── grid.py
│   ├── benchmark/
│   │   ├── runner.py
│   │   └── plots.py
│   ├── gui/
│   │   └── pygame_app.py
│   └── utils/
│       ├── heuristics.py
│       ├── metrics.py
│       └── timer.py
├── scripts/
│   ├── bench_all.py
│   └── density_sweep.py
├── run.py
├── requirements.txt
└── README.md
```

## Uwaga dot. A\* i wag

Heurystyka (Manhattan/Octile/Euklides) jest skalowana przez minimalny koszt kroku (domyślnie 1), dzięki czemu pozostaje dopuszczalna.
Przy sąsiedztwie 8 używana jest metryka **octile**. Dla grafów ważonych (pola „błoto” o koszcie 5) BFS nie gwarantuje optymalności – aplikacja to sygnalizuje i nie pozwala uruchomić BFS.

