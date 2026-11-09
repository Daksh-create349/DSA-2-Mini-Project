"""
Brute Force Approach: Linear Scan
Range Minimum Query with Point Updates

Complexities:
- Build: O(n) including copying the input
- Query: O(n) worst case
- Point update: O(1)
- Auxiliary space: O(n) for the copied array; O(1) query workspace
"""

class LinearScan:
    def __init__(self, arr):
        if not arr:
            raise ValueError("Array must not be empty.")
        self.arr = list(arr)

    def query(self, left, right):
        if not (0 <= left <= right < len(self.arr)):
            raise ValueError("Invalid range: require 0 <= left <= right < n.")

        minimum = self.arr[left]
        for i in range(left + 1, right + 1):
            if self.arr[i] < minimum:
                minimum = self.arr[i]
        return minimum

    def update(self, index, value):
        if not 0 <= index < len(self.arr):
            raise IndexError("Update index is out of bounds.")
        self.arr[index] = value


if __name__ == "__main__":
    values = [8, 5, 9, 3, 7, 6, 2, 4]
    rmq = LinearScan(values)

    print("Brute Force - Linear Scan")
    print("Array:", values)
    print("Minimum in [1, 6]:", rmq.query(1, 6))  # 2

    rmq.update(6, 10)
    print("After updating index 6 to 10:", rmq.arr)
    print("Minimum in [1, 6]:", rmq.query(1, 6))  # 3
