#include "SumOfTwoSquaresTheorem.hpp"
#include <cstdint>
#include <vector>
#include "Quick64BitPrimes.hpp"

// ================================================================================================
// Sum of two squares theorem
// Count the number of uniques ways an integer can be represented as the sum of two squares
// Based on the prime factorization of that integer as long as all factors are in the form factor ≡ 1 (mod 4)
// ================================================================================================
std::uint_fast64_t sumOfTwoSquaresTheorem(const std::vector<q64bp::PrimeFactor>& primeFactors) {

    // All prime factors passed to this function must be in the form factor ≡ 1 (mod 4)
    // Otherwise the result will be incorrect!

    // Initialize the number of solutions to the sum of two squares theorem
    std::uint_fast64_t solutions = 4;

    // Loop through all prime factors
    for (const auto& primeFactor : primeFactors) {

        // Update the number of solutions to the sum of two squares theorem
        solutions *= primeFactor.exponent + 1;

    }

    // Compensate for unique ordering and negative solutions
    // Return the number of unique solutions
    return solutions / 8;

}