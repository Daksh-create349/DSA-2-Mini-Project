class SegmentTree:
    def __init__(self, arr):
        if not arr:
            raise ValueError("Array must not be empty.")
        self.arr = list(arr)
        self.n = len(self.arr)

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
    n = int(input("Enter road size: "))
    arr = list(map(int, input("Enter array entries (space-separated): ").split()))
    while len(arr) < n:
        arr.extend(map(int, input().split()))
    arr = arr[:n]

    rmq = SegmentTree(arr)

    left, right = map(int, input("Enter range for lowest score (left right): ").split())
    print("Lowest score in range:", rmq.query(left, right))

    index, val = map(int, input("Enter update (index new_value): ").split())
    rmq.update(index, val)
    print("Updated array:", rmq.arr)
    print("Lowest score in range after update:", rmq.query(left, right))

