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
    n = int(input("Enter road size: "))
    arr = list(map(int, input("Enter array entries (space-separated): ").split()))
    while len(arr) < n:
        arr.extend(map(int, input().split()))
    arr = arr[:n]

    rmq = LinearScan(arr)

    left, right = map(int, input("Enter range for lowest score (left right): ").split())
    print("Lowest score in range:", rmq.query(left, right))

    index, val = map(int, input("Enter update (index new_value): ").split())
    rmq.update(index, val)
    print("Updated array:", rmq.arr)
    print("Lowest score in range after update:", rmq.query(left, right))

