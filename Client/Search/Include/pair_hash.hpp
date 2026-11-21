#ifndef PARKER2_PAIR_HASH_HPP
#define PARKER2_PAIR_HASH_HPP

#include <cstddef>
#include <utility>
#include <functional>

// ================================================================================================
// Pair hashing function
// ================================================================================================
struct PairHash {

    // Customize the "()" operator
    template <typename Type1, typename Type2>
    std::size_t operator()(const std::pair<Type1, Type2>& pair) const noexcept {

        // Hash each value of the pair
        std::size_t hash_1 = std::hash<Type1>{}(pair.first);
        std::size_t hash_2 = std::hash<Type2>{}(pair.second);

        // Return the combined hash
        return hash_1 ^ (hash_2 << 1);

    }

};

#endif