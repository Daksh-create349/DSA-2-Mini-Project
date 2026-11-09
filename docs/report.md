# Range Minimum Query with Point Updates

## Algorithm Design, Correctness Tests, and Benchmark Report

**Case Study No. 02 — Segment Trees & Sparse Tables**  
**Prepared:** November 9, 2026  
**Purpose:** Compare three range-minimum-query approaches and recommend a suitable data structure for a workload that may include point updates.

**Prepared by:** Daksh Srivastava, Prathamesh More, Yuvraj Mishra, Biswajeet Rout, Sumit Shingole

---

## 1. Executive summary

A road-quality monitor stores one score for each road segment. It must answer questions such as “what is the lowest score from segment 120 through segment 450?” A new inspection can also change the score at one position. This is the **range minimum query (RMQ) with point updates** problem.

Three approaches were implemented and compared:

1. **Linear scan:** inspect every value in the requested range.
2. **Sparse table:** preprocess answers for power-of-two intervals; answer each query using two precomputed intervals. A point update rebuilds the table.
3. **Segment tree:** store interval minima in a tree so both queries and point updates can be handled without rebuilding everything.

All three implementations passed the included correctness tests. The benchmark used the same deterministic arrays and operations for each approach at each size. In this run, sparse-table queries were the fastest, but its rebuild-on-update cost and memory use were much higher. Linear scanning’s query time increased as ranges and arrays grew. The segment tree provided fast queries and fast updates with substantially less memory than the sparse table.

**Recommendation:** use the segment tree for a changing road-score system that requires both range queries and point updates. Use the sparse table only if the scores are effectively static and query speed is the overriding priority.

## 2. Problem definition and design contract

### Input and output

- **Input:** a non-empty, zero-indexed array of comparable numeric scores, and an operation.
- **Range query:** two integer indexes `left` and `right`, inclusive.
- **Query output:** the smallest value in `values[left:right + 1]`.
- **Point update:** an integer index and a replacement score. It changes exactly that position.
- **Update output:** no value is returned; the data structure’s stored state changes.

### Assumptions and constraints

- Indexing is zero-based, and query ranges are inclusive.
- The array must contain at least one value.
- A valid query must satisfy `0 <= left <= right < n`.
- A valid update index must satisfy `0 <= index < n`.
- Invalid ranges raise `ValueError`; invalid update indexes raise `IndexError`.
- Values can be negative, repeated, or positive. The benchmark uses integer scores.
- Each implementation copies the input list, so later changes to the caller’s list do not silently alter the structure.
- A sparse-table point update rebuilds its preprocessing table. This is intentionally simple and correct, but expensive; it is not presented as a dynamic sparse-table algorithm.

### Success criteria

1. Every valid query returns the same minimum as a direct Python `min` over the requested slice.
2. Updates change future answers and do not change unrelated positions.
3. Boundary, invalid-input, and non-power-of-two array cases behave consistently.
4. The three approaches are benchmarked on identical data and operation sequences.
5. The final recommendation follows the measured and theoretical trade-offs rather than query speed alone.

## 3. Algorithms and correctness reasoning

### 3.1 Linear scan

**Pseudocode**

```text
QUERY(left, right):
    validate 0 <= left <= right < n
    smallest = values[left]
    for i from left + 1 through right:
        if values[i] < smallest:
            smallest = values[i]
    return smallest

UPDATE(index, value):
    validate 0 <= index < n
    values[index] = value
```

**Why it is correct:** after the loop has visited through index `i`, `smallest` is the minimum of all visited values from `left` through `i`. The loop visits every element in the requested inclusive interval, so the final value is its minimum. An update directly replaces one stored element.

**Complexity:** build `O(n)` including the input copy; query `O(k)` for a range of length `k` (worst case `O(n)`); point update `O(1)`; auxiliary storage `O(n)` for the copied array.

### 3.2 Sparse table

**Pseudocode**

```text
BUILD(values):
    table[0] = values
    for each power k >= 1:
        for each start where an interval of length 2^k fits:
            table[k][start] =
                min(table[k-1][start],
                    table[k-1][start + 2^(k-1)])

QUERY(left, right):
    validate 0 <= left <= right < n
    length = right - left + 1
    k = floor(log2(length))
    block = 2^k
    return min(table[k][left],
               table[k][right - block + 1])

UPDATE(index, value):
    validate 0 <= index < n
    values[index] = value
    BUILD(values)
```

**Why it is correct:** each table entry stores the minimum of its represented interval. The query chooses two intervals of length `2^k` that together cover the requested range; they may overlap. Overlap is safe for the `min` operation because taking the minimum of a value more than once cannot change the result. Their union covers the full query, so the smaller of the two stored minima is the requested minimum. Rebuilding after an update restores the table invariant.

**Complexity:** build `O(n log n)`; query `O(1)`; point update `O(n log n)` for this implementation because it rebuilds; auxiliary storage `O(n log n)`.

