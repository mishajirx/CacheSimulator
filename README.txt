# Cache Simulator Project

## Experiments:
I evaluated the cache simulator performance using the gcc.trace memory trace. We explored variations in associativity, block size, write policies, and eviction policies to determine the optimal configuration for this benchmark.

Results Table (gcc.trace):
Sets | Blocks | Bytes | Write Alloc | Write Policy | Eviction | Load Misses | Store Misses | Total Cycles
-----|--------|-------|-------------|--------------|----------|-------------|--------------|-------------
256  | 1      | 16    | allocate    | back         | lru      | 19,334      | 12,284       | 20,312,483
256  | 4      | 16    | allocate    | back         | lru      | 3,399       | 9,236        | 9,344,483
512  | 4      | 16    | allocate    | back         | lru      | 2,986       | 9,018        | 8,607,683
128  | 4      | 32    | allocate    | back         | lru      | 2,508       | 4,849        | 10,616,483
1024 | 4      | 16    | allocate    | back         | lru      | 2,692       | 8,925        | 7,620,883
256  | 4      | 16    | no-alloc    | through      | lru      | 6,584       | 32,667       | 22,865,216
256  | 4      | 16    | allocate    | back         | fifo     | 4,026       | 9,439        | 9,845,283

## Analysis:
1. The performance difference between write-allocate/write-back and no-write-allocate/write-through is huge. For gcc.trace, which contains frequent writes, write-back is way more efficient because it avoids the 100-cycle penalty for every memory write.
2. Moving from a direct-mapped cache (20M cycles) to a 4-way set-associative cache (9.3M cycles) halved the cycles, which is a huge improvement.
3. While increasing block size from 16 to 32 bytes reduced the total number of misses, it significantly increased overall cycles (10.6M vs 9.3M). I think this is because the miss penalty doubled (800 cycles vs 400 cycles), and the increased bandwidth usage didn't compensate for the locality benefits.
4. LRU consistently outperformed FIFO for these configurations, with roughly 500,000 fewer cycles in our baseline 16KB 4-way SA cache.

## Best Cache Configuration:
I think that a 64KB, 4-way set-associative cache with 16-byte blocks, using write-allocate and write-back with LRU eviction, is the best configuration. It achieved the lowest cycle count (7.6M) and a very high hit rate, showing a good balance between capacity and data transfer efficiency.

## Total Size & Overhead:
While the data capacity is 64KB (1024 sets × 4 blocks × 16 bytes), the actual hardware footprint is larger because of the metadata. With 32-bit addresses, a 16-byte block needs a 4-bit offset, and 1024 sets need a 10-bit index, leaving an 18-bit tag. Adding 1 valid bit, 1 dirty bit, and roughly 2 bits for LRU tracking results in ~22 bits of overhead per block. Across 4096 total blocks, this adds exactly 11.26 KB of metadata, bringing the true physical size of the cache to about 75.26 KB.

## Contributions:
I worked on this project alone. I implemented the core simulation engine, parameter validation, and conducted the performance analysis.
