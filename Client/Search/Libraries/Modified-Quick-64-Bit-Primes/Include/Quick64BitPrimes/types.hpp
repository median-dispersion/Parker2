#ifndef QUICK_64_BIT_PRIMES_TYPES_HPP
#define QUICK_64_BIT_PRIMES_TYPES_HPP

#include "../../../../Include/types.hpp"

namespace q64bp {

    // Unsigned 64-bit integer alias
    using ui64 = ui64;

    // Check if the __uint128_t type is available and set its alias
    #define QUICK_64_BIT_PRIMES_UI128_AVAILABLE
    using ui128 = ui128;

    // Prime factor structure
    struct PrimeFactor {

        ui64 base;
        ui64 exponent;

    };

}

#endif