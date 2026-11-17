#ifndef PARKER2_SUM_OF_TWO_SQUARES_THEOREM
#define PARKER2_SUM_OF_TWO_SQUARES_THEOREM

#include "types.hpp"
#include <vector>
#include "Quick64BitPrimes/types.hpp"

// ================================================================================================
// Use the sum of two squares theorem to count the number of uniques ways an integer can be represented as the sum of two squares
// Based on the prime factorization of that integer as long as all factors are in the form factor ≡ 1 (mod 4)
// ================================================================================================
ui64 sum_of_two_squares_count(const std::vector<q64bp::PrimeFactor>& prime_factors);

#endif