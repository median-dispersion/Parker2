#include "brahmagupta_fibonacci_identity.hpp"
#include <unordered_set>
#include <utility>
#include "types.hpp"
#include "pair_hash.hpp"
#include <algorithm>

// ================================================================================================
// Brahmagupta-Fibonacci identity
// ================================================================================================
std::unordered_set<std::pair<ui64, ui64>, PairHash> brahmagupta_fibonacci_identity(
    const std::pair<ui64, ui64>& square_roots_1,
    const std::pair<ui64, ui64>& square_roots_2
) {

    // This function is safe for any number that is less or equal to (2⁶⁴-1)²
    // This is because the sum of two squares representation must be made up of square roots of that number
    // Any square root of that number is at most √(2⁶⁴-1)²
    // And √(2⁶⁴-1)² will fit in an unsigned 64-bit integer

    // Compute the four products (ac, bd, ad, bc)
    ui64 product_1 = square_roots_1.first * square_roots_2.first;
    ui64 product_2 = square_roots_1.second * square_roots_2.second;
    ui64 product_3 = square_roots_1.first * square_roots_2.second;
    ui64 product_4 = square_roots_1.second * square_roots_2.first;

    // Perform product addition ((ad + bc) & (ac + bd))
    // Perform product subtraction ((ac - bd) & (ad - bc))
    // If the subtraction would underflow, invert it, computing the absolute result
    // This automatically remove negative solutions from the sum of two squares representation
    // For example: 5 = -2² + 1² becomes 5 = 2² + 1²
    ui64 square_root_1 = product_1 > product_2 ? product_1 - product_2 : product_2 - product_1;
    ui64 square_root_2 = product_3 + product_4;
    ui64 square_root_3 = product_1 + product_2;
    ui64 square_root_4 = product_3 > product_4 ? product_3 - product_4 : product_4 - product_3;

    // Ensure uniqueness of the sum of two squares representation
    // By making sure the first square root in each pair is always smaller than the second square root
    // For example: 5 = 2² + 1² becomes 5 = 1² + 2²
    if (square_root_1 > square_root_2) { std::swap(square_root_1, square_root_2); }
    if (square_root_3 > square_root_4) { std::swap(square_root_3, square_root_4); }

    // Retrun the sum of two squares representation as a set of two pairs of square roots
    // If the pairs are identical the set will only contain one pair
    // This automatically deduplicates the sum of two squares representation
    return {{square_root_1, square_root_2}, {square_root_3, square_root_4}};

}