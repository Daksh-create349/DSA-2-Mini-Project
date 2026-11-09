"""Reproducible timing and memory comparison for the three RMQ approaches."""

import csv
import importlib.util
import math
import platform
import random
import statistics
import sys
import time
import tracemalloc
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
RESULTS = ROOT / "results"
REPEATS = 5
QUERY_PASSES = 3
CONFIGS = (
    (1_000, 300, 20),
    (10_000, 300, 20),
    (30_000, 200, 10),
)


def load_class(name, filename, class_name):
    spec = importlib.util.spec_from_file_location(name, SOURCE / filename)
    if spec is None or spec.loader is None:
        raise ImportError("Could not load {}".format(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


APPROACHES = (
    ("Linear Scan", load_class("linear_scan", "01_linear_scan.py", "LinearScan")),
    ("Sparse Table", load_class("sparse_table", "02_sparse_table.py", "SparseTable")),
    ("Segment Tree", load_class("segment_tree", "03_segment_tree.py", "SegmentTree")),
)


def make_array(size):
    rng = random.Random(20261109 + size)
    return [rng.randint(-100_000, 100_000) for _ in range(size)]


def make_workload(size, query_count, update_count):
    rng = random.Random(8300 + size)
    queries = []
    for i in range(query_count):
        if i % 3 == 0:
            length = rng.randint(1, max(1, size // 20))
        elif i % 3 == 1:
            length = rng.randint(max(1, size // 4), max(1, size // 2))
        else:
            length = rng.randint(max(1, size // 2), size)
        left = rng.randint(0, size - length)
        queries.append((left, left + length - 1))

    updates = [
        (rng.randrange(size), rng.randint(-100_000, 100_000))
        for _ in range(update_count)
    ]
    return queries, updates


def median_build_seconds(cls, values):
    samples = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        cls(values)
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def peak_build_bytes(cls, values):
    tracemalloc.start()
    obj = cls(values)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del obj
    return peak


def median_query_seconds(cls, values, queries):
    samples = []
    for _ in range(REPEATS):
        obj = cls(values)
        start = time.perf_counter()
        for _ in range(QUERY_PASSES):
            for left, right in queries:
                obj.query(left, right)
        elapsed = time.perf_counter() - start
        samples.append(elapsed / (QUERY_PASSES * len(queries)))
    return statistics.median(samples)


def median_update_seconds(cls, values, updates):
    samples = []
    for _ in range(REPEATS):
        obj = cls(values)
        start = time.perf_counter()
        for index, value in updates:
            obj.update(index, value)
        elapsed = time.perf_counter() - start
        samples.append(elapsed / len(updates))
    return statistics.median(samples)


def verify_workload(cls, values, queries, updates):
    obj = cls(values)
    for left, right in queries:
        expected = min(values[left:right + 1])
        actual = obj.query(left, right)
        if actual != expected:
            raise AssertionError(
                "{} failed query [{}, {}]: expected {}, got {}".format(
                    cls.__name__, left, right, expected, actual
                )
            )
    expected_values = list(values)
    for index, value in updates:
        obj.update(index, value)
        expected_values[index] = value
        left = min(index, len(values) - 1)
        if obj.query(left, left) != expected_values[left]:
            raise AssertionError("{} failed after a point update".format(cls.__name__))


def collect_results():
    results = []
    for size, query_count, update_count in CONFIGS:
        values = make_array(size)
        queries, updates = make_workload(size, query_count, update_count)
        for name, cls in APPROACHES:
            verify_workload(cls, values, queries, updates)
            results.append({
                "approach": name,
                "n": size,
                "queries": query_count,
                "updates": update_count,
                "build_seconds": median_build_seconds(cls, values),
                "query_avg_seconds": median_query_seconds(cls, values, queries),
                "update_avg_seconds": median_update_seconds(cls, values, updates),
                "peak_build_bytes": peak_build_bytes(cls, values),
            })
    return results


def write_csv(results):
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = RESULTS / "benchmark_results.csv"
    fields = (
        "approach", "n", "queries", "updates", "build_seconds",
        "query_avg_seconds", "update_avg_seconds", "peak_build_bytes",
    )
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    return path


def chart_panel(results, metric, title, y_label, top):
    left, right = 95, 925
    width = right - left
    height = 180
    bottom = top + height
    values = [row[metric] for row in results]
    log_min = min(values)
    log_max = max(values)
    low = math.floor(time_log10(log_min)) - 1
    high = max(low + 1, math.ceil(time_log10(log_max)))

    pieces = [
        '<text x="510" y="{}" text-anchor="middle" class="title">{}</text>'.format(top - 20, title),
        '<line x1="{}" y1="{}" x2="{}" y2="{}" class="axis"/>'.format(left, top, left, bottom),
        '<line x1="{}" y1="{}" x2="{}" y2="{}" class="axis"/>'.format(left, bottom, right, bottom),
    ]

    for exponent in range(low, high + 1):
        y = bottom - (exponent - low) / float(high - low) * height
        pieces.append('<line x1="{}" y1="{:.1f}" x2="{}" y2="{:.1f}" class="grid"/>'.format(left, y, right, y))
        pieces.append('<text x="{}" y="{:.1f}" text-anchor="end" class="tick">10^{} s</text>'.format(left - 10, y + 4, exponent))

    sizes = [row["n"] for row in results if row["approach"] == APPROACHES[0][0]]
    min_size = min(sizes)
    max_size = max(sizes)
    x_positions = {
        size: left + ((size - min_size) / float(max(1, max_size - min_size))) * width
        for size in sizes
    }
    for size in sizes:
        x = x_positions[size]
        pieces.append('<text x="{:.1f}" y="{}" text-anchor="middle" class="tick">{:,}</text>'.format(x, bottom + 20, size))

    styles = (
        ("#2563EB", ""),
        ("#EA580C", "8 4"),
        ("#15803D", "2 4"),
    )
    for (name, _), (color, dash) in zip(APPROACHES, styles):
        points = []
        for row in results:
            if row["approach"] != name:
                continue
            x = x_positions[row["n"]]
            y = bottom - (time_log10(row[metric]) - low) / float(high - low) * height
            points.append((x, y))
        point_string = " ".join("{:.1f},{:.1f}".format(x, y) for x, y in points)
        pieces.append('<polyline points="{}" fill="none" stroke="{}" stroke-width="3" stroke-dasharray="{}"/>'.format(point_string, color, dash))
        for x, y in points:
            pieces.append('<circle cx="{:.1f}" cy="{:.1f}" r="4" fill="{}"/>'.format(x, y, color))
    pieces.append('<text x="510" y="{}" text-anchor="middle" class="label">{}</text>'.format(bottom + 42, "Array size n"))
    pieces.append('<text transform="translate(22,{}) rotate(-90)" text-anchor="middle" class="label">{}</text>'.format(top + height / 2, y_label))
    return "\n".join(pieces)


def time_log10(value):
    return math.log10(value)


def write_chart(results):
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1020" height="650" viewBox="0 0 1020 650">
<style>
text { font-family: Arial, sans-serif; fill: #172033; }
.heading { font-size: 22px; font-weight: bold; }
.title { font-size: 16px; font-weight: bold; }
.label { font-size: 13px; }
.tick { font-size: 11px; }
.axis { stroke: #334155; stroke-width: 1.4; }
.grid { stroke: #dbe2ea; stroke-width: 1; }
</style>
<rect width="100%" height="100%" fill="white"/>
"""
    svg += chart_panel(results, "query_avg_seconds", "Median average time per range query", "Seconds per query (log scale)", 105)
    svg += chart_panel(results, "update_avg_seconds", "Median average time per point update", "Seconds per update (log scale)", 385)

    legend_y = 625
    for i, ((name, _), (color, dash)) in enumerate(zip(APPROACHES, (("#2563EB", ""), ("#EA580C", "8 4"), ("#15803D", "2 4")))):
        x = 340 + i * 145
        svg += '<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}" stroke-width="3" stroke-dasharray="{}"/>'.format(x, legend_y - 4, x + 24, legend_y - 4, color, dash)
        svg += '<text x="{}" y="{}" class="label">{}</text>'.format(x + 30, legend_y, name)
    svg += "</svg>\n"
    RESULTS.mkdir(parents=True, exist_ok=True)
    path = RESULTS / "benchmark_chart.svg"
    path.write_text(svg, encoding="utf-8")
    return path


def print_results(results):
    print("Range Minimum Query Benchmark")
    print("Python: {} | Platform: {}".format(sys.version.split()[0], platform.platform()))
    print("Median of {} timing runs; query average includes {} passes per run.".format(REPEATS, QUERY_PASSES))
    print("=" * 126)
    print("{:<15} {:>8} {:>8} {:>8} {:>13} {:>15} {:>15} {:>15}".format(
        "Approach", "N", "Queries", "Updates", "Build (s)", "Query avg (s)", "Update avg (s)", "Peak build (KiB)"
    ))
    print("-" * 126)
    for row in results:
        print("{:<15} {:>8,} {:>8} {:>8} {:>13.6g} {:>15.6g} {:>15.6g} {:>15.1f}".format(
            row["approach"], row["n"], row["queries"], row["updates"],
            row["build_seconds"], row["query_avg_seconds"], row["update_avg_seconds"],
            row["peak_build_bytes"] / 1024.0,
        ))
    print("\nCSV: results/benchmark_results.csv")
    print("Graph: results/benchmark_chart.svg")
    print("Correctness check: passed for all measured queries and updates.")


if __name__ == "__main__":
    benchmark_results = collect_results()
    write_csv(benchmark_results)
    write_chart(benchmark_results)
    print_results(benchmark_results)
