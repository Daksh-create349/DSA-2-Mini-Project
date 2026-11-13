# The Complete RMQ Master Guide: From Zero to Viva-Ready in 4 Hours

> **Case Study No. 02:** Range Minimum Query (RMQ) with Point Updates  
> **Topic:** Linear Scan vs. Sparse Table vs. Segment Tree  
> **Target Audience:** Anyone preparing for an oral exam / viva voce, especially if you currently find algorithms and tree data structures intimidating or confusing.

---

## 4-Hour Study Schedule

If your viva is today or tomorrow, follow this exact timeline:

| Time | Goal | What to Read |
| :--- | :--- | :--- |
| **Hour 1 (0:00 - 1:00)** | The Problem & The Basics | Read **Chapters 1, 2, and 3** (The Road Analogy, Big-O, and Linear Scan). |
| **Hour 2 (1:00 - 2:00)** | Mastering Sparse Tables | Read **Chapter 4**. Draw the power-of-2 interval table on a piece of paper by hand. |
| **Hour 3 (2:00 - 3:00)** | Mastering Segment Trees | Read **Chapter 5**. Understand *why* `left % 2 == 1` works with the diagram. |
| **Hour 4 (3:00 - 4:00)** | Benchmark & Viva Rehearsal | Read **Chapters 6 & 7**. Practice saying the top viva answers out loud. |

---

# CHAPTER 1: The Problem Explained in Plain English

### The Real-World Scenario: The Highway Road Monitor
Imagine a long highway that is **30,000 kilometers long**.
We divide the highway into 30,000 separate 1-kilometer segments, numbered from `0` to `29,999`.

Every segment gets a **quality score** from `1` to `10`:
* `10` = Brand new, perfectly smooth highway.
* `1` = Deep potholes, hazardous driving surface.

An array representing a small 5-segment road looks like this:
```text
Index:   [  0  ]   [  1  ]   [  2  ]   [  3  ]   [  4  ]
Score:      8         5         9         3         7
```

---

### The Two Actions Our Program Must Perform

#### Action 1: Range Minimum Query (RMQ)
A government inspector or GPS navigation app asks:
> *"Between kilometer 1 and kilometer 3, what is the absolute worst score?"*

Looking at our array:
* Segment 1 has score `5`
* Segment 2 has score `9`
* Segment 3 has score `3`

The lowest score is **`3`**. Our program must return `3`.

#### Action 2: Point Update
A construction crew arrives at kilometer 3 and patches the pothole with fresh asphalt. Its quality score jumps from `3` to `10`.
```text
Before update: [8, 5, 9, 3, 7]
After update:  [8, 5, 9, 10, 7]
```
If the inspector now asks again: *"What is the minimum between kilometer 1 and kilometer 3?"*
The segments are now `5`, `9`, `10`. The answer has changed to **`5`**.

---

### The Engineering Dilemma
* If there are **30,000 kilometers**, and millions of GPS users query ranges every second while road crews are updating scores:
* **How do we organize our memory so both questions (Queries) and road repairs (Updates) happen in microseconds without crashing the computer?**

---

# CHAPTER 2: Foundational Concepts (No Jargon)

Before opening any code, you must understand these 4 core concepts. Professors test these heavily in viva.

### 1. What is an Inclusive Interval `[left, right]`?
In our project, when an inspector asks for `[1, 3]`, both index `1` and index `3` are included:
* Length of range = `right - left + 1` (for example, `3 - 1 + 1 = 3` elements).
* Zero-based indexing: The first element is at index `0`, and the last is at index `n - 1`.

### 2. What is Big-O Notation? (Speed in Simple Terms)
Big-O tells you how the work grows when the road gets bigger (`n` increases):

* **`O(1)` (Instant / Constant Time):** Takes the exact same split-second whether you have 10 elements or 10,000,000 elements. Looking up a known array index like `arr[5]` is `O(1)`.
* **`O(log n)` (Logarithmic Time / Super Fast):** Every step cuts the problem in half. 
  * If `n = 1,000`, `log2(1,000)` is only about 10 steps.
  * If `n = 1,000,000`, `log2(1,000,000)` is only about 20 steps.
  * Extremely fast and scalable!
* **`O(n)` (Linear Time / Slow for big data):** You must inspect every single item one-by-one. If `n = 30,000`, you take 30,000 steps.
* **`O(n log n)`:** Doing logarithmic work for all `n` elements. Common for sorting and prebuilding tables.

