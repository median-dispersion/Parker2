#ifndef QUICK_64_BIT_PRIMES_PRIME_DECOMPOSITION_HPP
#define QUICK_64_BIT_PRIMES_PRIME_DECOMPOSITION_HPP

#include "Quick64BitPrimes/types.hpp"
#include <vector>

namespace q64bp {

    // ============================================================================================
    // Pretend that the input number is squared
    // Decompose the number into its prime factors
    // But only if all prime factors are in the form p ≡ 1 (mod 4)
    // ============================================================================================
    std::vector<PrimeFactor> squared_prime_decomposition_1mod4(ui64 number);

}

#endif