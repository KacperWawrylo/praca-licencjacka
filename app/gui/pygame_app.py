
import pygame
import sys
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from app.algorithms.grid import Grid
from app.algorithms.bfs import bfs
from app.algorithms.dijkstra import dijkstra
from app.algorithms.astar import astar
from app.utils.heuristics import manhattan, octile, scaled, euclidean
from app.benchmark.runner import run_bench, TrialConfig
from app.benchmark.plots import save_all_plots

CELL = 3
MARGIN = 1
PANEL_W = 400
FONT_SIZE = 16

class AppState:
    def __init__(self, config: Optional[TrialConfig] = None, cols=30, rows=22):
        self.config = config or TrialConfig()

        self.cols = self.config.cols if config else cols
        self.rows = self.config.rows if config else rows
        self.grid = Grid(self.cols, self.rows, diag=False)
        self.paused = False
        self.step_once = False
        self.speed_ms = 10  # opóźnienie animacji (ms/step)
        self.last_results = None  # wyniki benchmarków

def draw_text(surface, font, text, x, y):
    surf = font.render(text, True, (240,240,240))
    surface.blit(surf, (x, y))

def cell_rect(x, y):
    return (x*(CELL+MARGIN)+MARGIN, y*(CELL+MARGIN)+MARGIN, CELL, CELL)

def draw_grid(surface, state: AppState, font):
    grid = state.grid
    for x in range(grid.cols):
        for y in range(grid.rows):
            rect = pygame.Rect(*cell_rect(x, y))
            color = (30,30,30)
            if (x,y) in grid.walls:
                color = (100,100,100)
            elif (x,y) in grid.weighted:
                color = (60,60,120)
            pygame.draw.rect(surface, color, rect)
    # start/goal
    if grid.start:
        pygame.draw.rect(surface, (40,140,40), pygame.Rect(*cell_rect(*grid.start)))
    if grid.goal:
        pygame.draw.rect(surface, (160,50,50), pygame.Rect(*cell_rect(*grid.goal)))

def draw_overlay(surface, font, state: AppState):
    x0 = state.cols*(CELL+MARGIN)+MARGIN + 10
    y = 10
    draw_text(surface, font, "Skróty:", x0, y); y+=22
    for s in [
        "LPM: przeszkody",
        "PPM: START/CEL",
        "1: BFS   2: Dijkstra   3: A*",
        f"H: sąsiedztwo {4 if not state.grid.diag else 8}",
        "W: losowy labirynt",
        "G: tryb wag (maluj)",
        "R: reset planszy",
        "Spacja: pauza/wznów",
        "S: krok (gdy pauza)",
        "+/-: szybciej/wolniej",
        "B: benchmarky",
        "M: pokaż wykresy",
        "ESC: wyjście",
    ]:
        draw_text(surface, font, s, x0, y); y+=18

    y+=10
    draw_text(surface, font, f"Szybkość animacji: {state.speed_ms} ms/step", x0, y); y+=18
    draw_text(surface, font, f"Pauza: {'TAK' if state.paused else 'nie'}", x0, y); y+=18
    draw_text(surface, font, f"Sąsiedztwo: {'8' if state.grid.diag else '4'}", x0, y); y+=18
    draw_text(surface, font, f"Wagi aktywne: {'TAK' if state.grid.weighted else 'nie'}", x0, y); y+=18
    if state.last_results:
        draw_text(surface, font, "Ostatni benchmark: wyniki zapisano.", x0, y); y+=18

