#ifndef QUICK_64_BIT_PRIMES_PRIME_DECOMPOSITION_HPP
#define QUICK_64_BIT_PRIMES_PRIME_DECOMPOSITION_HPP

#include "Quick64BitPrimes/types.hpp"
#include <vector>

namespace q64bp {

    // ============================================================================================
    // Decompose a number into its prime factors
    // ============================================================================================
    std::vector<PrimeFactor> squared_prime_decomposition_1mod4(ui64 number);

}

#endif