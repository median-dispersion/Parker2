#include "Quick64BitPrimes/miller_rabin_primality_test.hpp"
#include "Quick64BitPrimes/types.hpp"
#include "Quick64BitPrimes/modular_arithmetic.hpp"
#include <initializer_list>

namespace q64bp {

    // ============================================================================================
    // Check if a number is prime using the Miller-Rabin primality test
    // Based on: https://cp-algorithms.com/algebra/primality_tests.html#miller-rabin-primality-test
    // ============================================================================================
    bool miller_rabin_primality_test(ui64 number) {

        // No number less than two can be prime
        if (number < 2) { return false; }

        // Check small primes directly witch is faster than using the Miller-Rabin primality test
        // Values from https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test#Testing_against_small_sets_of_bases
        // These value are technically intended to be used as bases in the Miller-Rabin primality test
        // But they also happen to work great as a quick check for small primes
        for (ui64 prime : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}) {

            // If the number itself is the prime return true
            if (number == prime) { return true; }

            // If the number is divisible by the prime return false
            if (number % prime == 0) { return false; }

        }

        // Initialize the factor and exponent (d & s)
        // Write number - 1 as factor^exponent
        ui64 factor = number - 1;
        ui64 exponent = 0;

        // Loop as long as factor is even using a bitwise AND check
        // Factoring out all powers of two from number - 1
        while (!(factor & 1)) {

            // Divide the factor by 2 using a right bit shift
            factor >>= 1;

            // Increase exponent
            exponent++;

        }

        // Deterministic set of bases that works for all 64-bit integers
        // Values from https://miller-rabin.appspot.com/
        // If none of these bases prove the number is a composite the number must be prime
        for (ui64 base : {2, 325, 9375, 28178, 450775, 9780504, 1795265022}) {

            // If the base is a multiple of the number continue with the next base
            // This is to avoid cases where the modular exponentiation would result in 0 instead of 1 or number - 1
            // In that case it would provide no useful information for detecting primality but also not proving the number composite
            if (base % number == 0) { continue; }

            // Calculate the starting point of the Miller-Rabin primality test
            ui64 result = modular_exponentiation(base, factor, number);

            // If the result is 1 or number - 1, continue with the next base
            // In the case that result is 1, squaring it repeatedly will make it stay 1
            // In the case that result is number - 1, squaring it would make it 1, witch will always stay 1
            // In those scenarios the base can't be used to prove the number is a composite
            // Indicating that it might be prime, so continue the test with the next base
            if (result == 1 || result == number - 1) { continue; }

            // Loop up to exponent - 1 times
            // Or until the result == number - 1
            for (ui64 loop = 1; loop < exponent && result != number - 1; loop++) {

                // Square the result using modular multiplication
                // If the result becomes number - 1, the base cant be used to prove the number is a composite
                // Indicating that it might be prime, so continue the test with the next base
                result = modular_multiplication(result, result, number);

            }

            // If the result is not number - 1, then the number is proven to be a composite, so return false
            // This is because it did not behave like a prime under modular arithmetic eventually becoming number - 1
            if (result != number - 1) { return false; }

        }

        // If no base could prove the number is a composite, the number must be prime
        // Return that the number is a prime
        return true;

    }

}