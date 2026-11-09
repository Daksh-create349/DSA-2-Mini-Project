"""
Dynamic Approach: Segment Tree
Range Minimum Query with Point Updates

Complexities:
- Build: O(n)
- Query: O(log n)
- Point update: O(log n)
- Auxiliary space: O(n)

Among these three approaches, the Segment Tree is the suitable choice
when both range queries and point updates must be efficient.
"""

class SegmentTree:
    def __init__(self, arr):
        if not arr:
            raise ValueError("Array must not be empty.")

        self.arr = list(arr)
        self.n = len(self.arr)

        # Padding to the next power of two handles arbitrary array lengths.
        self.size = 1
        while self.size < self.n:
            self.size *= 2

        self.tree = [float("inf")] * (2 * self.size)

        for i, value in enumerate(self.arr):
            self.tree[self.size + i] = value

        for i in range(self.size - 1, 0, -1):
            self.tree[i] = min(self.tree[2 * i], self.tree[2 * i + 1])

    def query(self, left, right):
        if not (0 <= left <= right < self.n):
            raise ValueError("Invalid range: require 0 <= left <= right < n.")

        left += self.size
        right += self.size
        minimum = float("inf")

        while left <= right:
            if left % 2 == 1:
                minimum = min(minimum, self.tree[left])
                left += 1

            if right % 2 == 0:
                minimum = min(minimum, self.tree[right])
                right -= 1

            left //= 2
            right //= 2

        return minimum

    def update(self, index, value):
        if not 0 <= index < self.n:
            raise IndexError("Update index is out of bounds.")

        self.arr[index] = value
        position = self.size + index
        self.tree[position] = value

        position //= 2
        while position >= 1:
            self.tree[position] = min(
                self.tree[2 * position],
                self.tree[2 * position + 1]
            )
            position //= 2


if __name__ == "__main__":
    values = [8, 5, 9, 3, 7, 6, 2, 4]
    rmq = SegmentTree(values)

    print("Dynamic Approach - Segment Tree")
    print("Array:", values)
    print("Minimum in [1, 6]:", rmq.query(1, 6))  # 2

    rmq.update(6, 10)
    print("After updating index 6 to 10:", rmq.arr)
    print("Minimum in [1, 6]:", rmq.query(1, 6))  # 3
