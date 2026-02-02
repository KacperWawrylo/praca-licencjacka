
import math

def manhattan(a, b):
    ax, ay = a
    bx, by = b
    return abs(ax - bx) + abs(ay - by)

def euclidean(a, b):
    ax, ay = a
    bx, by = b
    return math.hypot(ax - bx, ay - by)

def octile(a, b):
    """Octile distance dla siatek z sąsiedztwem 8 (D=1, D2=sqrt(2))."""
    ax, ay = a
    bx, by = b
    dx = abs(ax - bx)
    dy = abs(ay - by)
    D = 1.0
    D2 = math.sqrt(2.0)
    return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)

def scaled(h_func, scale=1.0):
    """Zwraca funkcję heurystyczną skalowaną przez scale (min koszt kroku)."""
    def h(a, b):
        return scale * h_func(a, b)
    return h
