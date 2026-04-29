#include <cstdint>
#include <string>
#include "Quick64BitPrimes.hpp" // Modified from https://github.com/median-dispersion/Quick-64-Bit-Primes
#include <vector>

// ================================================================================================
// Main
// ================================================================================================
int main(int, char *argv[]) {

    // Get the start and end index of the search range
    // Maximum value for e = 2⁶⁴-1
    std::uint_fast64_t startIndex = std::stoull(argv[1]);
    std::uint_fast64_t endIndex = std::stoull(argv[2]);

    // Make sure the start index is startIndex ≡ 1 (mod 4)
    // Maximum value for e = 2⁶⁴-4
    startIndex += (1 - startIndex % 4 + 4) % 4;

    // Loop through every value in the search range where e ≡ 1 (mod 4)
    for (std::uint_fast64_t e = startIndex; e < endIndex; e += 4) {

        // If e is a prime continue with the next value of e
        // A prime can not be represented as a sum of two squares in at least four unique ways
        // Maximum value for e = 2⁶⁴-1
        if (q64bp::millerRabinPrimalityTest(e)) { continue; }

        // Get all prime factors of e² that are in the from factor ≡ 1 (mod 4)
        // If e² contains any factors in the form factor ≡ 3 (mod 4) the magic square would be reducible
        // In that case no valid prime factors are returned and this value of e will be skipped
        // Maximum value for e = 2⁶⁴-1
        std::vector<q64bp::PrimeFactor> primeFactors = q64bp::squaredPrimeDecomposition1mod4(e);

        // If no valid prime factors where found continue with the next value of e
        if (primeFactors.empty()) { continue; }

    }

    // Exit
    return 0;

}