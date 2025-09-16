#include <cstdint>
#include <string>
#include <vector>
#include <utility>

using namespace std;

// ================================================================================================
// Get all valid (1 mod 4) prime factors for 2E²
// ================================================================================================
vector<pair<uint64_t, uint64_t>> getValidPrimeFactors(uint64_t e) {

    // List of valid prime factors and their exponent as a pair of integers
    vector<pair<uint64_t, uint64_t>> primeFactors;

    // Only odd numbers should be passed to this function
    // So no need to check for a prime factor of 2

    // For every odd factor up to the square root of E
    for (uint64_t factor = 3; factor <= e / factor; factor += 2) {

        // If the factor divides E, then the factor is a prime
        if (e % factor == 0) {

            // If the prime factor is not congruent 1 mod 4, return no valid prime factors
            if (factor % 4 != 1) { return {}; }

            // Exponent of the prime factor
            uint64_t exponent = 0;

            // Loop until E is no longer divisible by the prime factor
            while (e % factor == 0) {

                // Increase the exponent of the factor
                // The exponent is increased in steps of 2 to make it a valid prime factor for 2E²
                exponent += 2;

                // Divide out the prime factor from E
                e /= factor;

            }

            // Add the prime factor and its exponent to the list of prime factors
            primeFactors.emplace_back(factor, exponent);

        }

    }

    // If after the loop E is still larger that 1, then the remaining E is a prime
    if (e > 1) {

        // If the remaining prime factor is not congruent 1 mod 4, return no valid prime factors
        if (e % 4 != 1) { return {}; }

        // Add the remaining E as a prime factor with an exponent of 2 to the list of valid prime factors
        // The exponent is 2 to make it a valid prime factor of 2E²
        primeFactors.emplace_back(e, 2);


    }

    // Return the list of valid prime factors
    return primeFactors;

}

// ================================================================================================
// Main
// ================================================================================================
int main(int, char* launchArguments[]) {

    // Get the start and end index of the search range
    uint64_t startIndex = stoull(launchArguments[1]);
    uint64_t endIndex   = stoull(launchArguments[2]);

    // If the start index is an even number decrease it by one to make it odd
    if (startIndex % 2 == 0) { startIndex--; }

    // For every odd number as E in the search range
    for (uint64_t e = startIndex; e < endIndex; e += 2) {

        // Check if E is congruent to 1 mod 4
        // This is a requirement (but not a guarantee) for all prime factors of 2E² to also be congruent to 1 mod 4
        if (e % 4 == 1) {

            // Get all valid (1 mod 4) prime factors for 2E²
            vector<pair<uint64_t, uint64_t>> primeFactors = getValidPrimeFactors(e);

            // Check if there are any valid prime factors for 2E²
            if (!primeFactors.empty()) {



            }

        }

    }

    // Exit
    return 0;

}