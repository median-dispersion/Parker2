#include <cstdint>
#include <string>
#include <vector>
#include <utility>
#include "PrimeDecomposition.h"

using namespace std;

// ================================================================================================
// Main
// ================================================================================================
int main(int, char *argv[]) {

    // Get the start and end index of the search range
    // Maximum value for e = 2⁶⁴-1
    uint_fast64_t startIndex = stoull(argv[1]);
    uint_fast64_t endIndex = stoull(argv[2]);

    // Make sure the start index is startIndex ≡ 1 (mod 4)
    // Maximum value for e = 2⁶⁴-4
    startIndex += (1 - startIndex % 4 + 4) % 4;

    // Loop through every value in the search range where e ≡ 1 (mod 4)
    for (uint_fast64_t e = startIndex; e < endIndex; e += 4) {

        // Get all prime factors of e² using trial division
        // Maximum value for e = (2³²-1)²
        vector<pair<uint_fast64_t, uint_fast64_t>> primeFactors = squaredTrialDivision1mod4(e);

        // Check if there are no valid prime factors for e²
        if (primeFactors.empty()) {

            // Skip e
            continue;

        }

    }

    return 0;

}