def animate_path(surface, state: AppState, font, explored: List[Tuple[int,int]], path: List[Tuple[int,int]]):
    clock = pygame.time.Clock()
    grid = state.grid
    # animacja odwiedzeń
    for u in explored:
        # reaguj na pauzę/krok
        waiting = True
        while state.paused and waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # wznów/pauza
                        state.paused = not state.paused
                        waiting = not waiting
                    elif event.key == pygame.K_s:  # krok
                        state.step_once = True
                        waiting = False
            pygame.time.delay(10)
        if state.step_once:
            state.step_once = False
            # wykona jeden krok i wraca do pauzy
            pass

        rect = pygame.Rect(*cell_rect(*u))
        pygame.draw.rect(surface, (80,80,160), rect)
        if grid.start:
            pygame.draw.rect(surface, (40,140,40), pygame.Rect(*cell_rect(*grid.start)))
        if grid.goal:
            pygame.draw.rect(surface, (160,50,50), pygame.Rect(*cell_rect(*grid.goal)))
        pygame.display.flip()
        if state.speed_ms > 0:
            pygame.time.delay(state.speed_ms)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    state.paused = not state.paused
                elif event.key == pygame.K_s and state.paused:
                    state.step_once = True

    # animacja ścieżki
    for u in path:
        waiting = True
        while state.paused and waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        state.paused = not state.paused
                        waiting = not waiting
                    elif event.key == pygame.K_s:
                        state.step_once = True
                        waiting = False
            pygame.time.delay(10)
        if state.step_once:
            state.step_once = False

        rect = pygame.Rect(*cell_rect(*u))
        pygame.draw.rect(surface, (200,200,60), rect)
        pygame.display.flip()
        pygame.time.delay(max(5, state.speed_ms//2))
def perform_search(surface, state: AppState, font, algo_name: str):
    g = state.grid
    if not g.start or not g.goal:
        return
    # kopia tła
    base = surface.copy()
    # uruchom wybrany algorytm
    try:
        if algo_name == "BFS":
            result = bfs(g)
        elif algo_name == "Dijkstra":
            result = dijkstra(g)
        elif algo_name == "A*":
            base_h = octile if g.diag else manhattan
            h = scaled(base_h, scale=g.min_step_cost())
            result = astar(g, h)
        else:
            return
    except Exception as e:
        # komunikat
        x0 = g.cols*(CELL+MARGIN)+MARGIN + 10
        draw_text(surface, font, f"Nie można uruchomić: {e}", x0, 420)
        pygame.display.flip()
        pygame.time.delay(1200)
        return

    # odtwórz tło i animuj
    surface.blit(base, (0,0))
    pygame.display.flip()
    animate_path(surface, state, font, result.explored_order, result.path)

    # NOWE: Zatrzymaj się i pokaż wynik
    # Najpierw narysuj cały interfejs od nowa (żeby panel był widoczny)
    surface.fill((15, 15, 20))
    draw_grid(surface, state, font)
    pygame.draw.rect(surface, (25, 25, 30),
                     pygame.Rect(state.cols * (CELL + MARGIN) + MARGIN, 0, PANEL_W, g.rows * (CELL + MARGIN) + MARGIN))
    draw_overlay(surface, font, state)

    # Dorysuj animację (odwiedzone pola)
    for u in result.explored_order:
        rect = pygame.Rect(*cell_rect(*u))
        pygame.draw.rect(surface, (80, 80, 160), rect)

    # Dorysuj ścieżkę
    for u in result.path:
        rect = pygame.Rect(*cell_rect(*u))
        pygame.draw.rect(surface, (200, 200, 60), rect)

    # Dorysuj start/goal na wierzchu
    if g.start:
        pygame.draw.rect(surface, (40, 140, 40), pygame.Rect(*cell_rect(*g.start)))
    if g.goal:
        pygame.draw.rect(surface, (160, 50, 50), pygame.Rect(*cell_rect(*g.goal)))

    # Wyświetl statystyki
    x0 = g.cols * (CELL + MARGIN) + MARGIN + 10
    y_start = 350
    draw_text(surface, font, f"--- {algo_name} ZAKOŃCZONY ---", x0, y_start)
    draw_text(surface, font, f"Długość ścieżki: {result.path_length()}", x0, y_start + 25)
    draw_text(surface, font, f"Koszt: {result.total_cost:.1f}", x0, y_start + 45)
    draw_text(surface, font, f"Odwiedzone: {result.visited_count}", x0, y_start + 65)
    draw_text(surface, font, f"Rozwinięcia: {result.expanded_count}", x0, y_start + 85)
    draw_text(surface, font, f"Czas: {result.time_s * 1000:.2f} ms", x0, y_start + 105)
    draw_text(surface, font, "", x0, y_start + 130)
    draw_text(surface, font, "Naciśnij klawisz aby kontynuować", x0, y_start + 150)
    pygame.display.flip()

    # Czekaj na naciśnięcie klawisza
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        pygame.time.delay(10)

def show_plots(paths: dict):
    # Pokaż zapisane obrazy w prostym oknie pygame (sekwencyjnie)
    if not paths:
        return

    old_surface = pygame.display.get_surface()
    old_size = old_surface.get_size()
    old_caption = pygame.display.get_caption()[0]

    display_info = pygame.display.Info()
    max_width, max_height = display_info.current_w - 100, display_info.current_h - 100

    for title, p in paths.items():
        img = pygame.image.load(p)
        w, h = img.get_width(), img.get_height()

        #skalowanko obrazu jak za duży
        scale_factor = 1.0
        if w>max_width or h>max_height:
            scale_w = max_width / w
            scale_h = max_height / h
            scale_factor = min(scale_w, scale_h)

            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            img = pygame.transform.smoothscale(img, (new_w, new_h))
            w, h = new_w, new_h


        screen = pygame.display.set_mode((w, h))
        screen.blit(img, (0,0))
        pygame.display.set_caption(title)
        pygame.display.flip()
        showing = True
        while showing:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                    showing = False
                    break

    screen = pygame.display.set_mode(old_size)
    pygame.display.set_caption(old_caption)
    return screen

def main():
    pygame.init()
    cfg = TrialConfig()
    state = AppState(config=cfg)
    W = state.cols*(CELL+MARGIN)+MARGIN + PANEL_W
    H = state.rows*(CELL+MARGIN)+MARGIN
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Porównanie BFS / Dijkstra / A* (pygame)")
    font = pygame.font.SysFont("consolas", FONT_SIZE)

    clock = pygame.time.Clock()
    painting_weights = False

    while True:
        screen.fill((15,15,20))
        draw_grid(screen, state, font)
        pygame.draw.rect(screen, (25,25,30), pygame.Rect(state.cols*(CELL+MARGIN)+MARGIN, 0, PANEL_W, H))
        draw_overlay(screen, font, state)
        pygame.display.flip()



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit(0)
                elif event.key == pygame.K_h:
                    state.grid.diag = not state.grid.diag
                elif event.key == pygame.K_r:
                    state.grid.walls.clear()
                    state.grid.clear_weights()
                elif event.key == pygame.K_w:
                    state.grid.randomize_walls(state.config.wall_density)
                elif event.key == pygame.K_g:
                    painting_weights = not painting_weights
                elif event.key == pygame.K_1:
                    perform_search(screen, state, font, "BFS")
                elif event.key == pygame.K_2:
                    perform_search(screen, state, font, "Dijkstra")
                elif event.key == pygame.K_3:
                    perform_search(screen, state, font, "A*")
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    state.speed_ms = max(0, state.speed_ms - 5)
                elif event.key == pygame.K_MINUS:
                    state.speed_ms = min(200, state.speed_ms + 5)
                elif event.key == pygame.K_SPACE:
                    state.paused = not state.paused
                elif event.key == pygame.K_s:
                    if state.paused:
                        state.step_once = True
                elif event.key == pygame.K_b:
                    # uruchom benchmarki
                    cfg = TrialConfig(
                        diag=state.grid.diag,
                        weight_density=0.10 if state.grid.weighted else 0.0
                    )
                    results = run_bench(cfg)
                    out_dir = str(Path.cwd() / "benchmark_plots")
                    paths = save_all_plots(results, out_dir)
                    state.last_results = paths
                    screen = show_plots(paths)
                elif event.key == pygame.K_m:
                    if state.last_results:
                        screen = show_plots(state.last_results)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                cx = x // (CELL+MARGIN)
                cy = y // (CELL+MARGIN)
                if 0 <= cx < state.cols and 0 <= cy < state.rows:
                    c = (cx, cy)
                    if event.button == 1:  # LPM
                        if painting_weights:
                            # maluj/wymazuj wagi
                            if c in state.grid.weighted:
                                state.grid.weighted.pop(c, None)
                            else:
                                if c != state.grid.start and c != state.grid.goal and c not in state.grid.walls:
                                    state.grid.weighted[c] = 5
                        else:
                            # maluj ściany
                            if c == state.grid.start or c == state.grid.goal:
                                pass
                            elif c in state.grid.walls:
                                state.grid.walls.remove(c)
                            else:
                                if c not in state.grid.weighted:
                                    state.grid.walls.add(c)
                    elif event.button == 3:  # PPM
                        if state.grid.start is None:
                            state.grid.start = c
                            state.grid.walls.discard(c)
                            state.grid.weighted.pop(c, None)
                        elif state.grid.goal is None:
                            state.grid.goal = c
                            state.grid.walls.discard(c)
                            state.grid.weighted.pop(c, None)
                        else:
                            # zamień: start -> kliknięte, poprzedni start staje się zwykłym polem
                            state.grid.start = c
                            state.grid.walls.discard(c)
                            state.grid.weighted.pop(c, None)

        clock.tick(60)

if __name__ == "__main__":
    main()
