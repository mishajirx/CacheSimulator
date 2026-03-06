#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

struct Slot {
  uint32_t tag;
  bool valid, dirty;
  uint32_t load_ts, access_ts;
};
struct Set {
  std::vector<Slot> slots;
};
struct Cache {
  std::vector<Set> sets;
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
    // TODO: implement cache logic
    (void)addr;
  }

  return 0;
}
