"""
priority_queue.py
-----------------
A generic binary max-heap–based Priority Queue supporting:
  - insert(task)
  - extract_max()
  - increase_key(task_id, new_priority)
  - decrease_key(task_id, new_priority)   [bonus – mirrors increase_key]
  - peek()
  - is_empty()

A companion Task dataclass stores the information required for a
task-scheduling simulation (task_id, priority, arrival_time, deadline,
description).

Design choice: Python list as the underlying array
--------------------------------------------------
A Python list gives O(1) amortised append and O(1) index access, which maps
directly onto the array-based binary-heap formulas for parent / child indices.
No extra pointer indirection (as in a linked representation) is needed, and
cache locality is good because elements are stored contiguously.  A
dict (self._index) is maintained in parallel so that increase/decrease_key
can locate any task in O(1) instead of O(n), keeping those operations O(log n).

Heap choice: max-heap
---------------------
A max-heap is natural for a "highest-priority-first" scheduler.  The task
with the numerically largest priority value is always at the root and can
be extracted in O(log n).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Task dataclass
# ---------------------------------------------------------------------------

@dataclass(order=False)          # We compare tasks only via priority
class Task:
    """
    Represents a single schedulable task.

    Attributes
    ----------
    task_id      : unique string identifier
    priority     : integer priority (higher = more urgent)
    arrival_time : simulation time-step when the task arrived
    deadline     : simulation time-step by which the task must complete
    description  : human-readable label
    """
    task_id:      str
    priority:     int
    arrival_time: int   = 0
    deadline:     int   = field(default=9_999_999)
    description:  str   = ""

    def __repr__(self) -> str:
        return (f"Task(id={self.task_id!r}, priority={self.priority}, "
                f"arrival={self.arrival_time}, deadline={self.deadline})")


# ---------------------------------------------------------------------------
# MaxHeap-based Priority Queue
# ---------------------------------------------------------------------------

class PriorityQueue:
    """
    Max-heap priority queue where the Task with the *highest* priority
    value is served first.

    Internal representation
    -----------------------
    self._heap  : list[Task]        – the heap array (0-indexed)
    self._index : dict[str, int]    – maps task_id -> current heap index
                                      for O(1) look-up in change_key ops
    """

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        self._heap:  list[Task]       = []
        self._index: dict[str, int]   = {}

    # ------------------------------------------------------------------
    # Index arithmetic
    # ------------------------------------------------------------------

    @staticmethod
    def _parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _left(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _right(i: int) -> int:
        return 2 * i + 2

    # ------------------------------------------------------------------
    # Swap helper (keeps _index consistent)
    # ------------------------------------------------------------------

    def _swap(self, i: int, j: int) -> None:
        """Swap heap[i] and heap[j] and update the index map."""
        self._index[self._heap[i].task_id] = j
        self._index[self._heap[j].task_id] = i
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    # ------------------------------------------------------------------
    # Restore heap property
    # ------------------------------------------------------------------

    def _sift_up(self, i: int) -> None:
        """
        Move element at index *i* upward until the heap property holds.
        Used after insert and increase_key.  O(log n).
        """
        while i > 0:
            p = self._parent(i)
            if self._heap[i].priority > self._heap[p].priority:
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i: int) -> None:
        """
        Move element at index *i* downward until the heap property holds.
        Used after extract_max and decrease_key.  O(log n).
        """
        n = len(self._heap)
        while True:
            largest = i
            l = self._left(i)
            r = self._right(i)

            if l < n and self._heap[l].priority > self._heap[largest].priority:
                largest = l
            if r < n and self._heap[r].priority > self._heap[largest].priority:
                largest = r

            if largest != i:
                self._swap(i, largest)
                i = largest
            else:
                break

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_empty(self) -> bool:
        """
        Return True if the priority queue contains no tasks.

        Time complexity: O(1).
        """
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)

    def peek(self) -> Optional[Task]:
        """
        Return (but do not remove) the highest-priority task.

        Time complexity: O(1) – the max is always at index 0.
        Returns None if the queue is empty.
        """
        return self._heap[0] if self._heap else None

    def insert(self, task: Task) -> None:
        """
        Add *task* to the priority queue.

        Steps
        -----
        1. Append the task to the end of the heap array: O(1) amortised.
        2. Sift the new element upward to restore the max-heap property: O(log n).

        Time complexity: **O(log n)** overall.

        Raises
        ------
        ValueError if a task with the same task_id already exists.
        """
        if task.task_id in self._index:
            raise ValueError(f"Task '{task.task_id}' is already in the queue.")
        self._heap.append(task)
        idx = len(self._heap) - 1
        self._index[task.task_id] = idx
        self._sift_up(idx)

    def extract_max(self) -> Task:
        """
        Remove and return the task with the highest priority.

        Steps
        -----
        1. Record the root (maximum) task.
        2. Move the last element to the root: O(1).
        3. Remove the last position: O(1) amortised.
        4. Sift the new root downward to restore the heap property: O(log n).

        Time complexity: **O(log n)** overall.

        Raises
        ------
        IndexError if the queue is empty.
        """
        if self.is_empty():
            raise IndexError("extract_max called on an empty priority queue.")

        # Swap root with last element, then remove last.
        self._swap(0, len(self._heap) - 1)
        max_task = self._heap.pop()
        del self._index[max_task.task_id]

        if self._heap:          # Restore heap property if elements remain.
            self._sift_down(0)

        return max_task

    def increase_key(self, task_id: str, new_priority: int) -> None:
        """
        Increase the priority of an existing task.

        Steps
        -----
        1. Locate the task in O(1) via the index map.
        2. Validate the new priority is higher.
        3. Update the priority.
        4. Sift the task upward: O(log n).

        Time complexity: **O(log n)** overall.

        Raises
        ------
        KeyError   if task_id is not in the queue.
        ValueError if new_priority <= current priority (use decrease_key instead).
        """
        if task_id not in self._index:
            raise KeyError(f"Task '{task_id}' not found in the priority queue.")
        i = self._index[task_id]
        if new_priority <= self._heap[i].priority:
            raise ValueError(
                f"New priority {new_priority} must be strictly greater than "
                f"current priority {self._heap[i].priority}. "
                "Use decrease_key to lower a priority."
            )
        self._heap[i].priority = new_priority
        self._sift_up(i)

    def decrease_key(self, task_id: str, new_priority: int) -> None:
        """
        Decrease the priority of an existing task.

        Steps
        -----
        1. Locate the task in O(1) via the index map.
        2. Validate the new priority is lower.
        3. Update the priority.
        4. Sift the task downward: O(log n).

        Time complexity: **O(log n)** overall.

        Raises
        ------
        KeyError   if task_id is not in the queue.
        ValueError if new_priority >= current priority (use increase_key instead).
        """
        if task_id not in self._index:
            raise KeyError(f"Task '{task_id}' not found in the priority queue.")
        i = self._index[task_id]
        if new_priority >= self._heap[i].priority:
            raise ValueError(
                f"New priority {new_priority} must be strictly less than "
                f"current priority {self._heap[i].priority}. "
                "Use increase_key to raise a priority."
            )
        self._heap[i].priority = new_priority
        self._sift_down(i)

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"PriorityQueue({self._heap!r})"


# ---------------------------------------------------------------------------
# Quick self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== PriorityQueue self-test ===\n")
    pq = PriorityQueue()

    tasks = [
        Task("T1", priority=10, arrival_time=0, deadline=50, description="Low-priority batch job"),
        Task("T2", priority=40, arrival_time=1, deadline=10, description="Critical user request"),
        Task("T3", priority=25, arrival_time=2, deadline=30, description="Background sync"),
        Task("T4", priority=5,  arrival_time=3, deadline=100, description="Analytics aggregation"),
        Task("T5", priority=55, arrival_time=4, deadline=5,  description="Emergency alert"),
    ]

    print("Inserting tasks:")
    for t in tasks:
        pq.insert(t)
        print(f"  inserted {t}  | heap size={len(pq)}")

    print(f"\nPeek (should be T5, priority=55): {pq.peek()}")

    print("\nIncrease T1 priority 10 -> 60:")
    pq.increase_key("T1", 60)
    print(f"  Peek now (should be T1, priority=60): {pq.peek()}")

    print("\nDecrease T1 priority 60 -> 1:")
    pq.decrease_key("T1", 1)
    print(f"  Peek now (should be T5, priority=55): {pq.peek()}")

    print("\nExtracting all tasks in priority order:")
    while not pq.is_empty():
        t = pq.extract_max()
        print(f"  {t}")

    print("\nQueue empty?", pq.is_empty())
