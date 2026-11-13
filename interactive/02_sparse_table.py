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
    n = int(input("Enter road size: "))
    arr = list(map(int, input("Enter array entries (space-separated): ").split()))
    while len(arr) < n:
        arr.extend(map(int, input().split()))
    arr = arr[:n]

    rmq = SparseTable(arr)

    left, right = map(int, input("Enter range for lowest score (left right): ").split())
    print("Lowest score in range:", rmq.query(left, right))

    index, val = map(int, input("Enter update (index new_value): ").split())
    rmq.update(index, val)
    print("Updated array:", rmq.arr)
    print("Lowest score in range after update:", rmq.query(left, right))

