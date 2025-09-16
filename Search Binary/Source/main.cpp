#include <cstdint>
#include <string>
#include <vector>
#include <utility>
#include <cmath>

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
// Use the sum of two squares theorem to count the number of unique ways 2E² could be represented as a sum of two squares
// ================================================================================================
uint64_t countUniqueSumOfSquares(const vector<pair<uint64_t, uint64_t>>& primeFactors) {

    // Number of solutions to the sum of two squares theorem
    uint64_t count = 4;

    // For each prime factor and its exponent
    for (auto& [prime, exponent] : primeFactors) {

        // All prime factors of 2E² are proven to be congruent to 1 mod 4
        // No need to check additional constraints of the sum of two squares theorem

        // Update the number of solutions to the sum of two squares theorem
        count *= exponent + 1;

    }

    // Compensate for unique ordering and negative solutions
    count /= 8;

    // Return the number of solutions
    return count;

}

// ================================================================================================
// Direct (brut force) way of searching for all unique pairs of integers that if squared and summed would represent 2E²
// ================================================================================================
vector<pair<uint64_t, uint64_t>> getOrderedUniqueBasePairsDirect(const uint64_t e) {

    // This search function will only work to a value of E < 2147483648
    // Because otherwise 2E² would overflow the maximum value of an unsigned 64 bit integer

    // Search constraints
    // 2E² = X² + Y²
    // X² ≠ Y²
    // X² > 0
    // X² < E²
    // Y² > E²
    // Y² < 2E²

    // List of base pairs
    vector<pair<uint64_t, uint64_t>> basePairs;

    // Target sum is 2E²
    uint64_t targetSum = 2 * e * e;

    // Y² > E² therfore Y > E and Y² < 2E² therfore Y < √2E²
    // Loop through every possible value of Y in decreasing order
    // Doing it in this way will automaticaly sort the pairs from smallest to largest
    for (uint64_t y = sqrt(targetSum); y > e; y--) {

        // Solve for X²
        uint64_t xSquared = targetSum - y * y;

        // Take the root of X² to get X 
        uint64_t x = sqrt(xSquared);

        // Check if X is a perfect square
        if (x * x == xSquared) {

            // Add to the list of base pairs
            basePairs.emplace_back(x, y);

        }

    }

    // Return the list of base pairs
    return basePairs;

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

                // Check if there are at least 4 unique ways to represented 2E² as a sum of two squares
                if(countUniqueSumOfSquares(primeFactors) >= 4) {

                    // Manually add 2¹ as a valid prime factor for 2E²
                    primeFactors.emplace_back(2, 1);

                    // Get all pairs of integers that if squared and summed would represent 2E²
                    vector<pair<uint64_t, uint64_t>> basePairs = getOrderedUniqueBasePairsDirect(e);

                } 

            }

        }

    }

    // Exit
    return 0;

}