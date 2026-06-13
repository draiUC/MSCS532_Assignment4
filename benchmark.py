"""
benchmark.py
------------
Empirically compare Heapsort, Python's built-in Timsort (as a proxy for
Mergesort), and a recursive Quicksort on:
  - random arrays
  - already-sorted arrays
  - reverse-sorted arrays

across a range of input sizes.

Results are written to benchmark_results.csv and also printed to stdout.
"""

from __future__ import annotations

import csv
import random
import sys
import time
from typing import Callable

# Raise Python's recursion limit to handle large sorted arrays in Quicksort.
sys.setrecursionlimit(100_000)

# ── Local import ────────────────────────────────────────────────────────────
from heapsort import heapsort


# ---------------------------------------------------------------------------
# Reference sorting implementations
# ---------------------------------------------------------------------------

def mergesort(arr: list) -> list:
    """Standard top-down merge sort.  Returns a *new* sorted list."""
    if len(arr) <= 1:
        return arr[:]
    mid  = len(arr) // 2
    left  = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return _merge(left, right)


def _merge(left: list, right: list) -> list:
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quicksort(arr: list) -> list:
    """
    Randomised pivot quicksort.  Returns a *new* sorted list.
    Randomisation avoids worst-case O(n²) on sorted/reverse-sorted input.
    """
    if len(arr) <= 1:
        return arr[:]
    pivot = arr[random.randrange(len(arr))]
    less    = [x for x in arr if x <  pivot]
    equal   = [x for x in arr if x == pivot]
    greater = [x for x in arr if x >  pivot]
    return quicksort(less) + equal + quicksort(greater)


def timsort_wrapper(arr: list) -> list:
    """Python's built-in sort (Timsort) – returns a new sorted list."""
    return sorted(arr)


# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------

def time_sort(sort_fn: Callable[[list], list], data: list, repeats: int = 3) -> float:
    """
    Run *sort_fn* on a *copy* of *data* for *repeats* iterations and return
    the minimum elapsed time in milliseconds.  Using the minimum reduces
    noise from OS scheduling jitter.
    """
    best = float("inf")
    for _ in range(repeats):
        copy = data[:]
        t0   = time.perf_counter()
        sort_fn(copy)
        elapsed = (time.perf_counter() - t0) * 1_000   # convert to ms
        best = min(best, elapsed)
    return round(best, 4)


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------

SIZES        = [100, 500, 1_000, 5_000, 10_000, 50_000]
DISTRIBUTIONS = {
    "random":         lambda n: [random.randint(0, n * 10) for _ in range(n)],
    "sorted":         lambda n: list(range(n)),
    "reverse-sorted": lambda n: list(range(n - 1, -1, -1)),
}

ALGORITHMS = {
    "Heapsort":  heapsort,
    "Mergesort": mergesort,
    "Quicksort": quicksort,
    "Timsort":   timsort_wrapper,
}


def run_benchmark() -> list[dict]:
    rows = []
    for dist_name, gen in DISTRIBUTIONS.items():
        print(f"\n{'='*60}")
        print(f"Distribution: {dist_name}")
        print(f"{'='*60}")
        header = f"{'n':>8} | " + " | ".join(f"{name:>10}" for name in ALGORITHMS)
        print(header)
        print("-" * len(header))

        for n in SIZES:
            data = gen(n)
            row  = {"distribution": dist_name, "n": n}
            times = []
            for algo_name, fn in ALGORITHMS.items():
                ms = time_sort(fn, data)
                row[algo_name] = ms
                times.append(f"{ms:>10.4f}")
            rows.append(row)
            print(f"{n:>8} | " + " | ".join(times))

    return rows


def save_csv(rows: list[dict], path: str = "benchmark_results.csv") -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nResults saved to {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    random.seed(42)
    rows = run_benchmark()
    save_csv(rows)
