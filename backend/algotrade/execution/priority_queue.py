"""
AlgoTrade Engine — Priority Queue (Max-Heap)
Maintains pending trade signals ranked by expected return.

DAA Paradigm: Heap Data Structure
O(n) heapify vs O(n log n) repeated insertion — benchmarked.
Uses Python heapq (min-heap) with negated values for max-heap behavior.
"""

import heapq


class MaxHeap:
    """
    Max-Heap using Python's heapq with negated values.
    insert:      O(log n)
    extract_max: O(log n)
    peek_max:    O(1)
    heapify:     O(n)
    """

    def __init__(self):
        self._heap = []
        self._count = 0  # Tiebreaker for equal priorities

    def insert(self, priority: float, item: dict):
        """Insert item with given priority. O(log n)."""
        self._count += 1
        # Negate priority for max-heap behavior; count breaks ties
        heapq.heappush(self._heap, (-priority, self._count, item))

    def extract_max(self) -> tuple[float, dict]:
        """Remove and return highest-priority item. O(log n)."""
        if not self._heap:
            raise IndexError("extract_max from empty heap")
        neg_priority, _, item = heapq.heappop(self._heap)
        return (-neg_priority, item)

    def peek_max(self) -> tuple[float, dict]:
        """View highest-priority item without removing. O(1)."""
        if not self._heap:
            raise IndexError("peek_max on empty heap")
        neg_priority, _, item = self._heap[0]
        return (-neg_priority, item)

    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return len(self._heap) > 0

    @classmethod
    def from_list(cls, items: list[tuple[float, dict]]) -> "MaxHeap":
        """
        Build heap from list in O(n) using heapify.
        items: list of (priority, data_dict)
        """
        heap = cls()
        heap._heap = [(-p, i, d) for i, (p, d) in enumerate(items)]
        heap._count = len(items)
        heapq.heapify(heap._heap)  # O(n) Floyd's algorithm
        return heap


def build_heap_repeated_insertion(items: list[tuple[float, dict]]) -> MaxHeap:
    """Build heap via repeated insertion — O(n log n). For benchmarking."""
    heap = MaxHeap()
    for priority, data in items:
        heap.insert(priority, data)
    return heap


def build_heap_heapify(items: list[tuple[float, dict]]) -> MaxHeap:
    """Build heap via heapify — O(n). For benchmarking."""
    return MaxHeap.from_list(items)
