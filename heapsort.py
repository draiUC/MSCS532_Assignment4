"""
heapsort.py
-----------
Heapsort implementation using a max-heap.

Steps:
  1. Build a max-heap from the input array (O(n)).
  2. Repeatedly extract the maximum element, placing it at the end
     of the array and reducing the heap size by 1 (O(n log n)).

Time Complexity : O(n log n) – worst, average, and best cases.
Space Complexity: O(1) auxiliary – in-place sort.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Low-level heap helpers
# ---------------------------------------------------------------------------

def _left(i: int) -> int:
    """Return the index of the left child of node i."""
    return 2 * i + 1


def _right(i: int) -> int:
    """Return the index of the right child of node i."""
    return 2 * i + 2


def _max_heapify(arr: list, heap_size: int, i: int) -> None:
    """
    Restore the max-heap property rooted at index *i*.

    Assumes both subtrees rooted at _left(i) and _right(i) already satisfy
    the max-heap property.  Runs in O(log n) time.

    Parameters
    ----------
    arr       : mutable list being heapified in-place
    heap_size : number of elements currently in the heap (a suffix of arr)
    i         : root index whose subtree we want to fix
    """
    largest = i
    l = _left(i)
    r = _right(i)

    if l < heap_size and arr[l] > arr[largest]:
        largest = l
    if r < heap_size and arr[r] > arr[largest]:
        largest = r

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        _max_heapify(arr, heap_size, largest)


def build_max_heap(arr: list) -> None:
    """
    Convert an arbitrary list into a max-heap **in-place**.

    The naive approach calls _max_heapify on every node (O(n log n)), but the
    Floyd / bottom-up build only calls it on the n/2 non-leaf nodes, and the
    work at shallow nodes is bounded by smaller subtree heights.  The total
    cost telescopes to **O(n)**.

    Parameters
    ----------
    arr : list to be converted into a max-heap in-place
    """
    n = len(arr)
    # Start from the last non-leaf and work upward.
    for i in range(n // 2 - 1, -1, -1):
        _max_heapify(arr, n, i)


# ---------------------------------------------------------------------------
# Heapsort
# ---------------------------------------------------------------------------

def heapsort(arr: list) -> list:
    """
    Sort *arr* in ascending order using Heapsort and return the sorted list.

    The sort is performed **in-place**; the original list is also mutated.

    Algorithm
    ---------
    1. Build a max-heap: O(n).
    2. For i from n-1 down to 1:
         a. Swap arr[0] (maximum) with arr[i].
         b. Decrease heap_size by 1.
         c. Call _max_heapify on the root: O(log n).
       Total for this phase: O(n log n).

    Parameters
    ----------
    arr : list of comparable elements

    Returns
    -------
    The same list, sorted in ascending order.
    """
    n = len(arr)
    build_max_heap(arr)           # Phase 1 – O(n)

    for i in range(n - 1, 0, -1): # Phase 2 – O(n log n)
        arr[0], arr[i] = arr[i], arr[0]   # Place max at end
        _max_heapify(arr, i, 0)            # Restore heap on prefix arr[0..i-1]

    return arr


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import random

    test_cases = [
        ("random",         [random.randint(0, 1000) for _ in range(20)]),
        ("sorted",         list(range(15))),
        ("reverse-sorted", list(range(14, -1, -1))),
        ("all equal",      [7] * 10),
        ("single element", [42]),
        ("empty",          []),
    ]

    all_pass = True
    for name, data in test_cases:
        original = data[:]
        result   = heapsort(data)
        expected = sorted(original)
        ok = result == expected
        all_pass = all_pass and ok
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name:20s}  input={original}  output={result}")

    print()
    print("All tests passed." if all_pass else "SOME TESTS FAILED.")
