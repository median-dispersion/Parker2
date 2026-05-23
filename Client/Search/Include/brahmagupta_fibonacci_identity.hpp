#ifndef PARKER2_BRAHMAGUPTA_FIBONACCI_IDENTITY_HPP
#define PARKER2_BRAHMAGUPTA_FIBONACCI_IDENTITY_HPP

#include <unordered_set>
#include <utility>
#include "types.hpp"
#include "pair_hash.hpp"

// ================================================================================================
// Brahmagupta-Fibonacci identity
// ================================================================================================
std::unordered_set<std::pair<ui64, ui64>, PairHash> brahmagupta_fibonacci_identity(
    const std::pair<ui64, ui64>& square_roots_1,
    const std::pair<ui64, ui64>& square_roots_2
);

#endif