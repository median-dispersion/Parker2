#ifndef PARKER2_PAIR_HASH_HPP
#define PARKER2_PAIR_HASH_HPP

#include <cstddef>
#include <utility>
#include "types.hpp"
#include <functional>

// Pair hash struct
struct PairHash {

    // Custom hash operator
    std::size_t operator()(const std::pair<ui64, ui64>& pair) const noexcept {

        // Get the hash of each value in the pair
        std::size_t hash_1 = std::hash<ui64>{}(pair.first);
        std::size_t hash_2 = std::hash<ui64>{}(pair.second);

        // Combine and return hashes
        return hash_1 ^ (hash_2 << 1);

    }

};

#endif