#ifndef PARKER2_BRAHMAGUPTA_FIBONACCI_IDENTITY_HPP
#define PARKER2_BRAHMAGUPTA_FIBONACCI_IDENTITY_HPP

#include <unordered_set>
#include <utility>
#include "hash.hpp"
#include <algorithm>

// ================================================================================================
// Brahmagupta-Fibonacci identity
// ================================================================================================
template <typename IntegerType>
std::unordered_set<std::pair<IntegerType, IntegerType>, PairHash<IntegerType>> brahmagupta_fibonacci_identity(
    const std::pair<IntegerType, IntegerType>& square_roots_1,
    const std::pair<IntegerType, IntegerType>& square_roots_2
) {

    // TLDR: When using unsigned 64-bit integers, this function is only safe for values of e up to √(((2⁶⁴-1)²)/2) or ~1.3*10¹⁸ or 13'043'817'825'332'782'211
    // For any value larger than that, unsigned 128-bit integers can be used through the templating option

    // Long explanation:

    // This function is safe for any number that is less or equal to (2⁶⁴-1)²
    // This is because the sum of two squares representation must be made up of square roots of that number
    // Any square root of that number is at most √(2⁶⁴-1)²
    // And √(2⁶⁴-1)² will fit in an unsigned 64-bit integer

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
    // For value of e larger than √(((2⁶⁴-1)²)/2), switching over to using unsigned 128-bit integer is possible through the templating option
    // This makes this function "safe" for all values of e as long as e is less than 2⁶⁴-1

    // An alternative to the Brahmagupta-Fibonacci identity could be achieved using Gaussian integers
    // But that might require singed integer types and therefore is not used

    // Compute the four products (ac, bd, ad, bc)
    IntegerType product_1 = square_roots_1.first * square_roots_2.first;
    IntegerType product_2 = square_roots_1.second * square_roots_2.second;
    IntegerType product_3 = square_roots_1.first * square_roots_2.second;
    IntegerType product_4 = square_roots_1.second * square_roots_2.first;

    // Perform product addition ((ad + bc) & (ac + bd))
    // Perform product subtraction ((ac - bd) & (ad - bc))
    // If the subtraction would underflow, invert it, computing the absolute result
    // This automatically remove negative solutions from the sum of two squares representation
    // For example: 5 = -2² + 1² becomes 5 = 2² + 1²
    IntegerType square_root_1 = product_1 > product_2 ? product_1 - product_2 : product_2 - product_1;
    IntegerType square_root_2 = product_3 + product_4;
    IntegerType square_root_3 = product_1 + product_2;
    IntegerType square_root_4 = product_3 > product_4 ? product_3 - product_4 : product_4 - product_3;

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

#endif