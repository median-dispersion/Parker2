#include "PrimeDecomposition.h"

using namespace std;

// ================================================================================================
// Get all prime factors of e² using trial division
// ================================================================================================
vector<pair<uint_fast64_t, uint_fast64_t>> squaredTrialDivision1mod4(uint_fast64_t e) {

    // This function will get all prime factors and their exponents for the squared value of e i.e. e² using trial division
    // But only if the prime factor itself is primeFactor ≡ 1 (mod 4) else no prime factors will be returned

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