### 3. What is Idempotency? (THE MOST IMPORTANT VIVA WORD!)
An operation is called **idempotent** if applying it multiple times to the same input does not change the result:

```text
min(x, x) = x
```

* Example: `min(3, 3) = 3`. If you compare the same number twice, the minimum does not change!
* Compare this with addition: `3 + 3 = 6` (not 3!). Addition is **NOT** idempotent.
* **Why this matters:** Because minimum is idempotent, **Sparse Tables can use overlapping intervals to answer queries in `O(1)`!** If we were calculating sum, overlapping intervals would double-count numbers and give the wrong answer.

### 4. What are Powers of Two and Bit-Shifting?
Computer memory works in binary (powers of 2):
* `2^0 = 1`
* `2^1 = 2`
* `2^2 = 4`
* `2^3 = 8`
* `2^4 = 16`

In Python code, you will see bitwise operators:
* `1 << k` means `2^k`. Example: `1 << 3` is `8`.
* `x >> 1` means `x // 2` (integer division by 2). Example: `8 >> 1` is `4`.

---

# CHAPTER 3: Approach 1 — The Linear Scan (Brute Force)

### Intuition
Keep the numbers in a standard Python list. Do zero preparation.
* When asked for the minimum between `left` and `right`, start at `left`, walk element by element to `right`, keeping track of the smallest number seen so far.
* When an update happens at `index`, directly overwrite `arr[index] = new_value`.

```text
Array: [8, 5, 9, 3, 7]
Query [1, 4]:
  Start: smallest = arr[1] = 5
  Check index 2 (val 9): 9 < 5? No.  smallest = 5
  Check index 3 (val 3): 3 < 5? YES! smallest = 3
  Check index 4 (val 7): 7 < 3? No.  smallest = 3
  Return: 3
```

### Complexity
* **Build Time:** `O(n)` (just copying the input array).
* **Query Time:** `O(k)` where `k` is the range length; worst-case `O(n)` if checking the whole array.
* **Point Update Time:** `O(1)` (direct array assignment).
* **Auxiliary Space:** `O(n)` to store the array copy.

### Code Walkthrough (`src/01_linear_scan.py`)
```python
class LinearScan:
    def __init__(self, arr):
        # 1. Reject empty arrays as required by problem specification
        if not arr:
            raise ValueError("Array must not be empty.")
        # 2. Make an independent copy so external changes don't affect us
        self.arr = list(arr)

    def query(self, left, right):
        # Validate that indices are within 0 <= left <= right < n
        if not (0 <= left <= right < len(self.arr)):
            raise ValueError("Invalid range: require 0 <= left <= right < n.")

        # Walk through the range from left to right
        minimum = self.arr[left]
        for i in range(left + 1, right + 1):
            if self.arr[i] < minimum:
                minimum = self.arr[i]
        return minimum

    def update(self, index, value):
        # Validate index
        if not 0 <= index < len(self.arr):
            raise IndexError("Update index is out of bounds.")
        # Direct O(1) replacement
        self.arr[index] = value
```

---

# CHAPTER 4: Approach 2 — The Sparse Table

### Intuition: The Power-of-Two Cheat Sheet
Instead of scanning on every query, what if we precompute and write down the minimums in advance?
Writing down every single possible pair `(i, j)` would take `O(n^2)` space, which for `30,000` elements requires 900,000,000 entries (way too huge!).

**The Sparse Table Trick:** Only precompute intervals whose lengths are **powers of two** (`1, 2, 4, 8, 16, 32 ...`):
* Level 0 (`2^0 = 1`): Minimum of each interval of length 1 (just the array itself).
* Level 1 (`2^1 = 2`): Minimum of each interval of length 2.
* Level 2 (`2^2 = 4`): Minimum of each interval of length 4.
* Level `k` (`2^k`): Minimum of each interval of length `2^k`.

```text
Table Definition: table[k][i] = minimum in range [i, i + 2^k - 1]
```

### How to Build the Table (Dynamic Programming)
To find the minimum of an interval of length 4 starting at index `i`, we just look at the two halves of length 2 that we ALREADY computed in Level 1!

```text
table[k][i] = min(table[k-1][i], table[k-1][i + 2^(k-1)])
```

