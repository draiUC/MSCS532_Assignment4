# Assignment 4: Heap Data Structures

Implementation, empirical analysis, and scheduling application of Heapsort
and a binary max-heap Priority Queue.

---

## Repository Structure

```
.
├── heapsort.py           # Heapsort implementation
├── priority_queue.py     # PriorityQueue + Task dataclass
├── benchmark.py          # Empirical comparison: Heap / Merge / Quick / Timsort
├── benchmark_results.csv # Generated timing data (created on first run)
└── README.md             # This file
```

---

## Requirements

- Python 3.9 or later (uses `from __future__ import annotations`)
- No third-party packages required

---

## How to Run

### 1. Heapsort self-test

```bash
python heapsort.py
```

Runs six edge-case tests (random, sorted, reverse-sorted, all-equal,
single element, empty) and prints PASS/FAIL for each.

### 2. Priority Queue self-test

```bash
python priority_queue.py
```

Inserts five tasks, demonstrates `peek`, `increase_key`, `decrease_key`,
and extracts all tasks in descending priority order.

### 3. Sorting benchmark

```bash
python benchmark.py
```

Compares Heapsort, Mergesort, Quicksort (randomised pivot), and Python's
built-in Timsort on:
- Three distributions: random, sorted, reverse-sorted
- Six sizes: 100 · 500 · 1 000 · 5 000 · 10 000 · 50 000

Results are printed to stdout and saved to `benchmark_results.csv`.

---

## Summary of Findings

| Algorithm | Worst case | Average | Best | In-place? |
|---|---|---|---|---|
| **Heapsort** | O(n log n) | O(n log n) | O(n log n) | Yes |
| Mergesort | O(n log n) | O(n log n) | O(n log n) | No |
| Quicksort | O(n²) | O(n log n) | O(n log n) | Yes |
| Timsort | O(n log n) | O(n log n) | O(n) | No |

**Heapsort** is the only comparison sort that is simultaneously in-place
and O(n log n) in the worst case. In practice it runs 1.7–2× slower than
Mergesort due to poor cache locality from its non-sequential memory access
pattern, and roughly 2–3× slower than randomised Quicksort for the same
reason.

**Priority Queue operations** (insert, extract-max, increase-key,
decrease-key) all run in O(log n) time.  An auxiliary hash map keeps
key-change operations at O(log n) rather than O(n).

---

