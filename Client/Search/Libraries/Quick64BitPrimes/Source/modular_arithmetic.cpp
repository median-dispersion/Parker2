#include "Quick64BitPrimes/modular_arithmetic.hpp"
#include "Quick64BitPrimes/types.hpp"
#include <stdexcept>
#include <algorithm>

namespace q64bp {

    // ============================================================================================
    // Modular addition
    // ============================================================================================
    ui64 modular_addition(
        ui64 addend1,
        ui64 addend2,
        ui64 modulus
    ) {

        // Throw an exception if the modulus is zero
        if (modulus == 0) { throw std::invalid_argument("Modulus must be non-zero!"); }

        // Reduce the addends if they exceed the modulus
        if (addend1 >= modulus) { addend1 %= modulus; }
        if (addend2 >= modulus) { addend2 %= modulus; }

        // Check if the addition would exceed the modulus
        if (addend1 >= modulus - addend2) {

            // Use subtraction with is equivalent to (addend1 + addend2) % modulus
            return addend1 - (modulus - addend2);

        // If the addition does not exceed the modulus
        } else {

            // Add the two values directly
            return addend1 + addend2;

        }

    }

    // Check if an unsigned 128 bit integer type is available
    #ifdef QUICK_64_BIT_PRIMES_UI128_AVAILABLE

    // ============================================================================================
    // Modular multiplication using the q64bp::ui128 type
    // ============================================================================================
    ui64 modular_multiplication(
        ui64 factor1,
        ui64 factor2,
        ui64 modulus
    ) {

        // Throw an exception if the modulus is zero
        if (modulus == 0) { throw std::invalid_argument("Modulus must be non-zero!"); }

        // Return the result
        return static_cast<ui128>(factor1) * factor2 % modulus;

    }

    // If the unsigned 128 bit integer type is not available use the fallback option
    // The fallback option is significantly slower!
    #else

    // ============================================================================================
    // Modular multiplication
    // ============================================================================================
    ui64 modular_multiplication(
        ui64 factor1,
        ui64 factor2,
        ui64 modulus
    ) {

        // Throw an exception if the modulus is zero
        if (modulus == 0) { throw std::invalid_argument("Modulus must be non-zero!"); }

        // Initialize the result
        ui64 result = 0;

        // Reduce the factors if they exceed the modulus
        if (factor1 >= modulus) { factor1 %= modulus; }
        if (factor2 >= modulus) { factor2 %= modulus; }

        // Make sure factor2 is the smaller factor to limit the number of addition loops
        if (factor1 < factor2) { std::swap(factor1, factor2); }

        // Loop until the factor2 becomes zero
        // Expanding factor1 * factor2 into factor1 + factor1 + factor1... factor2 times
        while (factor2) {

            // Check if factor2 is odd using a bitwise AND
            if (factor2 & 1) {

                // Use modular addition instead of direct multiplication to prevent overflows
                // Check if the addition would exceed the modulus
                if (result >= modulus - factor1) {

                    // Use subtraction with is equivalent to (result + factor1) % modulus
                    result -= (modulus - factor1);

                // If the addition does not exceed the modulus
                } else {

                    // Add the two values directly
                    result += factor1;

                }

            }

            // Double factor1 using addition
            // Check if the addition would exceed the modulus
            if (factor1 >= modulus - factor1) {

                // Use subtraction with is equivalent to (factor1 + factor1) % modulus
                factor1 -= (modulus - factor1);

            // If the addition does not exceed the modulus
            } else {

                // Add the two values directly
                factor1 += factor1;

            }

            // Divide factor2 by 2 using a right bit shift
            factor2 >>= 1;

        }

        // Return the result
        return result;

    }

    #endif

    // ============================================================================================
    // Modular exponentiation
    // https://en.wikipedia.org/wiki/Modular_exponentiation#Pseudocode
    // ============================================================================================
    ui64 modular_exponentiation(
        ui64 base,
        ui64 exponent,
        ui64 modulus
    ) {

        // Throw an exception if the modulus is zero
        if (modulus == 0) { throw std::invalid_argument("Modulus must be non-zero!"); }

        // If the modulus is one the only possible result is zero
        if (modulus == 1) { return 0; }

        // Initialize the result
        ui64 result = 1;

        // Reduce base if it exceeds the modulus
        if (base >= modulus) { base %= modulus; }

        // Loop until the exponent becomes zero
        // Expanding base^exponent into base * base * base... exponent times
        while (exponent) {

            // Check if the exponent is odd using a bitwise AND
            // Multiply the result by the base mod modulus
            if (exponent & 1) { result = modular_multiplication(result, base, modulus); }

            // Square the base mod modulus
            base = modular_multiplication(base, base, modulus);

            // Divide the exponent by 2 using a right bit shift
            exponent >>= 1;

        }

        // Return the result
        return result;

    }

}