```text
Interval of length 4 starting at i:
[----------- Length 4 -----------]
[-- Length 2 --][-- Length 2 --]
  table[1][i]     table[1][i + 2]
```
Because each level takes `O(n)` and there are about `log2(n)` levels, building the entire table takes **`O(n log n)` time and space**.

---

### How to Answer ANY Query in `O(1)` Time
Suppose someone asks for a range of length `L = right - left + 1`.
1. Find the largest power of 2 that fits inside `L`. Let this be `k = floor(log2(L))`. Let `block = 2^k`.
2. Note that `2 * block >= L`. That means **two blocks of size `2^k` can completely cover the entire range by overlapping in the middle!**
   * Block 1 starts at `left`: covers `[left, left + block - 1]`
   * Block 2 ends at `right`: starts at `right - block + 1`, covers `[right - block + 1, right]`

```text
Requested range [1, 5] (Length = 5).
Largest power of 2 <= 5 is 4 (k = 2, block = 2^2 = 4).

Block 1 (starts at 1, length 4): [1, 2, 3, 4]
Block 2 (ends at 5, length 4):      [2, 3, 4, 5]
                                    ^-----^
                                 Overlapping part!
```
Because taking the minimum of the overlap twice does not hurt (`min(x, x) = x` is idempotent):

```text
Answer = min(table[k][left], table[k][right - block + 1])
```

**This is just TWO table lookups and ONE comparison. Time taken: `O(1)` constant time!**

---

### The Fatal Flaw: Why Updates are Terrible
If the inspector changes even **one single road score**:
* That score is part of many precomputed blocks in Level 0, Level 1, Level 2...
* In this project, to keep the data structure strictly correct and simple, an update calls `self._build()`, which **rebuilds the entire table from scratch**.
* Update time: **`O(n log n)`**!
  * At `n = 30,000`, an update takes **`70.7 ms`** (over 70,000 microseconds!).

### Code Walkthrough (`src/02_sparse_table.py`)
```python
class SparseTable:
    def __init__(self, arr):
        if not arr:
            raise ValueError("Array must not be empty.")
        self.arr = list(arr)
        self._build()

    def _build(self):
        n = len(self.arr)
        
        # 1. Precompute integer logarithms to avoid slow math.log2() calls later
        # logs[length] gives floor(log2(length))
        self.logs = [0] * (n + 1)
        for i in range(2, n + 1):
            self.logs[i] = self.logs[i // 2] + 1

        levels = self.logs[n] + 1
        self.table = [[0] * n for _ in range(levels)]
        # Level 0 is just the input array itself (intervals of length 2^0 = 1)
        self.table[0] = self.arr.copy()

        # Fill table level by level
        for k in range(1, levels):
            interval_length = 1 << k        # 2^k
            half = interval_length >> 1     # 2^(k-1)

            for i in range(n - interval_length + 1):
                # Combine two halves from the previous level
                self.table[k][i] = min(
                    self.table[k - 1][i],
                    self.table[k - 1][i + half]
                )

    def query(self, left, right):
        n = len(self.arr)
        if not (0 <= left <= right < n):
            raise ValueError("Invalid range: require 0 <= left <= right < n.")

        length = right - left + 1
        k = self.logs[length]         # Largest power of 2 fitting in length
        block_length = 1 << k         # 2^k

        # Two overlapping lookups cover the entire range in O(1)
        return min(
            self.table[k][left],
            self.table[k][right - block_length + 1]
        )

    def update(self, index, value):
        if not 0 <= index < len(self.arr):
            raise IndexError("Update index is out of bounds.")
        self.arr[index] = value
        # Rebuilding table is O(n log n)
        self._build()
```

---

# CHAPTER 5: Approach 3 — The Segment Tree (Our Recommended Solution)

### Intuition: The Tournament Bracket
A **Segment Tree** is a binary tree where:
* The original array elements sit at the bottom as **leaves**.
* Every parent node stores the **minimum** of its two children.
* The top root node stores the minimum of the entire array.

```text
                  [Index 1: min=3]  (covers 0..7)
                    /          \
         [Idx 2: min=3]       [Idx 3: min=4]
          /          \          /          \
    [Idx 4: 5]    [Idx 5: 3] [Idx 6: 7]   [Idx 7: inf]
      /   \         /   \      /   \        /   \
    [8]   [5]     [9]   [3]  [7]  [inf]  [inf]  [inf]
   idx8  idx9   idx10  idx11 idx12 idx13  idx14  idx15
```

---

