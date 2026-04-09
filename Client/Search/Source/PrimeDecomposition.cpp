#include "PrimeDecomposition.h"

using namespace std;

// ================================================================================================
// Get all prime factors of e² using trial division
// Maximum input value e = (2³²-1)²
// ================================================================================================
vector<pair<uint_fast64_t, uint_fast64_t>> squaredTrialDivision1mod4(uint_fast64_t e) {

    // This function will get all prime factors and their exponents for the squared value of e i.e. e² using trial division
    // But only if the prime factor itself is primeFactor ≡ 1 (mod 4) else no prime factors will be returned
    // This function only works for values of e = 1 (mod 4)

    // List of all prime factors
    vector<pair<uint_fast64_t, uint_fast64_t>> primeFactors;

    // Loop through every odd number as the base of the prime factor up to the square root of e
    // Maximum value for e = (2³²-1)²
    for (uint_fast64_t base = 3; base <= e / base; base += 2) {

        // Check if e is divisible by the potential prime factor
        if (e % base == 0) {

            // Check if the potential prime factor base ≢ 1 (mod 4)
            if (base % 4 != 1) {

                // Return no valid prime factors for e
                return {};

            }

            // Exponent of the prime factor
            uint_fast64_t exponent = 0;

            // Loop until e is no longer divisible by the prime factor base
            while (e % base == 0) {

                // Divide out the prime factor base from e
                e /= base;

                // Increase the prime factor exponent
                // Increase it in steps of two because at this point e is treated as e²
                // The exponent of a prime factor of e will be twice as big if e gets squared
                exponent += 2;

            }

            // Add the prime factor to the list of all prime factors
            primeFactors.emplace_back(base, exponent);

        }

    }

    // If after the loop e is still larger that 1, then the remaining e itself is a prime
    if (e > 1) {

        // Check if the remaining e ≢ 1 (mod 4)
        if (e % 4 != 1) {

            // Return no valid prime factors for e
            return {};

        }

        // Add the remaining prime factor
        // With an exponent of 2 because at this pint e is treated as e²
        // The exponent of a prime factor of e will be twice as big if e gets squared
        primeFactors.emplace_back(e, 2);

    }

    // Return all prime factors
    return primeFactors;

}

// ================================================================================================
// Modular multiplication using __uint128_t to allow multiplication of two 64-bit integers
// Maximum input values = 2⁶⁴-1
// ================================================================================================
uint_fast64_t modularMultiplication(
    uint_fast64_t factor1,
    uint_fast64_t factor2,
    uint_fast64_t modulus
) {

    return static_cast<__uint128_t>(factor1) * factor2 % modulus;

}

// ================================================================================================
// Modular exponentiation (https://en.wikipedia.org/wiki/Modular_exponentiation#Pseudocode)
// Maximum input values = 2⁶⁴-1
// ================================================================================================
uint_fast64_t modularExponentiation(
    uint_fast64_t base,
    uint_fast64_t exponent,
    uint_fast64_t modulus
) {

    // Initialize result to 1
    uint_fast64_t result = 1;

    // Reduce base to prevent overflows
    base %= modulus;

    // Loop until the exponent becomes zero
    while (exponent > 0) {

        // Check if the exponent is odd using a bitwise AND
        if (exponent & 1) {

            // Multiply the result by the base
            result = modularMultiplication(result, base, modulus);

        }

        // Divide the exponent by 2 using a right bit shift
        exponent >>= 1;

        // Square the base
        base = modularMultiplication(base, base, modulus);

    }

    // Return the result
    return result;

}

// ================================================================================================
// Miller-Rabin Primality test (https://cp-algorithms.com/algebra/primality_tests.html)
// Maximum input value n = 2⁶⁴-1
// ================================================================================================
bool millerRabinPrimalityTest(uint_fast64_t number) {

    // Check if the number is less than 2
    if (number < 2) {

        // No number less than 2 can be prime
        // Return not prime
        return false;

    }

    // Check small primes directly witch is faster than using Miller-Rabin
    // Values from https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test#Testing_against_small_sets_of_bases
    for (uint_fast64_t prime : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}) {

        // Check if the number is divisible by the prime
        if (number % prime == 0) {

            // Return true only if the number itself is the prime
            return number == prime;

        }

    }

    // Initialize the factor and exponent
    uint_fast64_t factor = number - 1;
    uint_fast64_t exponent = 0;

    // Loop as long as factor is even using a bitwise AND check
    while ((factor & 1) == 0) {

        // Divide the factor by 2 using a right bit shift
        factor >>= 1;

        // Increase exponent
        exponent++;

    }

    // Deterministic set of bases that works for all 64-bit integers
    // Values from https://miller-rabin.appspot.com/
    for (uint_fast64_t base : {2, 325, 9375, 28178, 450775, 9780504, 1795265022}) {

        // Check if the base is a multiple of the number
        if (base % number == 0) {

            // Skip this base
            continue;

        }

        // Get a result
        uint_fast64_t result = modularExponentiation(base, factor, number);

        // Check if the result is 1 or number - 1
        if (result == 1 || result == number - 1) {

            // Skip this base
            continue;

        }

        // Flag for checking if the number is a composite
        bool composite = true;

        // Repeat squaring up to exponent - 1 times
        for (uint_fast64_t repeat = 1; repeat < exponent; repeat++) {

            // Square the result using modular multiplication
            result = modularMultiplication(result, result, number);

            // Check if the result is number - 1
            if (result == number - 1) {

                // Set the composite flag to false
                composite = false;

                // Stop the squaring loop immediately
                break;

            }

        }

        // Check if the number is a composite
        if (composite) {

            // Return that the number is not a prime
            return false;

        }

    }

    // Return that the number is a prime
    return true;

}