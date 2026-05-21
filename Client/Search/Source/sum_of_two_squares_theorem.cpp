#include "sum_of_two_squares_theorem.hpp"
#include "types.hpp"
#include <vector>
#include "Quick64BitPrimes/types.hpp"

// ================================================================================================
// Use the sum of two squares theorem to count the number of uniques ways an integer can be represented as the sum of two squares
// Based on the prime factorization of that integer as long as all factors are in the form factor ≡ 1 (mod 4)
// ================================================================================================
ui64 sum_of_two_squares_count(const std::vector<q64bp::PrimeFactor>& prime_factors) {

    // All prime factors passed to this function must be in the form factor ≡ 1 (mod 4)
    // Otherwise the result will be incorrect!

    // This function is safe for all unsigned 64 bit integers that meet the input criteria
    // An unsigned 64 bit integer can have at most 15 prime factors
    // Because the first 16 primes multiplied together would overflow the unsigned 64 bit integer range
    // For prime factors in the form factor ≡ 1 (mod 4) this number will be even less
    // 15 prime factors with an exponent of 2 would result in a maximum number of solution of 57'395'628
    // 57'395'628 < 2⁶⁴-1

    // Initialize the number of solutions to the sum of two squares theorem
    ui64 solutions = 4;

    // Loop through all prime factors
    for (const q64bp::PrimeFactor& prime_factor : prime_factors) {

        // Update the number of solutions to the sum of two squares theorem
        solutions *= prime_factor.exponent + 1;

    }

    // Compensate for unique ordering and negative solutions
    // Return the number of unique solutions
    return solutions / 8;

}