### Secret 1: Flat Array Representation (No Pointers!)
We do not use complex node objects or pointers like `node.left` and `node.right`.
Instead, we store the entire tree inside **one flat 1-D array** of size `2 * size`:
* The root is at index `1`.
* For any node at index `i`:
  * Its **left child** is at index `2 * i`.
  * Its **right child** is at index `2 * i + 1`.
  * Its **parent** is at index `i // 2`.

### Secret 2: Padding to the Next Power of Two
If `n = 5`, what is the next power of 2? It is **8**.
* We set `self.size = 8`.
* Our tree array has length `2 * 8 = 16` (indexes 0 to 15).
* The 5 real elements are placed at indexes `8, 9, 10, 11, 12`.
* Unused leaf slots (`13, 14, 15`) are filled with `float('inf')` (positive infinity).
* **Why padding is brilliant:** It guarantees the tree is a complete, perfectly balanced binary tree. The math for parent and children never breaks. And because valid queries only ask for indexes within `0 <= left <= right < n`, the dummy `inf` values can never be returned as a valid minimum!

---

### Secret 3: How the Query Works (`while left <= right`)
This is the single most common question examiners ask to catch students unprepared. **Understand this step-by-step:**

When querying `[left, right]`:
1. First, shift to leaf indices: `left += self.size`, `right += self.size`.
2. As we move upward through the tree:

#### Case A: What if `left` is odd (`left % 2 == 1`)?
* In our 1-based indexing, an **odd index is a RIGHT child** of its parent.
* Its left sibling is at `left - 1`, which is **outside** our queried range!
* If we moved up to its parent (`left // 2`), the parent would include that left sibling (polluting our answer with data outside our range).
* **Therefore:** We MUST include `tree[left]` directly into our answer:
  ```python
  minimum = min(minimum, self.tree[left])
  left += 1   # step right so we start at a clean parent boundary
  ```

#### Case B: What if `right` is even (`right % 2 == 0`)?
* An **even index is a LEFT child** of its parent.
* Its right sibling is at `right + 1`, which is **outside** our range!
* **Therefore:** We MUST include `tree[right]` directly into our answer:
  ```python
  minimum = min(minimum, self.tree[right])
  right -= 1  # step left so we end at a clean parent boundary
  ```

#### Case C: Move up to the next level
```python
left //= 2
right //= 2
```
We repeat this loop until `left > right`. 
Because the tree height is `log2(size)`, the loop runs at most about `log n` times!
**Query Time: `O(log n)`.**

---

### Secret 4: How Point Updates Work
When segment `index` changes to `new_value`:
1. Go directly to its leaf position: `pos = self.size + index`.
2. Update the leaf: `self.tree[pos] = new_value`.
3. Ride the elevator straight up to the root:
   ```python
   pos //= 2
   while pos >= 1:
       self.tree[pos] = min(self.tree[2 * pos], self.tree[2 * pos + 1])
       pos //= 2
   ```
4. Only the ancestors on that single path are updated (about `log n` nodes). All other nodes remain untouched!
**Update Time: `O(log n)` (around 2.9 microseconds at `n = 30,000` — over 23,000 times faster than Sparse Table!).**

---

### Code Walkthrough (`src/03_segment_tree.py`)
```python
class SegmentTree:
    def __init__(self, arr):
        if not arr:
            raise ValueError("Array must not be empty.")

        self.arr = list(arr)
        self.n = len(self.arr)

        # 1. Find smallest power of 2 >= n (e.g. for n=5, size=8)
        self.size = 1
        while self.size < self.n:
            self.size *= 2

        # 2. Allocate flat tree array filled with infinity
        self.tree = [float("inf")] * (2 * self.size)

        # 3. Put original array elements in leaf positions (size to size + n - 1)
        for i, value in enumerate(self.arr):
            self.tree[self.size + i] = value

        # 4. Bottom-up build: parent = min(left_child, right_child)
        for i in range(self.size - 1, 0, -1):
            self.tree[i] = min(self.tree[2 * i], self.tree[2 * i + 1])

    def query(self, left, right):
        if not (0 <= left <= right < self.n):
            raise ValueError("Invalid range: require 0 <= left <= right < n.")

        # Shift to leaf indices
        left += self.size
        right += self.size
        minimum = float("inf")

        # Iteratively climb the tree
        while left <= right:
            # If left is a right child, take it and move to next block
            if left % 2 == 1:
                minimum = min(minimum, self.tree[left])
                left += 1

            # If right is a left child, take it and move to previous block
            if right % 2 == 0:
                minimum = min(minimum, self.tree[right])
                right -= 1

            # Move both pointers up to their parents
            left //= 2
            right //= 2

        return minimum

    def update(self, index, value):
        if not 0 <= index < self.n:
            raise IndexError("Update index is out of bounds.")

        self.arr[index] = value
        position = self.size + index
        self.tree[position] = value

        # Ascend path to root and recompute each parent
        position //= 2
        while position >= 1:
            self.tree[position] = min(
                self.tree[2 * position],
                self.tree[2 * position + 1]
            )
            position //= 2
```

