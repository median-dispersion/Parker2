#ifndef QUICK_64_BIT_PRIMES_MODULAR_ARITHMETIC_HPP
#define QUICK_64_BIT_PRIMES_MODULAR_ARITHMETIC_HPP

#include <cstdint>

namespace q64bp::ModularArithmetic {

    // ============================================================================================
    // Modular addition
    // ============================================================================================
    std::uint_fast64_t addition(
        std::uint_fast64_t addend1,
        std::uint_fast64_t addend2,
        std::uint_fast64_t modulus
    );

    // ============================================================================================
    // Modular multiplication
    // ============================================================================================
    std::uint_fast64_t multiplication(
        std::uint_fast64_t factor1,
        std::uint_fast64_t factor2,
        std::uint_fast64_t modulus
    );

    // ============================================================================================
    // Modular exponentiation
    // ============================================================================================
    std::uint_fast64_t exponentiation(
        std::uint_fast64_t base,
        std::uint_fast64_t exponent,
        std::uint_fast64_t modulus
    );

}

#endif