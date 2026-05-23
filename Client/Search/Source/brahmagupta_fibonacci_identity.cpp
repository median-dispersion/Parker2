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

    // TLDR: This function is only safe for values of e up to √(((2⁶⁴-1)²)/2) or ~1.3*10¹⁹ or 13'043'817'825'332'782'211

    // This function is safe for any number that can be represented as the sum of two squares up to (2⁶⁴-1)²
    // Because any square root in the sum of two squares representation of the number can at most be √(2⁶⁴-1)²
    // √(2⁶⁴-1)² < 2⁶⁴ and therfore has no risk of overflowing

    // This means:

    // For any prime factor of e² this function is safe!
    // Because the maximum possible prime factor of e² is the largest prime that fits in the unsigned 64 bit integer range
    // That prime must be less than 2⁶⁴-1 and therefore its squared from will also be less than (2⁶⁴-1)²
    // This means that this function will get the correct sum of two squares representation of any prime factor of e²

    // However this function is NOT safe for all sum of two square representations of 2e²!
    // This is because 2e² could be as large as 2*((2⁶⁴-1)²), therfore its square root representation could be as large as √(2*((2⁶⁴-1)²))
    // √(2*((2⁶⁴-1)²)) > √(2⁶⁴-1)² therefore overflows near the upper 64 bit integer range will occur
    // This in turn means that e must be less than √(((2⁶⁴-1)²)/2) for this function to be safe
    // Because if e is √(((2⁶⁴-1)²)/2) then 2e² will be 2*((√(((2⁶⁴-1)²)/2))²) and √(2*((√(((2⁶⁴-1)²)/2))²)) is less than 2⁶⁴

    // Something similar could be achieved using Gaussian integers
    // But that might require singed integer types

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