#include "types.hpp"
#include <string>
#include "Quick64BitPrimes/Quick64BitPrimes.hpp" // Modified from https://github.com/median-dispersion/Quick-64-Bit-Primes

// ================================================================================================
// Main
// ================================================================================================
int main(int, char *argv[]) {

    // Get the start and end index of the search range
    // Maximum value for e = 2⁶⁴-1
    ui64 start_index = std::stoull(argv[1]);
    ui64 end_index = std::stoull(argv[2]);

    // Make sure the start index is at least 5
    if (start_index < 5) { start_index = 5; }

    // Make sure the start index is in the form start_index ≡ 1 (mod 4)
    // If it is not increase the start index to the next value that is in the form 1 (mod 4)
    // Maximum value for e = 2⁶⁴-4
    start_index += (1 - start_index % 4 + 4) % 4;

    // Loop through every value in the search range where e ≡ 1 (mod 4)
    for (ui64 e = start_index; e < end_index; e += 4) {

        // If e is a prime continue with the next value of e
        // A prime can not be represented as a sum of two squares in at least four unique ways
        // Maximum value for e = 2⁶⁴-1
        if (q64bp::miller_rabin_primality_test(e)) { continue; }

        // Get all prime factors of e² that are in the from factor ≡ 1 (mod 4)
        // If e² contains any factors in the form factor ≡ 3 (mod 4) the magic square would be reducible
        // In that case no valid prime factors are returned and this value of e will be skipped
        // Maximum value for e = 2⁶⁴-1
        std::vector<q64bp::PrimeFactor> prime_factors = q64bp::squared_prime_decomposition_1mod4(e);

        // If no valid prime factors where found continue with the next value of e
        if (prime_factors.empty()) { continue; }

    }

    // Exit cleanly
    return 0;

}