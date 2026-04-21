# Run experiments for cache simulator
import subprocess
import os

configs = [
    (256, 1, 16, "write-allocate", "write-back", "lru"),
    (256, 4, 16, "write-allocate", "write-back", "lru"),
    (512, 4, 16, "write-allocate", "write-back", "lru"),
    (128, 4, 32, "write-allocate", "write-back", "lru"),
    (1024, 4, 16, "write-allocate", "write-back", "lru"),
    (256, 4, 16, "no-write-allocate", "write-through", "lru"),
    (256, 4, 16, "write-allocate", "write-back", "fifo"),
]

trace_file = "traces/gcc.trace"

print("Sets,Blocks,Bytes,WriteAlloc,WritePolicy,Eviction,LoadHits,LoadMisses,StoreHits,StoreMisses,TotalCycles")

for sets, blocks, bytes, wa, wp, ev in configs:
    # Use direct stdin instead of cat to avoid platform issues
    with open(trace_file, 'r') as f:
        cmd = ["./csim.exe", str(sets), str(blocks), str(bytes), wa, wp, ev]
        process = subprocess.Popen(cmd, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
    
    # Debug: print(stdout)
    lines = stdout.strip().split('\n')
    results = {}
    for line in lines:
        if ':' in line:
            parts = line.split(':')
            if len(parts) == 2:
                key, val = parts
                results[key.strip()] = val.strip()
            
    print(f"{sets},{blocks},{bytes},{wa},{wp},{ev},{results.get('Load hits')},{results.get('Load misses')},{results.get('Store hits')},{results.get('Store misses')},{results.get('Total cycles')}")
