# Assignment 3: Cache Simulator

**Course:** CSF @ JHU

**Due Dates:**
- Milestone 1: Friday, March 6th *(no late hours)*
- Milestone 2: Wednesday, March 25th by 11pm *(max 48 late hours)*
- Milestone 3: Wednesday, April 1st by 11pm

**Assignment type:** Pair — you may work with one partner

> **Note on late hours:** If you anticipate using more than 48 late hours on Milestone 3, post privately (to instructors and CAs) on Courselore to request permission. Late hours may not be used on Milestone 1, and at most 48 late hours may be used on Milestone 2.

---

## Overview

*Acknowledgment: This assignment was originally developed by Peter Fröhlich for his version of CSF.*

This problem focuses on simulating and evaluating caches. You'll be given a number of memory traces from real benchmark programs. You'll implement a program to simulate how a variety of caches perform on these traces, then use your program and the given traces to determine the best overall cache configuration.

---

## Milestone 1 (5 points)

For this submission, you must have started working on your code and have at least one submission uploaded to Gradescope which successfully builds an executable named `csim` when the autograder executes:

```
make csim
```

Starter code is available here: `csf_assign03.zip`.

Even though you aren't required to have any specific program functionality working for Milestone 1, it is recommended that you at least make a start. Good places to begin include:

- Handling command line arguments
- Reading the memory trace file (reading each operation, determining the address accessed, and whether the access is a load or store)
- Getting some of the core data structures and functions in place for the actual cache simulation

> ⚠️ **Important:** For Milestone 1, there will be no credit for submissions that don't compile successfully and no credit for late submissions.

---

## Milestone 2 (15 points)

For this submission, you must have implemented your cache simulation for **LRU**.

---

## Milestone 3 (80 points)

All functions must be written with full assignment specifications met.

---

## Grading Criteria

| Criterion | Weight |
|---|---|
| Milestone 1 (`csim` executable can be built) | 5% |
| Gracefully handling invalid parameters | 1.5% |
| Accurate load count | 9% |
| Accurate store count | 9% |
| Accurate load hits | 12.5% |
| Accurate load misses | 12.5% |
| Accurate store hits | 12.5% |
| Accurate store misses | 12.5% |
| Accurate total cycles | 5.5% |
| Report on best cache | 10% |
| Design, coding style, and contributions | 10% |

For numeric results, **Total cycles** only needs to be within ±5%, while all other results must be exact.

Make sure you follow the style guidelines. Your program should execute without memory errors or memory leaks. Memory errors (invalid reads/writes, use of uninitialized memory) will result in a deduction of up to **10 points**. Memory leaks will result in a deduction of up to **5 points**.

---

## Programming Languages

You can use either **C** or **C++**. You're allowed to use the standard library of your chosen language as much as you'd like, but no additional (non-standard) libraries.

One advantage of C++ is access to built-in container data structures such as `map`, `vector`, etc. (Note that it is entirely possible to create a straightforward and robust implementation using dynamically-allocated arrays.)

Regardless of language, write modular, well-designed code. Strive for simplicity.

### Makefile Requirements

You must provide a `Makefile` such that:

- `make clean` removes all object files and executables
- `make` or `make csim` compiles and links your program, producing an executable called `csim`

Your code should compile cleanly using `-Wall -Wextra -pedantic` compiler flags.

> ⚠️ **Important:** Your Makefile **must** use these options. If your Makefile does not compile your code with these options, you will forfeit **all** points for design and coding style.

---

## Part (a): Cache Simulator

You will design and implement a cache simulator to study and compare the effectiveness of various cache configurations. Your simulator will:

1. Read a memory access trace from **standard input**
2. Simulate what a cache with given parameters would do in response to those memory accesses
3. Print summary statistics to **standard output**

### Trace File Format

```
s 0x1fffff50 1
l 0x1fffff58 1
l 0x1fffff88 6
l 0x1fffff90 2
l 0x1fffff98 2
l 0x200000e0 2
l 0x200000e8 2
l 0x200000f0 2
l 0x200000f8 2
l 0x30031f10 3
s 0x3004d960 0
s 0x3004d968 1
s 0x3004caa0 1
s 0x3004d970 1
s 0x3004d980 6
l 0x30000008 1
l 0x1fffff58 4
l 0x3004d978 4
l 0x1fffff68 4
l 0x1fffff68 2
s 0x3004d980 9
l 0x30000008 1
```

Each memory access is recorded on a separate line with three whitespace-separated fields:

1. `l` or `s` — whether the processor is **loading** from or **storing** to memory
2. A 32-bit memory address in hexadecimal (the `0x` prefix is not part of the address)
3. A third field — **ignore this for the assignment**

> Each load or store accesses at most 4 bytes of data, and no load or store accesses data spanning multiple cache blocks.

