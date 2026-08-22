#!/usr/bin/env python3
"""
Experiment Harness for Cache Simulator (CSF Assignment 3)

Runs an iso-capacity experiment matrix across cache capacities, block sizes,
associativities, write policies, and eviction policies on memory trace files.
Results are parsed, derived metrics computed, and deterministically written to CSV.
"""

import argparse
import concurrent.futures
import csv
import os
import shutil
import subprocess
import sys
import time
from typing import Dict, List, NamedTuple, Optional


class SimConfig(NamedTuple):
    trace: str
    sets: int
    ways: int
    block_bytes: int
    capacity_bytes: int
    write_alloc: str
    write_policy: str
    eviction: str


class SimResult(NamedTuple):
    config: SimConfig
    total_loads: int
    total_stores: int
    load_hits: int
    load_misses: int
    store_hits: int
    store_misses: int
    total_accesses: int
    load_miss_rate: float
    store_miss_rate: float
    overall_miss_rate: float
    total_cycles: int
    cycles_per_access: float


CAPACITIES = [4096, 16384, 65536, 262144]  # 4 KB, 16 KB, 64 KB, 256 KB
BLOCK_SIZES = [16, 32, 64, 128]
ASSOCIATIVITIES = [1, 2, 4, 8, 16]
POLICIES = [
    ("write-allocate", "write-back"),
    ("write-allocate", "write-through"),
    ("no-write-allocate", "write-through"),
]
EVICTIONS = ["lru", "fifo"]
DEFAULT_TRACES = ["traces/gcc.trace", "traces/swim.trace"]

CSV_HEADER = [
    "trace",
    "sets",
    "ways",
    "block_bytes",
    "capacity_bytes",
    "write_alloc",
    "write_policy",
    "eviction",
    "total_loads",
    "total_stores",
    "load_hits",
    "load_misses",
    "store_hits",
    "store_misses",
    "total_accesses",
    "load_miss_rate",
    "store_miss_rate",
    "overall_miss_rate",
    "total_cycles",
    "cycles_per_access",
]


def find_binary(search_dir: Optional[str] = None) -> str:
    """Locate the cache simulator executable (csim.exe or csim)."""
    if search_dir is None:
        search_dir = os.path.dirname(os.path.abspath(__file__))

    candidates = [
        os.path.join(search_dir, "csim.exe"),
        os.path.join(search_dir, "csim"),
        "csim.exe",
        "csim",
        "./csim.exe",
        "./csim",
    ]
    for cand in candidates:
        if os.path.isfile(cand):
            return os.path.abspath(cand)

    found = shutil.which("csim.exe") or shutil.which("csim")
    if found:
        return os.path.abspath(found)

    raise FileNotFoundError(
        f"Could not find 'csim.exe' or 'csim' binary in '{search_dir}'. "
        "Please build the project first (e.g. run 'make')."
    )


def generate_configurations(traces: List[str]) -> List[SimConfig]:
    """
    Generate all valid simulation configurations based on the iso-capacity matrix.
    Matrix: 4 capacities * 4 block sizes * 5 assocs = 80 geometry configs.
            80 * 3 policies * 2 evictions = 480 configs per trace.
            480 * len(traces) total configs.
    """
    configs: List[SimConfig] = []

    for trace in traces:
        norm_trace = trace.replace("\\", "/")
        for cap in CAPACITIES:
            for blk in BLOCK_SIZES:
                for ways in ASSOCIATIVITIES:
                    denom = ways * blk
                    if cap % denom != 0:
                        continue
                    sets = cap // denom
                    if sets < 1 or (sets & (sets - 1)) != 0:
                        continue
                    for wa, wp in POLICIES:
                        for ev in EVICTIONS:
                            configs.append(
                                SimConfig(
                                    trace=norm_trace,
                                    sets=sets,
                                    ways=ways,
                                    block_bytes=blk,
                                    capacity_bytes=cap,
                                    write_alloc=wa,
                                    write_policy=wp,
                                    eviction=ev,
                                )
                            )
    return configs


def parse_simulation_output(stdout_str: str) -> Dict[str, int]:
    """Parse simulator stdout into integer metrics."""
    stats: Dict[str, int] = {}
    for line in stdout_str.strip().splitlines():
        if ":" in line:
            parts = line.split(":", 1)
            stats[parts[0].strip()] = int(parts[1].strip())

    required = [
        "Total loads",
        "Total stores",
        "Load hits",
        "Load misses",
        "Store hits",
        "Store misses",
        "Total cycles",
    ]
    for key in required:
        if key not in stats:
            raise ValueError(
                f"Missing expected statistic '{key}' in simulator output:\n{stdout_str}"
            )
    return stats


