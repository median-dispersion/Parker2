#ifndef QUICK_64_BIT_PRIMES_MILLER_RABIN_PRIMALITY_TEST_HPP
#define QUICK_64_BIT_PRIMES_MILLER_RABIN_PRIMALITY_TEST_HPP

#include "Quick64BitPrimes/types.hpp"

namespace q64bp {

    // ============================================================================================
    // Check if a number is prime using the Miller-Rabin primality test
    // ============================================================================================
    bool miller_rabin_primality_test(ui64 number);

}

#endif