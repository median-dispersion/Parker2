#ifndef QUICK_64_BIT_PRIMES_FERMAT_SUM_OF_TWO_SQUARES_THEOREM
#define QUICK_64_BIT_PRIMES_FERMAT_SUM_OF_TWO_SQUARES_THEOREM

#include "Quick64BitPrimes/types.hpp"
#include <optional>
#include <utility>

namespace q64bp {

    // ============================================================================================
    // Get Fermat's sum of two squares representation of a prime (x² + y² = p)
    // ============================================================================================
    std::optional<std::pair<ui64, ui64>> fermat_sum_of_two_squares_theorem(ui64 prime);

}

#endif