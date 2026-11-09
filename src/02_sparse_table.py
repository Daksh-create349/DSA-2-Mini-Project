"""
Better Static-Query Approach: Sparse Table
Range Minimum Query with Point Updates (via full rebuild)

Complexities:
- Build: O(n log n)
- Query: O(1)
- Point update: O(n log n), because the table is rebuilt
- Auxiliary space: O(n log n)

A Sparse Table is best when the array is static and there are many queries.
It is not suitable for frequent point updates.
"""

class SparseTable:
    def __init__(self, arr):
        if not arr:
            raise ValueError("Array must not be empty.")
        self.arr = list(arr)
        self._build()

    def _build(self):
        n = len(self.arr)
        self.logs = [0] * (n + 1)

        for i in range(2, n + 1):
            self.logs[i] = self.logs[i // 2] + 1

        levels = self.logs[n] + 1
        self.table = [[0] * n for _ in range(levels)]
        self.table[0] = self.arr.copy()

        for k in range(1, levels):
            interval_length = 1 << k
            half = interval_length >> 1

            for i in range(n - interval_length + 1):
                self.table[k][i] = min(
                    self.table[k - 1][i],
                    self.table[k - 1][i + half]
                )

    def query(self, left, right):
        n = len(self.arr)
        if not (0 <= left <= right < n):
            raise ValueError("Invalid range: require 0 <= left <= right < n.")

        length = right - left + 1
        k = self.logs[length]
        block_length = 1 << k

        return min(
            self.table[k][left],
            self.table[k][right - block_length + 1]
        )

    def update(self, index, value):
        if not 0 <= index < len(self.arr):
            raise IndexError("Update index is out of bounds.")

        self.arr[index] = value
        self._build()


if __name__ == "__main__":
    values = [8, 5, 9, 3, 7, 6, 2, 4]
    rmq = SparseTable(values)

    print("Better Approach - Sparse Table")
    print("Array:", values)
    print("Minimum in [1, 6]:", rmq.query(1, 6))  # 2

    rmq.update(6, 10)
    print("After updating index 6 to 10:", rmq.arr)
    print("Minimum in [1, 6]:", rmq.query(1, 6))  # 3