def run_single_simulation(
    csim_bin: str, config: SimConfig, trace_bytes: bytes
) -> SimResult:
    """Run one simulation subprocess and return parsed metrics."""
    cmd = [
        csim_bin,
        str(config.sets),
        str(config.ways),
        str(config.block_bytes),
        config.write_alloc,
        config.write_policy,
        config.eviction,
    ]

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout_bytes, stderr_bytes = proc.communicate(input=trace_bytes)

    if proc.returncode != 0:
        err_msg = stderr_bytes.decode("utf-8", errors="replace").strip()
        out_msg = stdout_bytes.decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"Simulator failed with exit code {proc.returncode}.\n"
            f"Command: {' '.join(cmd)}\n"
            f"Stderr: {err_msg}\n"
            f"Stdout: {out_msg}"
        )

    stdout_str = stdout_bytes.decode("utf-8", errors="replace")
    stats = parse_simulation_output(stdout_str)

    total_loads = stats["Total loads"]
    total_stores = stats["Total stores"]
    load_hits = stats["Load hits"]
    load_misses = stats["Load misses"]
    store_hits = stats["Store hits"]
    store_misses = stats["Store misses"]
    total_cycles = stats["Total cycles"]

    total_accesses = total_loads + total_stores
    load_miss_rate = load_misses / total_loads if total_loads > 0 else 0.0
    store_miss_rate = store_misses / total_stores if total_stores > 0 else 0.0
    overall_miss_rate = (
        (load_misses + store_misses) / total_accesses if total_accesses > 0 else 0.0
    )
    cycles_per_access = (
        total_cycles / total_accesses if total_accesses > 0 else 0.0
    )

    return SimResult(
        config=config,
        total_loads=total_loads,
        total_stores=total_stores,
        load_hits=load_hits,
        load_misses=load_misses,
        store_hits=store_hits,
        store_misses=store_misses,
        total_accesses=total_accesses,
        load_miss_rate=load_miss_rate,
        store_miss_rate=store_miss_rate,
        overall_miss_rate=overall_miss_rate,
        total_cycles=total_cycles,
        cycles_per_access=cycles_per_access,
    )


def sort_key(result: SimResult):
    """Deterministic sort key for CSV output."""
    cfg = result.config
    return (
        cfg.trace,
        cfg.capacity_bytes,
        cfg.block_bytes,
        cfg.ways,
        cfg.write_alloc,
        cfg.write_policy,
        cfg.eviction,
    )


def write_results_csv(output_path: str, results: List[SimResult]) -> None:
    """Write simulation results deterministically to a CSV file."""
    sorted_results = sorted(results, key=sort_key)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        for r in sorted_results:
            cfg = r.config
            writer.writerow(
                [
                    cfg.trace,
                    cfg.sets,
                    cfg.ways,
                    cfg.block_bytes,
                    cfg.capacity_bytes,
                    cfg.write_alloc,
                    cfg.write_policy,
                    cfg.eviction,
                    r.total_loads,
                    r.total_stores,
                    r.load_hits,
                    r.load_misses,
                    r.store_hits,
                    r.store_misses,
                    r.total_accesses,
                    r.load_miss_rate,
                    r.store_miss_rate,
                    r.overall_miss_rate,
                    r.total_cycles,
                    r.cycles_per_access,
                ]
            )


def preload_traces(trace_paths: List[str]) -> Dict[str, bytes]:
    """Read all trace files into RAM once to avoid redundant disk I/O."""
    trace_data: Dict[str, bytes] = {}
    for path in trace_paths:
        norm_key = path.replace("\\", "/")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Trace file not found: {path}")
        print(f"Preloading trace '{path}' into memory...", flush=True)
        with open(path, "rb") as f:
            data = f.read()
        trace_data[norm_key] = data
        print(f"  Loaded {len(data):,} bytes for {norm_key}", flush=True)
    return trace_data


def main():
    parser = argparse.ArgumentParser(
        description="Run cache simulation experiment matrix and output results to CSV."
    )
    parser.add_argument(
        "--binary",
        type=str,
        default=None,
        help="Path to csim binary (default: auto-detect)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results.csv",
        help="Path to output CSV file (default: results.csv)",
    )
    parser.add_argument(
        "--traces",
        nargs="+",
        default=DEFAULT_TRACES,
        help=f"Trace files to evaluate (default: {' '.join(DEFAULT_TRACES)})",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of parallel worker threads (default: os.cpu_count())",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only generate and print configurations without running simulations.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of simulations to run (useful for quick testing).",
    )
    args = parser.parse_args()

    configs = generate_configurations(args.traces)
    if args.limit is not None:
        configs = configs[: args.limit]

    print(f"Generated {len(configs)} simulation configurations across {len(args.traces)} traces.")

    if args.dry_run:
        print("Dry run requested. Configurations:")
        for idx, c in enumerate(configs, 1):
            print(f"[{idx:4d}] Trace={c.trace} Cap={c.capacity_bytes}B Sets={c.sets} Ways={c.ways} Block={c.block_bytes}B WA={c.write_alloc} WP={c.write_policy} Ev={c.eviction}")
        return

    csim_bin = args.binary or find_binary()
    print(f"Using binary: {csim_bin}")

    # Preload traces into memory
    trace_data = preload_traces(args.traces)

    num_workers = args.workers or os.cpu_count() or 4
    print(f"Starting parallel execution with {num_workers} workers...", flush=True)

    start_time = time.time()
    results: List[SimResult] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_config = {
            executor.submit(
                run_single_simulation,
                csim_bin,
                cfg,
                trace_data[cfg.trace],
            ): cfg
            for cfg in configs
        }

        total_done = 0
        total_total = len(configs)
        for future in concurrent.futures.as_completed(future_to_config):
            cfg = future_to_config[future]
            try:
                res = future.result()
                results.append(res)
            except Exception as exc:
                print(f"Error running config {cfg}: {exc}", file=sys.stderr)
                raise

            total_done += 1
            if total_done % 50 == 0 or total_done == total_total:
                elapsed = time.time() - start_time
                print(
                    f"Progress: {total_done}/{total_total} ({total_done/total_total*100:.1f}%) "
                    f"in {elapsed:.2f}s ({(total_done/elapsed):.1f} runs/sec)",
                    flush=True,
                )

    total_time = time.time() - start_time
    print(f"Completed {len(results)} simulations in {total_time:.2f} seconds.")

    # Write output CSV
    write_results_csv(args.output, results)
    print(f"Successfully wrote {len(results)} rows to '{args.output}'.")


if __name__ == "__main__":
    main()