---

# CHAPTER 6: Benchmark Results & The Final Recommendation

### Summary Table of Recorded Experiments

| Approach | Array Size (`n`) | Build Time | Query Avg | Update Avg | Peak Build Memory |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Linear Scan** | 1,000 | 0.0000009 sec | 12.16 µs | 0.11 µs | 8.0 KiB |
| **Sparse Table** | 1,000 | 0.00131 sec | 0.28 µs | 1.30 ms | 101.9 KiB |
| **Segment Tree** | 1,000 | 0.00019 sec | 1.32 µs | 1.57 µs | 24.2 KiB |
| **Linear Scan** | 30,000 | 0.000032 sec | 422.67 µs | 0.11 µs | 234.5 KiB |
| **Sparse Table** | 30,000 | 0.0623 sec | **0.34 µs** | 70.72 ms | 4,219.1 KiB |
| **Segment Tree** | 30,000 | 0.0068 sec | **3.71 µs** | **2.99 µs** | **746.7 KiB** |

*(Note: µs = microsecond = 1 millionth of a second; ms = millisecond = 1 thousandth of a second)*

### Key Takeaways to Memorize
1. **The Sparse Table has the fastest queries (0.34 µs)**, but its updates are brutally slow (70.72 ms) because it must rebuild the entire table. It also uses 5.6 times more memory (4.2 MB vs 746 KB).
2. **The Linear Scan has the fastest updates (0.11 µs)**, but its queries slow down drastically as ranges get wider (422.67 µs).
3. **The Segment Tree is the clear winner for our Road Quality Monitor**:
   - Query time: 3.71 µs (very fast!).
   - Update time: 2.99 µs (over **23,600 times faster** than Sparse Table!).
   - Memory: `O(n)` (746 KB vs 4.2 MB).

---

# CHAPTER 7: The Top 25 Viva Voce Questions & Model Answers

Read these carefully. If you know these answers, you are guaranteed top marks.

#### Q1: What was the goal of your mini-project?
> *"We investigated the Range Minimum Query with Point Updates problem in the context of a road quality monitor. We implemented, tested, and benchmarked three approaches: Linear Scan, Sparse Table, and Segment Tree, to recommend the optimal data structure when both range queries and point updates occur."*

#### Q2: What is an idempotent operation, and why is it important here?
> *"An operation is idempotent if `op(x, x) = x`. Taking the minimum is idempotent because `min(x, x) = x`. This allows the Sparse Table to answer queries in `O(1)` using two overlapping intervals without double-counting errors."*

#### Q3: Can you use a Sparse Table for Range Sum Queries in `O(1)`?
> *"No, because addition is NOT idempotent (`x + x = 2x != x`). Overlapping intervals would double-count elements in the overlapping section. Range Sum in a Sparse Table requires combining disjoint power-of-two blocks in `O(log n)`."*

#### Q4: Why does Sparse Table take `O(n log n)` space?
> *"Because it stores `log2(n) + 1` levels, and each level has `n` entries. For `n = 30,000`, `log2(n)` is about 15, so it stores approximately `15 * 30,000 = 450,000` values."*

#### Q5: Why did you pad the Segment Tree size to the next power of two?
> *"Padding makes the tree a complete binary tree. This guarantees that every node has a clear parent and child relationship on a flat array without boundary edge cases, and completely eliminates dynamic pointers or recursion."*

#### Q6: Why did you choose an iterative Segment Tree instead of recursive?
> *"An iterative segment tree works bottom-up using a simple loop. It avoids Python function call overhead and call stack frames, preventing `RecursionError` on large arrays and running significantly faster in wall-clock time."*

