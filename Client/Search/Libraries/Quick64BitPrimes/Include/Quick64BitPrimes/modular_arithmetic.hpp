#ifndef QUICK_64_BIT_PRIMES_MODULAR_ARITHMETIC_HPP
#define QUICK_64_BIT_PRIMES_MODULAR_ARITHMETIC_HPP

#include "Quick64BitPrimes/types.hpp"

namespace q64bp {

    // ============================================================================================
    // Modular addition
    // ============================================================================================
    ui64 modular_addition(
        ui64 addend1,
        ui64 addend2,
        ui64 modulus
    );

    // ============================================================================================
    // Modular multiplication
    // ============================================================================================
    ui64 modular_multiplication(
        ui64 factor1,
        ui64 factor2,
        ui64 modulus
    );

    // ============================================================================================
    // Modular exponentiation
    // ============================================================================================
    ui64 modular_exponentiation(
        ui64 base,
        ui64 exponent,
        ui64 modulus
    );

}

#endif