### 3.3 Segment tree

**Pseudocode**

```text
BUILD(values):
    place values in the tree leaves
    fill each parent with min(left_child, right_child)

QUERY(left, right):
    validate 0 <= left <= right < n
    use the iterative tree walk to select disjoint nodes
        that exactly cover [left, right]
    return the minimum stored in those nodes

UPDATE(index, value):
    validate 0 <= index < n
    replace the corresponding leaf
    recompute each ancestor as min(left_child, right_child)
```

The implementation pads the leaf area to the next power of two with positive infinity. Padding does not affect a real query because query indexes are checked against the original array length.

**Why it is correct:** every internal node stores the minimum of its child intervals. The iterative query selects nodes whose covered intervals are disjoint and whose union is exactly the requested inclusive interval. Taking the minimum of those node values therefore gives the range minimum. For an update, only the updated leaf and its ancestors can have changed interval minima; recomputing that path restores the invariant throughout the tree.

**Complexity:** build `O(n)`; query `O(log n)`; point update `O(log n)`; auxiliary storage `O(n)`.

## 4. Correctness testing

The test suite is `tests/test_rmq.py`, using only Python’s standard `unittest` library. Run it from the project root:

```text
python3 -m unittest discover -s tests -v
```

The suite checks all three implementations against expected results. It covers:

- Hand-worked answers, full-array ranges, single-element ranges, and ranges touching either boundary.
- Updates at index `0` and the final index, including changes to and away from the current minimum.
- Length-one and non-power-of-two arrays, ascending and descending inputs, duplicate values, and negative values.
- A deterministic sequence of 100 mixed random queries and updates for each implementation, checked against a plain list.
- Invalid ranges, out-of-bounds updates, empty input, and input-list preservation.

**Validation result:** all 7 test methods passed for all three approaches (`Ran 7 tests ... OK`). The benchmark additionally checks every timed query against the direct minimum and checks the updated positions before it reports timings. Thus timing output is not produced if its workload’s correctness check fails.

## 5. Benchmark method

Run the benchmark from the project root:

```text
python3 tools/benchmark.py
```

The script uses Python’s standard library only. It reports the runtime environment, writes machine-readable `results/benchmark_results.csv`, and creates the labelled graph `results/benchmark_chart.svg`.

### Dataset and workload

| Array size (`n`) | Queries per approach | Updates per approach |
|---:|---:|---:|
| 1,000 | 300 | 20 |
| 10,000 | 300 | 20 |
| 30,000 | 200 | 10 |

Values are generated deterministically as integers in `[-100,000, 100,000]`. A fixed seed makes each size reproducible. For each array size, every approach receives the same query ranges and point updates. Query ranges deliberately include a mix of short ranges (about 1–5% of the array), medium ranges (about 25–50%), and broad ranges (about 50–100%). This avoids measuring only tiny intervals, which would understate the linear scan’s work. Update positions and replacement values are identical across approaches.

Build time is the median of five measurements. Average query time is measured over three passes through the same query set; the reported value is the median per-query time from five runs. Average update time is similarly measured and reported as the median per-update time from five runs. Structure construction is outside the query and update timers. Peak build allocation is measured separately with `tracemalloc`; it is approximate Python-traced memory for the structure build and excludes the already-existing input array and interpreter baseline.

**Environment for the recorded run:** Python 3.9.6, macOS 27.0.1, Apple Silicon arm64. Timings are wall-clock measurements and can vary with hardware, background load, and Python version. They are evidence for this workload, not universal constants.

## 6. Measured results

The following are the actual results from the included benchmark run. Times are seconds; “peak build” is approximate KiB of traced Python allocations.

| Approach | n | Queries | Updates | Build (s) | Avg query (s) | Avg update (s) | Peak build (KiB) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Linear Scan | 1,000 | 300 | 20 | 0.000000916 | 0.000012163 | 0.000000112 | 8.0 |
| Sparse Table | 1,000 | 300 | 20 | 0.00131271 | 0.000000283 | 0.00130543 | 101.9 |
| Segment Tree | 1,000 | 300 | 20 | 0.000197625 | 0.000001329 | 0.000001571 | 24.2 |
| Linear Scan | 10,000 | 300 | 20 | 0.000013416 | 0.000128625 | 0.000000115 | 78.3 |
| Sparse Table | 10,000 | 300 | 20 | 0.0185985 | 0.000000312 | 0.0196605 | 1,328.5 |
| Segment Tree | 10,000 | 300 | 20 | 0.00356742 | 0.000001943 | 0.000002415 | 334.5 |
| Linear Scan | 30,000 | 200 | 10 | 0.000032625 | 0.000422677 | 0.000000117 | 234.5 |
| Sparse Table | 30,000 | 200 | 10 | 0.0623089 | 0.000000345 | 0.0707280 | 4,219.1 |
| Segment Tree | 30,000 | 200 | 10 | 0.00681229 | 0.000003711 | 0.000002996 | 746.7 |

