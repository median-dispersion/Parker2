#ifndef QUICK_64_BIT_PRIMES_TONELLI_SHANKS_ALGORITHM
#define QUICK_64_BIT_PRIMES_TONELLI_SHANKS_ALGORITHM

#include "Quick64BitPrimes/types.hpp"
#include <optional>
#include <utility>

namespace q64bp {

    // ============================================================================================
    // Get the square roots of a number modulo a prime using the Tonelli-Shanks algorithm (r² ≡ n (mod p))
    // ============================================================================================
    std::optional<std::pair<ui64, std::optional<ui64>>> tonelli_shanks_algorithm(
        ui64 number,
        ui64 prime
    );

    // ============================================================================================
    // Unsafe, no input validation, only for internal library use!
    // Get the square roots of a number modulo a prime using the Tonelli-Shanks algorithm (r² ≡ n (mod p))
    // ============================================================================================
    std::pair<ui64, ui64> tonelli_shanks_algorithm_unsafe(
        ui64 number,
        ui64 prime
    );

}

#endif