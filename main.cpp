#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

struct Slot {
  uint32_t tag;
  bool valid;
  bool dirty;
  uint32_t load_ts;
  uint32_t access_ts;
};

struct Set {
  std::vector<Slot> slots;
};

class CacheSimulator {
private:
  uint32_t num_sets;
  uint32_t num_blocks;
  uint32_t num_bytes;
  std::string write_alloc;
  std::string write_policy;
  std::string eviction;
  std::vector<Set> sets;
  uint32_t load_hits;
  uint32_t load_misses;
  uint32_t store_hits;
  uint32_t store_misses;
  uint32_t total_loads;
  uint32_t total_stores;
  uint32_t total_cycles;
  uint64_t ts;

public:
  CacheSimulator(uint32_t s, uint32_t b, uint32_t by, const std::string &wa,
                 const std::string &wp, const std::string &ev)
      : num_sets(s), num_blocks(b), num_bytes(by), write_alloc(wa),
        write_policy(wp), eviction(ev), load_hits(0), load_misses(0),
        store_hits(0), store_misses(0), total_loads(0), total_stores(0),
        total_cycles(0), ts(1) {
    sets.resize(num_sets);
    for (uint32_t i = 0; i < num_sets; ++i) {
      sets[i].slots.resize(num_blocks);
      for (uint32_t j = 0; j < num_blocks; ++j) {
        sets[i].slots[j] = {0, false, false, 0, 0};
      }
    }
  }

  void process_access(char type, uint32_t addr) {
    if (type == 'l')
      total_loads++;
    else if (type == 's')
      total_stores++;

    uint32_t block_addr = addr / num_bytes;
    uint32_t index = block_addr % num_sets;
    uint32_t tag = block_addr / num_sets;

    bool hit = false;
    int hit_idx = -1;

    for (uint32_t i = 0; i < num_blocks; ++i) {
      if (sets[index].slots[i].valid && sets[index].slots[i].tag == tag) {
        hit = true;
        hit_idx = i;
        break;
      }
    }

    if (hit) {
      if (type == 'l')
        load_hits++;
      else
        store_hits++;

      sets[index].slots[hit_idx].access_ts = ts++;
      total_cycles += 1;

      if (type == 's') {
        if (write_policy == "write-through") {
          total_cycles += 100;
        } else {
          sets[index].slots[hit_idx].dirty = true;
        }
      }
    } else {
      if (type == 'l')
        load_misses++;
      else
        store_misses++;

      if (type == 's' && write_alloc == "no-write-allocate") {
        total_cycles += 101;
      } else {
        int replace_idx = -1;
        for (uint32_t i = 0; i < num_blocks; ++i) {
          if (!sets[index].slots[i].valid) {
            replace_idx = i;
            break;
          }
        }

        if (replace_idx == -1) {
          replace_idx = 0;
          for (uint32_t i = 1; i < num_blocks; ++i) {
            if (eviction == "lru") {
              if (sets[index].slots[i].access_ts <
                  sets[index].slots[replace_idx].access_ts) {
                replace_idx = i;
              }
            } else {
              if (sets[index].slots[i].load_ts <
                  sets[index].slots[replace_idx].load_ts) {
                replace_idx = i;
              }
            }
          }
          if (sets[index].slots[replace_idx].dirty) {
            total_cycles += 100 * (num_bytes / 4);
          }
        }

        total_cycles += 100 * (num_bytes / 4);

        sets[index].slots[replace_idx].valid = true;
        sets[index].slots[replace_idx].tag = tag;
        sets[index].slots[replace_idx].load_ts = ts;
        sets[index].slots[replace_idx].access_ts = ts;
        sets[index].slots[replace_idx].dirty = false;
        ts++;

        total_cycles += 1;

        if (type == 's') {
          if (write_policy == "write-through") {
            total_cycles += 100;
          } else {
            sets[index].slots[replace_idx].dirty = true;
          }
        }
      }
    }
  }

  void print_stats() const {
    std::cout << "Total loads: " << total_loads << "\n";
    std::cout << "Total stores: " << total_stores << "\n";
    std::cout << "Load hits: " << load_hits << "\n";
    std::cout << "Load misses: " << load_misses << "\n";
    std::cout << "Store hits: " << store_hits << "\n";
    std::cout << "Store misses: " << store_misses << "\n";
    std::cout << "Total cycles: " << total_cycles << "\n";
  }
};

bool is_power_of_two(uint32_t n) { return n > 0 && (n & (n - 1)) == 0; }

int main(int argc, char **argv) {
  if (argc != 7) {
    std::cerr << "Usage: ./csim <sets> <blocks> <bytes> "
                 "<write-allocate|no-write-allocate> "
                 "<write-through|write-back> <lru|fifo>\n";
    return 1;
  }

  uint32_t num_sets, num_blocks, num_bytes;
  try {
    num_sets = std::stoul(argv[1]);
    num_blocks = std::stoul(argv[2]);
    num_bytes = std::stoul(argv[3]);
  } catch (...) {
    std::cerr << "Invalid numeric arguments\n";
    return 1;
  }

  std::string write_alloc = argv[4];
  std::string write_policy = argv[5];
  std::string eviction = argv[6];

  if (!is_power_of_two(num_sets)) {
    std::cerr << "Invalid number of sets\n";
    return 1;
  }
  if (!is_power_of_two(num_blocks)) {
    std::cerr << "Invalid number of blocks\n";
    return 1;
  }
  if (num_bytes < 4 || !is_power_of_two(num_bytes)) {
    std::cerr << "Invalid block size\n";
    return 1;
  }
  if (write_alloc != "write-allocate" && write_alloc != "no-write-allocate") {
    std::cerr << "Invalid write-allocate parameter\n";
    return 1;
  }
  if (write_policy != "write-through" && write_policy != "write-back") {
    std::cerr << "Invalid write-through/write-back parameter\n";
    return 1;
  }
  if (eviction != "lru" && eviction != "fifo") {
    std::cerr << "Invalid eviction parameter\n";
    return 1;
  }
  if (write_policy == "write-back" && write_alloc == "no-write-allocate") {
    std::cerr << "Cannot have write-back and no-write-allocate\n";
    return 1;
  }

  CacheSimulator simulator(num_sets, num_blocks, num_bytes, write_alloc,
                           write_policy, eviction);

  char type;
  std::string address;
  int ignore;
  while (std::cin >> type >> address >> ignore) {
    if (type != 'l' && type != 's')
      continue;
    uint32_t addr = 0;
    try {
      addr = std::stoul(address, nullptr, 16);
    } catch (...) {
      continue;
    }
    simulator.process_access(type, addr);
  }

  simulator.print_stats();
  return 0;
}