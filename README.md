# Comprehensive Cache Simulator Performance Analysis

## Executive Summary

An empirical evaluation of the `csim` cache simulator (Computer Systems Fundamentals, Assignment 3) over **960 deterministic configurations**, recorded in [`results.csv`](file:///c:/JHU/CSF/csf_assign03/results.csv). Two workloads with contrasting profiles:

- **`gcc.trace`** — irregular compiler workload; 516,566 accesses, 38.41% stores.
- **`swim.trace`** — regular scientific grid sweep; 303,135 accesses, 13.97% stores.

Five dimensions are varied: set associativity (1–16 way), block size (16–128 B), eviction policy (LRU / FIFO), write and allocation policy, and total capacity (4 KB – 256 KB).

### Headline Finding

Cache configurations can be compared two ways, and each answers a different question:

- **Capacity-scaling comparison** — vary capacity together with organization. Answers *"how much faster is a bigger, better cache?"*
- **Iso-capacity comparison** — hold $\text{Sets} \times \text{Ways} \times \text{BlockBytes}$ constant and vary one organizational parameter. Answers *"what is associativity alone worth?"*

Both are reported throughout.

| Comparison (`gcc.trace`, 16 B blocks, WA/WB/LRU) | Cycle reduction | What varied | Dominant mechanism |
| :--- | :---: | :--- | :--- |
| 4 KB 1-way $\to$ 64 KB 4-way | **-62.48%** | Capacity **and** ways ($16\times$ more storage) | Capacity expansion (dominant), plus associativity |
| 4 KB iso-capacity, 1-way $\to$ 4-way | **-43.80%** | Ways only | Conflict-miss elimination |
| 16 KB iso-capacity, 1-way $\to$ 4-way | -16.02% | Ways only | Conflict-miss elimination |
| 64 KB iso-capacity, 1-way $\to$ 4-way | -5.78% | Ways only | Conflicts largely exhausted; dirty set still overflows |
| 256 KB iso-capacity, 1-way $\to$ 4-way | -7.39% | Ways only | Dirty-line retention (writeback avoidance) |

Row 1 scales storage $16\times$ and produces the study's largest speedup — **a 62.48% cycle reduction**, from 20,312,483 to 7,620,883 cycles. Rows 2–5 hold storage fixed and isolate associativity, which proves not to be a constant — worth **43.80%** at 4 KB (with load misses down 68.5%) but only **5.78%** at 64 KB, where capacity alone has already absorbed most of the working set.

At 256 KB the gain rises again through a different mechanism: associativity stops removing misses (only 493 fewer across the entire 1-way $\to$ 16-way range) and instead retains dirty lines, collapsing writebacks from 852 to 51.

Any single-number claim about associativity therefore needs both the capacity and the mechanism attached. Sections 1–2 supply them.

---

## 1. Two Comparison Methodologies

### 1.1 Capacity-Scaling Comparison
Growing a cache along its natural upgrade path changes storage and organization together:
- **4 KB direct-mapped** (`256` sets $\times$ `1` way $\times$ `16` bytes): **20,312,483 cycles**
- **16 KB 4-way** (`256` $\times$ `4` $\times$ `16`): **9,344,483 cycles**
- **64 KB 4-way** (`1024` $\times$ `4` $\times$ `16`): **7,620,883 cycles**

The resulting $\sim 54\%$ and $\sim 62\%$ reductions are reproducible and answer a practical procurement question. They do not separate storage from organization: at $16\times$ the capacity, storage carries most of the effect.

### 1.2 Iso-Capacity Comparison
To attribute a change to a single parameter, total data capacity is held invariant:

$$\text{Capacity} = \text{Sets} \times \text{Ways} \times \text{BlockBytes} = \text{Constant}$$

Doubling associativity ($W \to 2W$) therefore requires halving the set count ($S \to S/2$). Every organizational result in Sections 2–5 uses this control.

### 1.3 Side by Side

Both methodologies on `gcc.trace` (16-byte blocks, Write-Allocate, Write-Back, LRU):

| Comparison Type | Configuration (Sets $\times$ Ways $\times$ Block) | Total Capacity | Load Misses | Store Misses | Total Misses | Miss Rate | Total Cycles | Cycles / Access |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Capacity-Scaling 1** | $256 \times 1 \times 16$ (Direct-Mapped) | **4 KB** | 19,334 | 12,284 | 31,618 | 6.13% | 20,312,483 | 39.39 |
| **Capacity-Scaling 2** | $256 \times 4 \times 16$ (4-Way SA) | **16 KB ($4\times$)** | 3,399 | 9,236 | 12,635 | 2.45% | 9,344,483 | 18.12 |
| **Capacity-Scaling 3** | $1024 \times 4 \times 16$ (4-Way SA) | **64 KB ($16\times$)**| 2,692 | 8,925 | 11,617 | 2.25% | 7,620,883 | 14.78 |
| | | | | | | | | |
| **Iso-Capacity 4 KB** | $256 \times 1 \times 16$ (1-way) | **4 KB** | 19,334 | 12,284 | 31,618 | 6.13% | 20,312,483 | 39.39 |
| **Iso-Capacity 4 KB** | $64 \times 4 \times 16$ (4-way) | **4 KB** | 6,098 | 9,960 | 16,058 | 3.11% | 11,414,883 | 22.14 |
| | | | | | | | | |
| **Iso-Capacity 16 KB**| $1024 \times 1 \times 16$ (1-way) | **16 KB** | 5,959 | 9,984 | 15,943 | 3.09% | 11,127,283 | 21.54 |
| **Iso-Capacity 16 KB**| $256 \times 4 \times 16$ (4-way) | **16 KB** | 3,399 | 9,236 | 12,635 | 2.45% | 9,344,483 | 18.12 |
| | | | | | | | | |
| **Iso-Capacity 64 KB**| $4096 \times 1 \times 16$ (1-way) | **64 KB** | 3,550 | 9,060 | 12,610 | 2.45% | 8,088,083 | 15.68 |
| **Iso-Capacity 64 KB**| $1024 \times 4 \times 16$ (4-way) | **64 KB** | 2,692 | 8,925 | 11,617 | 2.25% | 7,620,883 | 14.78 |

**Takeaway:** The two methodologies measure different things, and the gap is large. Capacity-scaling reports 62.48%. Iso-capacity attributes **43.80%** to associativity at 4 KB (20.31M $\to$ 11.41M cycles; load misses 19,334 $\to$ 6,098), **16.02%** at 16 KB, and **5.78%** at 64 KB (8.09M $\to$ 7.62M, saving 467,200 cycles).

The associativity effect is real at every capacity but shrinks as capacity alone absorbs the working set. A 5.78% reduction at zero storage cost is still architecturally significant — real designs ship for less — yet it is an order of magnitude below what the same change buys at 4 KB.

---

## 2. Set Associativity & Conflict Miss Reduction (Iso-Capacity)

### 2.1 Experimental Results across Associativities

Holding total data capacity constant at **64 KB** and block size at **16 bytes** (with Write-Allocate, Write-Back, LRU), we evaluated associativity from 1-way up to 16-way:

#### `gcc.trace` (64 KB Capacity, 16B Block, WA/WB/LRU)
| Sets | Ways | Capacity | Load Misses | Store Misses | Total Misses | Miss Rate | Total Cycles | Cycle $\Delta$ vs 1-way | Cycles / Access |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 4096 | 1 | 64 KB | 3,550 | 9,060 | 12,610 | 2.45% | 8,088,083 | Baseline | 15.68 |
| 2048 | 2 | 64 KB | 2,763 | 8,948 | 11,711 | 2.27% | 7,662,083 | -5.27% (-426,000) | 14.86 |
| 1024 | 4 | 64 KB | 2,692 | 8,925 | 11,617 | 2.25% | 7,620,883 | -5.78% (-467,200) | 14.78 |
| 512  | 8 | 64 KB | 2,660 | 8,923 | 11,583 | 2.25% | 7,609,683 | -5.91% (-478,400) | 14.76 |
| 256  | 16| 64 KB | 2,649 | 8,921 | 11,570 | 2.24% | 7,621,683 | -5.77% (-466,400) | 14.78 |

#### `swim.trace` (64 KB Capacity, 16B Block, WA/WB/LRU)
| Sets | Ways | Capacity | Load Misses | Store Misses | Total Misses | Miss Rate | Total Cycles | Cycle $\Delta$ vs 1-way | Cycles / Access |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 4096 | 1 | 64 KB | 1,200 | 10,586 | 11,786 | 3.89% | 7,847,593 | Baseline | 25.88 |
| 2048 | 2 | 64 KB | 1,052 | 10,515 | 11,567 | 3.82% | 7,745,193 | -1.30% (-102,400) | 25.55 |
| 1024 | 4 | 64 KB | 1,025 | 10,506 | 11,531 | 3.80% | 7,744,393 | -1.32% (-103,200) | 25.54 |
| 512  | 8 | 64 KB | 1,018 | 10,507 | 11,525 | 3.80% | 7,753,193 | -1.20% (-94,400)  | 25.57 |
| 256  | 16| 64 KB | 1,017 | 10,508 | 11,525 | 3.80% | 7,761,593 | -1.10% (-86,000)  | 25.60 |

### 2.2 Full Associativity Matrix Across Capacities
The effect of associativity varies depending on how constrained the cache capacity is:

```
gcc.trace Cycle Reduction vs. 1-way Baseline:
Capacity | 2-way SA      | 4-way SA      | 8-way SA      | 16-way SA
---------+---------------+---------------+---------------+---------------
  4 KB   | -33.91% (-6.9M)| -43.80% (-8.9M)| -45.51% (-9.2M)| -46.29% (-9.4M)
 16 KB   | -13.83% (-1.5M)| -16.02% (-1.8M)| -16.62% (-1.8M)| -16.72% (-1.9M)
 64 KB   |  -5.27% (-426K)|  -5.78% (-467K)|  -5.91% (-478K)|  -5.77% (-466K)
256 KB   |  -5.89% (-326K)|  -7.39% (-409K)|  -8.79% (-487K)|  -9.34% (-518K)
```

```
swim.trace Cycle Reduction vs. 1-way Baseline:
Capacity | 2-way SA      | 4-way SA      | 8-way SA      | 16-way SA
---------+---------------+---------------+---------------+---------------
  4 KB   | -15.60% (-2.2M)| -18.41% (-2.6M)| -20.05% (-2.9M)| -21.14% (-3.0M)
 16 KB   | -10.54% (-1.1M)| -11.42% (-1.2M)| -11.60% (-1.2M)| -11.75% (-1.2M)
 64 KB   |  -1.30% (-102K)|  -1.32% (-103K)|  -1.20% (-94K) |  -1.10% (-86K)
256 KB   |  -6.86% (-372K)|  -9.85% (-534K)| -10.20% (-554K)| -10.22% (-555K)
```

### 2.3 Analysis
1. **Most of the gain arrives by 2-way / 4-way.** Direct-mapped caches lose heavily to conflict misses when active lines share a set index. 2-way removes the bulk of them (4 KB `gcc`: -33.91% cycles, misses 31.6K $\to$ 19.5K); 4-way captures the remaining non-uniform collisions.
2. **Little remains beyond 4-way.** At 64 KB on `gcc`, 4-way $\to$ 8-way is worth 0.15%, and 16-way is marginally *worse* as dirty-line replacement order shifts.
3. **Hardware cost rises with ways.** Wider comparator trees and multiplexers add area, power, and hit latency, making **2-way or 4-way the practical optimum**.
4. **The benefit is capacity-dependent and non-monotonic.** On `gcc` the 1-way $\to$ 4-way reduction runs 43.80% (4 KB), 16.02% (16 KB), 5.78% (64 KB), then back up to **7.39%** (256 KB); `swim` troughs at 1.32% (64 KB) before reaching 9.85% (256 KB). Section 2.4 explains why.

---

### 2.4 Miss vs. Writeback Decomposition

Under Write-Allocate / Write-Back with 16-byte blocks, the cycle model decomposes exactly:

$$\text{Cycles} = \text{Accesses} + 400 \times \text{Misses} + 400 \times \text{DirtyEvictions}$$

Dirty-eviction counts are derived from this identity ($\text{DirtyEvictions} = (\text{Cycles} - \text{Accesses} - 400 \times \text{Misses}) / 400$) and reconcile to `results.csv` with zero residual. Splitting the full 1-way $\to$ 16-way saving by source:

#### `gcc.trace` (16 B block, WA/WB/LRU)
| Capacity | Misses 1-way $\to$ 16-way | Dirty Evictions 1-way $\to$ 16-way | Saving from Misses | Saving from Writebacks | Writeback Share |
| :---: | :---: | :---: | ---: | ---: | :---: |
| 4 KB   | 31,618 $\to$ 15,100 | 17,874 $\to$ 10,883 | 6,607,200 | 2,796,400 | **30%** |
| 16 KB  | 15,943 $\to$ 12,463 | 10,586 $\to$ 9,415  | 1,392,000 | 468,400   | **25%** |
| 64 KB  | 12,610 $\to$ 11,570 | 6,321 $\to$ 6,195   | 416,000   | 50,400    | **11%** |
| 256 KB | 11,709 $\to$ 11,216 | 852 $\to$ 51        | 197,200   | 320,400   | **62%** |

#### `swim.trace` (16 B block, WA/WB/LRU)
| Capacity | Misses 1-way $\to$ 16-way | Dirty Evictions 1-way $\to$ 16-way | Saving from Misses | Saving from Writebacks | Writeback Share |
| :---: | :---: | :---: | ---: | ---: | :---: |
| 4 KB   | 21,448 $\to$ 16,270 | 13,747 $\to$ 11,326 | 2,071,200 | 968,400 | **32%** |
| 16 KB  | 13,920 $\to$ 11,672 | 10,751 $\to$ 10,012 | 899,200   | 295,600 | **25%** |
| 64 KB  | 11,786 $\to$ 11,525 | 7,075 $\to$ 7,121   | 104,400   | -18,400 | **-21%** |
| 256 KB | 11,528 $\to$ 11,423 | 1,284 $\to$ 2       | 42,000    | 512,800 | **92%** |

**The mechanism inverts with capacity.** Below 64 KB, associativity eliminates **conflict misses** — 68–75% of the benefit is avoided fetch cycles. At 256 KB the miss count has plateaued (varying ~4% on `gcc` and ~1% on `swim` across the full associativity range), and associativity instead **retains dirty lines long enough that they are never written back**: writebacks collapse 852 $\to$ 51 on `gcc` and 1,284 $\to$ 2 on `swim`, accounting for 62% and 92% of those savings.

The 64 KB trough sits between the two regimes — conflict misses largely exhausted, but the *modified* working set still exceeding capacity. On `swim` at 64 KB the writeback contribution is slightly **negative** (dirty evictions rise 7,075 $\to$ 7,121, as retained dirty lines are eventually evicted anyway), giving the weakest gain in the sweep at 1.10–1.32%.

**Implication:** in a write-back cache, associativity buys *writeback suppression* as well as conflict-miss elimination, and past a certain capacity that becomes the dominant term. Miss-rate deltas alone would have hidden the entire 256 KB effect.

---

## 3. Block Size Effect: Spatial Locality vs. Miss Penalty Tradeoff

### 3.1 Experimental Results (Iso-Capacity 64 KB, 4-Way SA, WA/WB/LRU)

The simulator models memory transfer latency as $100 \times (\text{block\_bytes} / 4)$ cycles per memory block transfer. Thus:
- **16-byte block:** 4 words $\to$ **400 cycle** transfer penalty
- **32-byte block:** 8 words $\to$ **800 cycle** transfer penalty
- **64-byte block:** 16 words $\to$ **1,600 cycle** transfer penalty
- **128-byte block:** 32 words $\to$ **3,200 cycle** transfer penalty

#### `gcc.trace` (64 KB Capacity, 4-way SA, WA/WB/LRU)
| Sets | Ways | Block Size | Miss Penalty | Load Misses | Store Misses | Total Misses | Miss Rate | Total Cycles | Cycles / Access |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1024 | 4 | **16 B**  | 400 cyc  | 2,692 | 8,925 | 11,617 | **2.25%** | **7,620,883**  | **14.78** |
| 512  | 4 | **32 B**  | 800 cyc  | 1,794 | 4,582 | 6,376  | **1.24%** | **8,400,483**  | **16.29** |
| 256  | 4 | **64 B**  | 1600 cyc | 1,242 | 2,430 | 3,672  | **0.71%** | **9,707,683**  | **18.82** |
| 128  | 4 | **128 B** | 3200 cyc | 887   | 1,345 | 2,232  | **0.43%** | **11,760,483** | **22.81** |

#### `swim.trace` (64 KB Capacity, 4-way SA, WA/WB/LRU)
| Sets | Ways | Block Size | Miss Penalty | Load Misses | Store Misses | Total Misses | Miss Rate | Total Cycles | Cycles / Access |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1024 | 4 | **16 B**  | 400 cyc  | 1,025 | 10,506 | 11,531 | **3.80%** | **7,744,393**  | **25.54** |
| 512  | 4 | **32 B**  | 800 cyc  | 666   | 5,817  | 6,483  | **2.14%** | **8,815,993**  | **29.08** |
| 256  | 4 | **64 B**  | 1600 cyc | 451   | 3,071  | 3,522  | **1.16%** | **9,591,193**  | **31.63** |
| 128  | 4 | **128 B** | 3200 cyc | 318   | 1,561  | 1,879  | **0.62%** | **10,159,193** | **33.51** |

### 3.2 Locality vs. Transfer Cost
1. **Spatial locality cuts misses sharply.** 16 B $\to$ 128 B reduces total misses **80.8%** on `gcc` (11,617 $\to$ 2,232) and **83.7%** on `swim` (11,531 $\to$ 1,879).
2. **Transfer latency scales linearly.** Doubling block size doubles the miss penalty; transferred bytes never referenced are wasted bus cycles.
3. **Dirty evictions amplify it.** A writeback costs the same $100 \times (\text{block\_bytes}/4)$, so at 128 B a dirty miss costs $3{,}200 + 3{,}200 = 6{,}400$ cycles.
4. **Net effect:** the penalty outweighs the miss reduction on both traces, and cycles grow monotonically from 16 B to 128 B. Under this cost model **16-byte blocks are optimal**.

---

## 4. Eviction Policy: LRU vs. FIFO

### 4.1 Comparative Results across Configurations (WA/WB, 16B Block)

We evaluated Least Recently Used (LRU) versus First-In, First-Out (FIFO) across associativities and capacities:

| Benchmark | Capacity | Sets | Ways | LRU Miss Rate | LRU Total Cycles | FIFO Miss Rate | FIFO Total Cycles | FIFO Cycle Penalty ($\Delta$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`gcc.trace`** | 16 KB | 1024 | 1 | 3.09% | 11,127,283 | 3.09% | 11,127,283 | **+0 (+0.00%)** |
| | 16 KB | 512 | 2 | 2.54% | 9,588,883 | 2.68% | 10,022,883 | **+434,000 (+4.53%)** |
| | 16 KB | 256 | 4 | 2.45% | 9,344,483 | 2.61% | 9,845,283 | **+500,800 (+5.36%)** |
| | 16 KB | 128 | 8 | 2.42% | 9,277,683 | 2.59% | 9,781,683 | **+504,000 (+5.43%)** |
| | 16 KB | 64  | 16| 2.42% | 9,266,883 | 2.58% | 9,778,483 | **+511,600 (+5.52%)** |
| | 64 KB | 4096 | 1 | 2.45% | 8,088,083 | 2.45% | 8,088,083 | **+0 (+0.00%)** |
| | 64 KB | 2048 | 2 | 2.27% | 7,662,083 | 2.31% | 7,803,283 | **+141,200 (+1.84%)** |
| | 64 KB | 1024 | 4 | 2.25% | 7,620,883 | 2.30% | 7,772,083 | **+151,200 (+1.98%)** |
| | 64 KB | 512  | 8 | 2.25% | 7,609,683 | 2.29% | 7,766,483 | **+156,800 (+2.06%)** |
| | 64 KB | 256  | 16| 2.24% | 7,621,683 | 2.29% | 7,764,883 | **+143,200 (+1.88%)** |
| | | | | | | | | |
| **`swim.trace`**| 16 KB | 1024 | 1 | 4.59% | 10,171,593 | 4.59% | 10,171,593 | **+0 (+0.00%)** |
| | 16 KB | 512 | 2 | 3.92% | 9,099,193 | 4.34% | 9,735,993 | **+636,800 (+7.00%)** |
| | 16 KB | 256 | 4 | 3.87% | 9,009,593 | 4.30% | 9,655,593 | **+646,000 (+7.17%)** |
| | 16 KB | 128 | 8 | 3.86% | 8,991,593 | 4.31% | 9,679,193 | **+687,600 (+7.65%)** |
| | 16 KB | 64  | 16| 3.85% | 8,976,793 | 4.30% | 9,657,593 | **+680,800 (+7.58%)** |
| | 64 KB | 4096 | 1 | 3.89% | 7,847,593 | 3.89% | 7,847,593 | **+0 (+0.00%)** |
| | 64 KB | 2048 | 2 | 3.82% | 7,745,193 | 3.86% | 7,859,193 | **+114,000 (+1.47%)** |
| | 64 KB | 1024 | 4 | 3.80% | 7,744,393 | 3.85% | 7,850,393 | **+106,000 (+1.37%)** |
| | 64 KB | 512  | 8 | 3.80% | 7,753,193 | 3.84% | 7,848,793 | **+95,600 (+1.23%)** |
| | 64 KB | 256  | 16| 3.80% | 7,761,593 | 3.83% | 7,849,593 | **+88,000 (+1.13%)** |

### 4.2 Implications
1. **Identical at 1-way.** With one slot per set, replacement is deterministic and the policies coincide exactly on every metric.
2. **LRU tracks reuse, FIFO tracks age.** LRU refreshes `access_ts` on every access; FIFO sets `load_ts` only at insertion, so a hot line is evicted purely for being old.
3. **The gap closes as capacity grows.** At 16 KB, FIFO costs **+7.65%** on `swim` (+687,600 cycles) and **+5.52%** on `gcc` (+511,600). At 64 KB it narrows to $\sim 1.2\%\text{--}2.0\%$ as evictions become rarer.

---

## 5. Write and Allocation Policies

### 5.1 Comparative Results (64 KB Capacity, 4-Way SA, 16B Block, LRU)

The simulator evaluates three valid policy pairs:
1. `write-allocate` + `write-back` (WA/WB)
2. `write-allocate` + `write-through` (WA/WT)
3. `no-write-allocate` + `write-through` (NWA/WT)

*(Note: `no-write-allocate` + `write-back` is disallowed by cache design and rejected by the simulator).*

| Benchmark | Write Allocation | Write Policy | Load Misses | Store Misses | Total Misses | Miss Rate | Total Cycles | Cycles / Access |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`gcc.trace`** | Write-Allocate | Write-Back | 2,692 | 8,925 | 11,617 | **2.25%** | **7,620,883** | **14.78** |
| (516,566 total accesses; | Write-Allocate | Write-Through | 2,692 | 8,925 | 11,617 | **2.25%** | **24,911,083** | **48.31** |
| 38.41% stores) | No-Write-Allocate| Write-Through | 6,072 | 32,284 | 38,356 | **7.44%** | **22,693,083** | **44.01** |
| | | | | | | | | |
| **`swim.trace`** | Write-Allocate | Write-Back | 1,025 | 10,506 | 11,531 | **3.80%** | **7,744,393** | **25.54** |
| (303,135 total accesses; | Write-Allocate | Write-Through | 1,025 | 10,506 | 11,531 | **3.80%** | **13,168,093** | **43.43** |
| 13.97% stores) | No-Write-Allocate| Write-Through | 2,535 | 24,475 | 27,010 | **8.91%** | **9,569,693** | **31.56** |

### 5.2 Write Traffic & Overhead Analysis
1. **Store frequency drives the penalty.** `gcc` is 38.41% stores (198,393); at 100 cycles each, write-through injects $\sim 19.8\text{M}$ cycles — **24.91M vs. 7.62M**, a **$3.27\times$** slowdown. `swim`, at 13.97% stores (42,342), still pays $4.23\text{M}$ extra cycles for a **$1.70\times$** slowdown (13.17M vs. 7.74M).
2. **Write-back coalesces.** Repeated writes to one block collapse into a single memory transfer at eviction.
3. **NWA beats WA under write-through.** A store miss costs $400 + 100 + 1 = 501$ cycles with allocation, versus $100 + 1 = 101$ without. Skipping the fetch makes NWA/WT *faster* than WA/WT on `gcc` (22.69M vs. 24.91M) despite a far worse miss rate (7.44% vs. 2.25%) — miss rate alone is a poor proxy for time.
4. **WA/WB wins overall**, by up to $69.4\%$ in total cycles.

---

## 6. Capacity Scaling

### 6.1 Capacity Scaling Matrix (4-Way SA, 16B Block, WA/WB/LRU)

Holding cache geometry constant (4-way SA, 16B blocks, WA/WB/LRU), we scaled capacity from 4 KB to 256 KB:

#### `gcc.trace` (4-Way SA, 16B Block, WA/WB/LRU)
| Capacity | Sets | Load Misses | Store Misses | Total Misses | Miss Rate | Total Cycles | Cycle $\Delta$ vs 4 KB | Cycles / Access |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **4 KB**   | 64   | 6,098 | 9,960 | 16,058 | 3.11% | 11,414,883 | Baseline | 22.14 |
| **16 KB**  | 256  | 3,399 | 9,236 | 12,635 | 2.45% | 9,344,483  | -18.14% (-2.07M) | 18.12 |
| **64 KB**  | 1024 | 2,692 | 8,925 | 11,617 | 2.25% | 7,620,883  | -33.24% (-3.79M) | 14.78 |
| **256 KB** | 4096 | 2,362 | 8,878 | 11,240 | 2.18% | 5,130,883  | -55.05% (-6.28M) | 9.95  |

#### `swim.trace` (4-Way SA, 16B Block, WA/WB/LRU)
| Capacity | Sets | Load Misses | Store Misses | Total Misses | Miss Rate | Total Cycles | Cycle $\Delta$ vs 4 KB | Cycles / Access |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **4 KB**   | 64   | 5,745 | 11,172 | 16,917 | 5.58% | 11,733,193 | Baseline | 38.70 |
| **16 KB**  | 256  | 1,161 | 10,569 | 11,730 | 3.87% | 9,009,593  | -23.21% (-2.72M) | 29.72 |
| **64 KB**  | 1024 | 1,025 | 10,506 | 11,531 | 3.80% | 7,744,393  | -34.00% (-3.99M) | 25.54 |
| **256 KB** | 4096 | 927   | 10,497 | 11,424 | 3.77% | 4,893,593  | -58.29% (-6.84M) | 16.14 |

### 6.2 Working-Set Fit and Dirty-Eviction Collapse
Decomposing execution cycles into **fetch penalty** versus **dirty writeback**:

$$\text{Total Cycles} = \text{Total Accesses} \times 1 + (\text{Total Misses} \times 400) + (\text{Dirty Evictions} \times 400)$$

| Benchmark | Capacity | Total Misses | Miss Fetch Cycles | Dirty Evictions | Dirty Writeback Cycles | Total Execution Cycles |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`gcc.trace`** | 4 KB   | 16,058 | 6,423,200 | 11,190 | 4,476,000 | 11,414,883 |
| | 16 KB  | 12,635 | 5,054,000 | 9,437  | 3,774,800 | 9,344,483 |
| | 64 KB  | 11,617 | 4,646,800 | 6,146  | 2,458,400 | 7,620,883 |
| | **256 KB** | **11,240** | **4,496,000** | **298** | **119,200** | **5,130,883** |
| | | | | | | |
| **`swim.trace`**| 4 KB   | 16,917 | 6,766,800 | 11,658 | 4,663,200 | 11,733,193 |
| | 16 KB  | 11,730 | 4,692,000 | 10,036 | 4,014,400 | 9,009,593 |
| | 64 KB  | 11,531 | 4,612,400 | 7,072  | 2,828,800 | 7,744,393 |
| | **256 KB** | **11,424** | **4,569,600** | **52** | **20,800** | **4,893,593** |

From 64 KB to 256 KB, misses barely move (377 fewer on `gcc`, 107 on `swim`), yet cycles fall **2.49M** and **2.85M** respectively. The cause is the **modified working set fitting entirely in cache**, collapsing dirty evictions from 6,146 to 298 on `gcc` and 7,072 to 52 on `swim`.

---

## 7. Workload Characterization: `gcc.trace` vs. `swim.trace`

The two benchmarks exhibit fundamentally different memory behavior:

```
+------------------------------------+------------------------------------+
|             gcc.trace              |             swim.trace             |
+------------------------------------+------------------------------------+
| * Total Accesses: 516,566          | * Total Accesses: 303,135          |
| * Loads: 318,173 (61.59%)          | * Loads: 260,793 (86.03%)          |
| * Stores: 198,393 (38.41%)         | * Stores: 42,342 (13.97%)          |
| * Access Pattern: Complex control  | * Access Pattern: Regular, nested  |
|   flow, dynamic pointer chasing,   |   multidimensional grid sweeps,    |
|   stack frame updates.             |   matrix array traversal.          |
| * Locality: Strong temporal        | * Locality: High spatial locality, |
|   clustering with heavy write      |   large grid working set requiring |
|   frequency. Highly sensitive to   |   >= 16 KB capacity.               |
|   write policy.                    |                                    |
+------------------------------------+------------------------------------+
```

1. **Write intensity:** `gcc` writes nearly $3\times$ as often as `swim` (38.41% vs. 13.97%), so write-through costs it 227% overhead against `swim`'s 70%.
2. **Spatial locality:** `swim`'s linear grid sweeps cut miss rate over $83\%$ from 16 B to 128 B blocks — but bus latency still makes 16 B optimal on both traces.

---

## 8. Optimal Cache Configuration & Hardware Overhead Analysis

### 8.1 Recommended Cache Configuration

Across the 960-configuration sweep, the best-balanced L1 configuration is:

> **Selected Architecture:**  
> **64 KB Capacity, 4-Way Set-Associative, 16-Byte Block Size, Write-Allocate + Write-Back, LRU Eviction**  
> *(Parameters: `1024 4 16 write-allocate write-back lru`)*

**Justification:**
1. **Performance:** 7,620,883 cycles (14.78 /access) on `gcc` and 7,744,393 (25.54 /access) on `swim`, at over $97.7\%$ hit rate.
2. **Associativity:** 4-way lands within 0.15% of 8- and 16-way while avoiding their hit-latency, area, and routing costs.
3. **Block size:** 16 B minimizes transfer latency under the $100 \times (\text{bytes}/4)$ penalty model.
4. **Policies:** WA/WB removes redundant memory writes; LRU retains lines by reuse rather than age.

*Note:* 256 KB is faster still (5.13M / 4.89M cycles) but is well outside a realistic L1 budget; see Section 6.

---

### 8.2 Step-by-Step Metadata Overhead Calculation

Real cache hardware requires auxiliary storage bits for tags and status metadata in addition to data capacity.

#### Step 1: Address Bit Breakdown (32-bit Architecture)
For a 64 KB cache with 1024 sets, 4 ways, and 16-byte blocks:
- **Address Width ($N$):** $32\text{ bits}$
- **Block Offset Bits ($b$):** $\log_2(\text{BlockBytes}) = \log_2(16) = 4\text{ bits}$ (Address bits $[3:0]$)
- **Set Index Bits ($s$):** $\log_2(\text{NumSets}) = \log_2(1024) = 10\text{ bits}$ (Address bits $[13:4]$)
- **Tag Bits ($t$):** $N - s - b = 32 - 10 - 4 = 18\text{ bits}$ (Address bits $[31:14]$)

#### Step 2: Per-Slot Metadata Storage
Each slot (block entry) stores:
- **Tag:** $18\text{ bits}$
- **Valid Bit:** $1\text{ bit}$
- **Dirty Bit:** $1\text{ bit}$ (required for Write-Back)
- **LRU State:** For 4-way associativity, tracking exact LRU order requires $\lceil\log_2(4)\rceil = 2\text{ bits}$ per slot (or $\log_2(4!) = 4.58 \to 5\text{ bits}$ per set via permutation encodings). Using 2 bits/slot:

$$\text{Overhead per slot} = 18\text{ (tag)} + 1\text{ (valid)} + 1\text{ (dirty)} + 2\text{ (LRU)} = 22\text{ bits/slot}$$

#### Step 3: Total Cache Metadata Footprint
- **Total Slots:** $\text{Sets} \times \text{Ways} = 1024 \times 4 = 4,096\text{ slots}$
- **Total Metadata Bits:** $4,096\text{ slots} \times 22\text{ bits/slot} = 90,112\text{ bits}$
- **Total Metadata Bytes:** $\frac{90,112\text{ bits}}{8\text{ bits/byte}} = 11,264\text{ bytes} = 11.00\text{ KiB}\text{ (or } 11.264\text{ kB decimal)}$
- **Data Capacity:** $65,536\text{ bytes} = 64.00\text{ KiB}$
- **Metadata Overhead Percentage:**

$$\text{Overhead Fraction} = \frac{11,264\text{ bytes}}{65,536\text{ bytes}} = 17.1875\% \approx 17.19\%$$

- **Total Physical Footprint:** $65,536\text{ B} + 11,264\text{ B} = 76,800\text{ bytes} = 75.00\text{ KiB}\text{ (or } 76.80\text{ kB decimal)}$

---

### 8.3 Metadata Overhead Comparison Across Configurations

The table below illustrates how hardware metadata overhead scales across varying block sizes and associativities for a 64 KB cache:

| Capacity | Sets | Ways | Block Size | Offset Bits | Index Bits | Tag Bits | Bits / Slot | Total Metadata | Overhead % | Total Physical Footprint |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 64 KB | 4096 | 1  | 16 B | 4 | 12 | 16 | 18 | 9.00 KiB  | 14.06% | 73.00 KiB |
| 64 KB | 2048 | 2  | 16 B | 4 | 11 | 17 | 20 | 10.00 KiB | 15.62% | 74.00 KiB |
| **64 KB** | **1024** | **4**  | **16 B** | **4** | **10** | **18** | **22** | **11.00 KiB** | **17.19%** | **75.00 KiB** |
| 64 KB | 512  | 8  | 16 B | 4 | 9  | 19 | 24 | 12.00 KiB | 18.75% | 76.00 KiB |
| 64 KB | 256  | 16 | 16 B | 4 | 8  | 20 | 26 | 13.00 KiB | 20.31% | 77.00 KiB |
| | | | | | | | | | | |
| 64 KB | 512  | 4  | 32 B | 5 | 9  | 18 | 22 | 5.50 KiB  | 8.59%  | 69.50 KiB |
| 64 KB | 256  | 4  | 64 B | 6 | 8  | 18 | 22 | 2.75 KiB  | 4.30%  | 66.75 KiB |
| 64 KB | 128  | 4  | 128 B| 7 | 7  | 18 | 22 | 1.38 KiB  | 2.15%  | 65.38 KiB |

**Observation:** each doubling of block size halves the slot count and therefore the metadata storage — but Section 3 shows that area saving is paid for in transfer cycles.

---

## 9. Experimental Methodology & Reproduction

### 9.1 Build

```bash
make
```

### 9.2 Full Sweep
All 960 configurations reproduce deterministically via [`run_experiments.py`](file:///c:/JHU/CSF/csf_assign03/run_experiments.py):

```bash
python run_experiments.py --output results.csv
```

---

## 10. Summary & Conclusions

1. **Two methodologies, two answers.** Capacity-scaling (4 KB 1-way $\to$ 64 KB 4-way) gives $62.48\%$; iso-capacity attributes $43.80\%$ of it to associativity at 4 KB. Both are valid measurements of different questions, and stating which one is in use is what makes either citable.
2. **Associativity is capacity-dependent.** At iso-capacity, 4-way over direct-mapped is worth $43.80\%$ at 4 KB, $16.02\%$ at 16 KB, and $5.78\%$ at 64 KB on `gcc`. No single number describes it.
3. **The mechanism inverts with capacity.** Below 64 KB associativity eliminates conflict misses (68–75% of the benefit); at 256 KB it removes almost none and instead suppresses dirty writebacks (62% on `gcc`, 92% on `swim`) — a non-monotonic curve that miss-rate analysis alone would miss.
4. **Block size:** under the $100 \times \text{words}$ transfer model, 16 B gives the lowest cycle count despite 128 B giving the lowest miss rate.
5. **Write policy:** WA/WB is decisive on write-heavy workloads, up to $3.27\times$ faster than write-through.
6. **Eviction:** LRU beats FIFO on all associative configurations, by up to $7.65\%$.
7. **Overhead:** the 64 KB 4-way 16 B cache carries **11.00 KiB (17.19%)** of metadata, for a **75.00 KiB** physical footprint.

---

## Appendix A: Initial Seven-Configuration Study

The study began as a seven-configuration comparison using the capacity-scaling methodology of Section 1.1. It is preserved here verbatim: every cycle count below reappears unchanged in the 960-configuration sweep, and its conclusions are the baseline the iso-capacity analysis in Sections 1–2 builds on. Where a conclusion below compares caches of differing capacity, Section 1.3 gives the corresponding iso-capacity figure.

### A.1 Results (`gcc.trace`)

| Sets | Blocks | Bytes | Write Alloc | Write Policy | Eviction | Load Misses | Store Misses | Total Cycles |
|------|--------|-------|-------------|--------------|----------|-------------|--------------|--------------|
| 256  | 1      | 16    | allocate    | back         | lru      | 19,334      | 12,284       | 20,312,483   |
| 256  | 4      | 16    | allocate    | back         | lru      | 3,399       | 9,236        | 9,344,483    |
| 512  | 4      | 16    | allocate    | back         | lru      | 2,986       | 9,018        | 8,607,683    |
| 128  | 4      | 32    | allocate    | back         | lru      | 2,508       | 4,849        | 10,616,483   |
| 1024 | 4      | 16    | allocate    | back         | lru      | 2,692       | 8,925        | 7,620,883    |
| 256  | 4      | 16    | no-alloc    | through      | lru      | 6,584       | 32,667       | 22,865,216   |
| 256  | 4      | 16    | allocate    | back         | fifo     | 4,026       | 9,439        | 9,845,283    |

### A.2 Analysis (verbatim)

1. The performance difference between write-allocate/write-back and no-write-allocate/write-through is huge. For gcc.trace, which contains frequent writes, write-back is way more efficient because it avoids the 100-cycle penalty for every memory write.
2. Moving from a direct-mapped cache (20M cycles) to a 4-way set-associative cache (9.3M cycles) halved the cycles, which is a huge improvement.
3. While increasing block size from 16 to 32 bytes reduced the total number of misses, it significantly increased overall cycles (10.6M vs 9.3M). I think this is because the miss penalty doubled (800 cycles vs 400 cycles), and the increased bandwidth usage didn't compensate for the locality benefits.
4. LRU consistently outperformed FIFO for these configurations, with roughly 500,000 fewer cycles in our baseline 16KB 4-way SA cache.

### A.3 Best Configuration (verbatim)

> I think that a 64KB, 4-way set-associative cache with 16-byte blocks, using write-allocate and write-back with LRU eviction, is the best configuration. It achieved the lowest cycle count (7.6M) and a very high hit rate, showing a good balance between capacity and data transfer efficiency.

### A.4 The Same Conclusions Under Iso-Capacity Control

| # | Initial Claim | Status | Notes |
| :--- | :--- | :--- | :--- |
| 1 | Write-back $\gg$ write-through on write-heavy `gcc` | **Confirmed** | Holds at iso-capacity; measured $3.27\times$ speedup (Section 5). |
| 2 | Direct-mapped $\to$ 4-way "halved the cycles" | **Refined** | Measured across 4 KB vs. 16 KB, so capacity contributes. At iso-capacity the figure is 16.02% at 16 KB and 43.80% at 4 KB (Sections 1.3, 2.1). |
| 3 | Larger blocks reduce misses but increase cycles | **Confirmed, extended** | Holds monotonically across all four block sizes and both traces (Section 3). |
| 4 | LRU consistently outperforms FIFO | **Confirmed** | Holds across the sweep; FIFO costs up to +7.65% on `swim` (Section 4). LRU $\equiv$ FIFO at 1-way. |
| — | 64 KB 4-way is the "best configuration" | **Confirmed for L1** | Lowest-cycle entry in the seven-config set; the full sweep adds 256 KB, which is faster but outside a realistic L1 budget (Section 8). |

Three of the four initial conclusions carry over unchanged. The fourth holds too, once the capacity contribution is separated out — it was the only comparison in the set that moved two parameters at once.
---

## Contributions

- **Simulation Engine:** Implemented the trace processing loop, set/tag indexing, valid/dirty bit maintenance, and cycle accounting in `csim`.
- **Validation & Correctness:** Verified parameter validation, power-of-two constraints, and illegal policy detection (`no-write-allocate` + `write-back`).
- **Automated Experimentation:** Developed the parallel experiment harness `run_experiments.py` and generated `results.csv`.
- **Architectural Analysis:** Developed the iso-capacity evaluation methodology, extended the initial seven-configuration study to a 960-configuration sweep, and authored the performance and hardware overhead analysis.