### Cache Design Parameters (Command-Line Arguments)

- **Number of sets** in the cache (positive power of 2)
- **Number of blocks** per set (positive power of 2)
- **Number of bytes** per block (positive power of 2, at least 4)
- `write-allocate` or `no-write-allocate`
- `write-through` or `write-back`
- `lru` (least-recently-used) or `fifo` (first-in-first-out) evictions

### Cache Configurations

| Configuration | Description |
|---|---|
| `n` sets of `1` block each | Direct-mapped |
| `n` sets of `m` blocks each | `m`-way set-associative |
| `1` set of `n` blocks | Fully associative |

The smallest valid cache is 1 set, 1 block, 4 bytes — this can only benefit if consecutive accesses go to the exact same address (useful for basic sanity testing).

### Write Policy Details

**Write-allocate** (determines behavior on store miss):
- `write-allocate`: bring the relevant memory block into the cache before the store proceeds
- `no-write-allocate`: a store miss does not modify the cache

**Write-through** (determines whether stores go immediately to memory):
- `write-through`: store writes to both the cache and memory
- `write-back`: store writes to the cache only and marks the block dirty; if the block is later evicted, it is written back to memory first

> ⚠️ It does **not** make sense to combine `no-write-allocate` with `write-back`.

The eviction parameter is only relevant for associative caches (direct-mapped caches have no choice):
- `lru`: evict the block that has not been accessed the longest
- `fifo`: evict the block that has been in the cache the longest

### Cycle Counting

- Loads/stores from/to the **cache**: **1 processor cycle**
- Loads/stores from/to **memory**: **100 processor cycles** per 4-byte quantity transferred

### Running the Simulator

```
./csim 256 4 16 write-allocate write-back lru < sometracefile
```

This simulates a 4-way set-associative cache with 256 sets, 16-byte blocks, write-allocate, write-back, and LRU eviction. (Total size: 16,384 bytes = 16 kB, ignoring metadata overhead.)

### Output Format

```
Total loads: count
Total stores: count
Load hits: count
Load misses: count
Store hits: count
Store misses: count
Total cycles: count
```

### Example

```
./csim 256 4 16 write-allocate write-back fifo < gcc.trace
```

Expected output:

```
Total loads: 318197
Total stores: 197486
Load hits: 314171
Load misses: 4026
Store hits: 188047
Store misses: 9439
Total cycles: 9845283
```

> Note: Your **Total cycles** value may vary slightly (within ±5%). All other counts must match exactly.

### Reporting Invalid Parameters

Before starting the simulation, validate the parameters. Examples of invalid configurations:

- Block size is not a power of 2
- Number of sets is not a power of 2
- Block size is less than 4
- `write-back` and `no-write-allocate` were both specified

If parameters are invalid:
1. Print an error message to `stderr` / `std::cerr`
2. Exit with a non-zero exit code

---

## Example Traces

| Trace | Notes |
|---|---|
| `gcc.trace` | Real program trace (use for empirical evaluation) |
| `read01.trace` | — |
| `read02.trace` | — |
| `read03.trace` | — |
| `swim.trace` | Real program trace (use for empirical evaluation) |
| `write01.trace` | — |
| `write02.trace` | — |

Download traces from the command line using `curl`, e.g.:

```bash
curl -O https://jhucsf.github.io/spring2026/assign/assign03/read01.trace
```

*(Use the uppercase letter `O`, not the digit `0`.)*

---

## Hints

- Your simulation is only concerned with **hits and misses** — you never need the actual data stored in the cache (which is why trace files don't contain it).
- Don't try to implement all options at once. Start with a direct-mapped cache using write-through and no-write-allocate, then extend step-by-step.
- Sanity-check frequently with small, hand-crafted traces for which you can manually derive the expected behavior.
- Accurate cycle counting is worth only ~6% of the grade. Prioritize getting hit/miss counts correct first.

---

## Part (b): Best Cache & Contributions

Use the memory traces and your simulator to determine which cache configuration has the **best overall effectiveness**. Consider:

- Hit rates
- Miss penalties
- Total cache size (including overhead)

In your `README.txt`, describe:
- What experiments you ran (and why)
- What results you got (and how)
- What, in your opinion, is the best cache configuration

Also include a brief summary of how work was divided between partners and what each person contributed. *(Not required if you worked alone.)*

---

## Submitting

For each milestone, create a **zip file** containing your `Makefile`, all source and header files, and `README.txt` — all in the **top-level directory** of the zip.

Example structure for `assign3.zip`:

```
Archive: assign3.zip
  main.c
  Makefile
  README.txt
```

Upload to Gradescope as **Assignment 3 MS1**, **Assignment 3 MS2**, or **Assignment 3 MS3** as appropriate.

---

*Memory traces courtesy of Steven Swanson, University of California, San Diego.*