#### Q7: In the Segment Tree query, why do you check `if left % 2 == 1`?
> *"Because in 1-based indexing, an odd index represents a right child. Its sibling (the left child) is outside our query range. Therefore, we cannot jump up to its parent; we must include `tree[left]` into our answer and increment `left` to move to the next valid block."*

#### Q8: In the Segment Tree query, why do you check `if right % 2 == 0`?
> *"Because an even index represents a left child. Its sibling (the right child) is outside our query range. We cannot jump to its parent; we must include `tree[right]` into our answer and decrement `right`."*

#### Q9: What happens if an empty array `[]` is passed to your constructors?
> *"All three implementations check for empty input and raise a `ValueError("Array must not be empty.")`, matching our specification."*

#### Q10: What happens if someone queries `left > right` or out-of-bounds?
> *"The code checks `0 <= left <= right < len(arr)`. If violated, it raises a `ValueError`. Out-of-bounds updates raise an `IndexError`."*

#### Q11: Does modifying the input list outside alter your data structure?
> *"No. All three constructors call `list(arr)` or `arr.copy()`, creating an independent copy. External mutations to the caller's array do not affect our data structure."*

#### Q12: Why is Linear Scan still useful?
> *"Because it is simple, has zero build overhead, and is trivial to verify. In our project, we used the Linear Scan as our **correctness oracle** to verify the answers of the Sparse Table and Segment Tree during automated testing."*

#### Q13: In what scenario would you recommend a Sparse Table over a Segment Tree?
> *"When the dataset is strictly static (no updates ever occur) and read queries happen millions of times. In that case, the Sparse Table's `O(1)` query speed (0.34 µs) outperforms the Segment Tree (3.71 µs)."*

#### Q14: In what scenario does the Segment Tree perform worse than Linear Scan?
> *"On extremely small arrays (like `n < 50`) or very tight queries (length 1 to 5). Linear scan iterates contiguous memory in the CPU cache with zero branch overhead, whereas the tree has index jumps."*

#### Q15: What is the height of a Segment Tree with `n` elements?
> *"`log2(n) + 1`. For `n = 30,000`, the height is 16 levels."*

#### Q16: How many nodes does an array-based Segment Tree of size `n` have?
> *"If size is padded to the next power of two `S`, the array length is `2 * S`. For `n = 30,000`, `S = 32,768`, so the tree has `65,536` nodes."*

#### Q17: What are the sentinels used in the Segment Tree?
> *"Unused leaves in the padded tree are initialized to `float('inf')` (positive infinity). Because `min(x, +inf) = x`, dummy leaves never interfere with real minimums."*

#### Q18: What is the time complexity of building a Segment Tree?
> *"`O(n)`. Although the tree has `log n` levels, the work is done bottom-up in a single pass of `S - 1` steps, which is linear in `n`."*

#### Q19: Why does point update in a Segment Tree take `O(log n)`?
> *"Because updating one leaf only affects the direct ancestors on the path from that leaf to the root. The length of this path is the height of the tree, which is `log2(size)`."*

#### Q20: What is Lazy Propagation, and did you need it?
> *"Lazy Propagation is a technique for updating an entire **range** `[L, R]` in `O(log n)` time by deferring updates to children. We did not need it because our problem statement specifically specifies **point updates** (updating one single index at a time)."*

#### Q21: How did you ensure benchmark reproducibility?
> *"We used fixed pseudo-random seeds (`20261109 + size` and `8300 + size`), took the median of 5 separate runs, and performed 3 passes per query batch to eliminate timer noise."*

#### Q22: How was memory measured in the benchmark?
> *"We used Python's built-in `tracemalloc` library to measure peak allocated heap memory during construction, excluding interpreter overhead and the input array."*

#### Q23: What are the exact update times at `n = 30,000`?
> *"Segment tree: about 2.99 µs. Sparse table: about 70.72 ms (70,728 microseconds). The Segment tree is over 23,600 times faster on updates."*

#### Q24: What are the exact query times at `n = 30,000`?
> *"Sparse Table: 0.345 µs. Segment Tree: 3.711 µs. Linear Scan: 422.677 µs."*

#### Q25: What is your final conclusion and recommendation?
> *"For the road-quality monitoring case study, scores change due to frequent inspections and maintenance. Therefore, the **Segment Tree is the strongly recommended primary approach** because it delivers balanced `O(log n)` queries and updates while using `O(n)` storage."*

---

### You are now ready. Review this guide once or twice, and you will ace your viva!