![Color-coded RMQ query and point-update benchmark chart. Both panels use a logarithmic time axis.](../results/benchmark_chart.png)

The complete unrounded machine-readable results are in [benchmark_results.csv](../results/benchmark_results.csv). Regenerate the data and graphs with [benchmark.py](../tools/benchmark.py).

## 7. Interpretation, comparison, and recommendation

### Query performance

The sparse table had the smallest measured query time at every size: about 0.0000003 seconds per query in this run. This follows its `O(1)` query complexity. Its query time barely changes as `n` grows because it needs only two precomputed table lookups and one minimum operation.

The segment tree’s query time increased from about 0.0000013 seconds at `n = 1,000` to about 0.0000037 seconds at `n = 30,000`, consistent with `O(log n)`. It is still very fast for this workload.

The linear scan was initially simple and inexpensive to build, but its average query time rose from about 0.000012 seconds to about 0.000423 seconds as array size and query spans grew. This is the expected cost of checking each value in the requested interval. A shorter-range-only workload would make it look better; a workload dominated by full-array queries would make it worse.

### Update performance

The linear scan updates one array element directly, so its update time is effectively constant and very small. The sparse table update took about 0.0013 seconds at `n = 1,000` and about 0.0707 seconds at `n = 30,000`, because this implementation rebuilds the full table after each change. The segment tree updates remained around 0.0000016–0.0000030 seconds because it recalculates only one path from a leaf to the root.

### Memory and total workload trade-off

The sparse table’s query advantage comes with a clear memory and update cost. At `n = 30,000`, its measured traced build allocation was about 4,219 KiB, compared with about 747 KiB for the segment tree. These are Python allocation measurements, not exact resident-memory totals, but they show the expected difference: `O(n log n)` storage versus `O(n)`.

Consequently, a “fastest query” claim is not by itself enough to choose a structure. A static dataset queried many times may justify the sparse table. A changing dataset that needs both operations benefits from the segment tree. A tiny dataset, or one with very few queries and a priority on simplicity, may be adequately served by a linear scan.

### Correctness, edge cases, and implementation effort

All three implementations use the same zero-based inclusive range contract and reject invalid query ranges. They also reject an empty initial array and out-of-range update indexes. The segment tree’s padding covers non-power-of-two lengths without exposing padded positions to valid queries. The sparse table’s overlapping query blocks are safe specifically because `min` is idempotent. The tests exercise these behaviors and compare randomized operations to a direct-list reference.

Implementation effort follows the structures’ complexity: the linear scan is the simplest to implement and inspect; the sparse table needs logarithm and interval preprocessing, and its update path is deliberately a full rebuild; the segment tree needs careful parent/child indexing and boundary handling, but then supports both operations without global rebuilding. This is a practical cost alongside runtime and memory: the simple scan is valuable as a correctness oracle even when it is not the fastest production choice.

### Recommendation for the road-quality monitor

The scenario includes inspection updates as well as range queries. The **segment tree is the recommended primary structure** because both operations remain efficient as the array grows, and it avoids the sparse table’s expensive full rebuild and higher memory use. Keep the linear scan as a simple correctness reference. Choose the sparse table only for a separately defined static-data workload where updates are absent or exceptionally rare.

## 8. Limitations and conclusion

This benchmark is controlled and reproducible, but it does not represent every real deployment. It tests three array sizes, integer scores, one deterministic random dataset per size, and a defined mix of interval lengths. Other hardware, Python implementations, score types, query distributions, or update/query ratios can change the measured constants. Python timer overhead is also relevant to very small operations; the script reduces that effect by batching queries and using medians, but these results should not be read as precise production latency guarantees. Traced Python allocation is an approximation and not a substitute for operating-system resident-memory profiling.

The theoretical behavior and the measured evidence point to the same workload-dependent conclusion: linear scan prioritizes simplicity, sparse table prioritizes static-query speed, and segment tree balances dynamic queries and updates. For range minimum with point updates, the segment tree is the best-supported recommendation.

## Submission files

- [01_linear_scan.py](../src/01_linear_scan.py) — linear-scan implementation.
- [02_sparse_table.py](../src/02_sparse_table.py) — sparse-table implementation with rebuild-on-update.
- [03_segment_tree.py](../src/03_segment_tree.py) — segment-tree implementation.
- [test_rmq.py](../tests/test_rmq.py) — correctness and edge-case tests.
- [benchmark.py](../tools/benchmark.py) — reproducible benchmark and correctness checks.
- [benchmark_results.csv](../results/benchmark_results.csv) — raw benchmark output.
- [benchmark_chart.svg](../results/benchmark_chart.svg) — labelled query/update comparison graph.
- [presentation.md](../presentation/slides_outline.md) — four-slide presentation summary.
- [presentation.html](../presentation/index.html) — printable, browser-based four-slide deck.
- [README.md](../README.md) — run instructions.
