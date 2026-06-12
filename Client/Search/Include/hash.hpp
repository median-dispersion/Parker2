#ifndef PARKER2_HASH_HPP
#define PARKER2_HASH_HPP

#include <cstddef>
#include <utility>
#include "types.hpp"
#include <functional>

// ================================================================================================
// Custom specialization for hashing unsigned 128-bit integers
// ================================================================================================
template<>
struct std::hash<ui128> {

    // Customize the "()" operator
    std::size_t operator()(const ui128& value) const noexcept {

        // Split the unsigned 128-bit integer into two parts
        ui64 low = static_cast<ui64>(value);
        ui64 high = static_cast<ui64>(value >> 64);

        // Hash each part of the value
        std::size_t hash_1 = std::hash<ui64>{}(low);
        std::size_t hash_2 = std::hash<ui64>{}(high);

        // Return the combined hash
        return hash_1 ^ (hash_2 << 1);

    }

};

// ================================================================================================
// Templated pair hashing function
// ================================================================================================
template <typename Type>
struct PairHash {

    // Customize the "()" operator
    std::size_t operator()(const std::pair<Type, Type>& pair) const noexcept {

        // Hash each value of the pair
        std::size_t hash_1 = std::hash<Type>{}(pair.first);
        std::size_t hash_2 = std::hash<Type>{}(pair.second);

        // Return the combined hash
        return hash_1 ^ (hash_2 << 1);

    }

};

#endif