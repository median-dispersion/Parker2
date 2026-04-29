#ifndef SUM_OF_TWO_SQUARES_THEOREM_HPP
#define SUM_OF_TWO_SQUARES_THEOREM_HPP

#include <cstdint>
#include <vector>
#include "Quick64BitPrimes.hpp"

// ================================================================================================
// Sum of two squares theorem
// Count the number of uniques ways an integer can be represented as the sum of two squares
// Based on the prime factorization of that integer as long as all factors are in the form factor ≡ 1 (mod 4)
// ================================================================================================
std::uint_fast64_t sumOfTwoSquaresTheorem(const std::vector<q64bp::PrimeFactor>& primeFactors);

#endif