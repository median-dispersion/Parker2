#include "types.hpp"
#include <string>
#include "Quick64BitPrimes/Quick64BitPrimes.hpp" // Modified from https://github.com/median-dispersion/Quick-64-Bit-Primes
#include <vector>
#include "sum_of_two_squares_theorem.hpp"
#include <unordered_set>
#include <utility>
#include "pair_hash.hpp"
#include <stdexcept>
#include <algorithm>

int main(int, char *argv[]) {

    // Get the start and end index of the search range
    // Maximum value for e = 2⁶⁴-1
    ui64 start_index = std::stoull(argv[1]);
    ui64 end_index = std::stoull(argv[2]);

    // Make sure the start index is at least 5
    if (start_index < 5) { start_index = 5; }

    // Make sure the start index is in the form start_index ≡ 1 (mod 4)
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

        // Get the number of unique ways e² can be represented as the sum of two squares using the sum of two squares theorem
        // Maximum value for e = 2⁶⁴-1
        ui64 number_of_unique_sum_of_two_squares = sum_of_two_squares_count(prime_factors);

        // If there are less than five unique ways e² can be represented as the sum of two squares
        // Continue with the next value for e
        // Technically only four ways are required, but because e² is a square
        // The sum of two squares representations will contain an additional pair of (0² + e²), witch is a correct representation
        if (number_of_unique_sum_of_two_squares < 5) { continue; }

        // Manually add 2¹ as a prime factor to complete the set of prime factor for 2e²
        prime_factors.emplace_back(2, 1);

        // Get the sum of two squares representations of 2e² as a unordered set of square root pairs
        // It uses the Brahmagupta-Fibonacci identity for this and is NOT safe for all values of e that fit in an unsigned 64 bit integer!
        // View comments in brahmagupta_fibonacci_identity.cpp for more info
        // Maximum value for e = √(((2⁶⁴-1)²)/2)
        std::unordered_set<std::pair<ui64, ui64>, PairHash> unordered_square_root_pairs = sum_of_two_squares_representations(prime_factors);

        // Check if the predicted and actually number of sum of two squares representations match
        // e² and 2e² should have the same number of representations because a prime factor of 2 does not contribute any new representations
        // If the don't match throw an exception
        if (unordered_square_root_pairs.size() != number_of_unique_sum_of_two_squares) { throw std::logic_error("Incorrect number of sum of two squares representations!"); }

        // Convert the unordered set of square root pairs of 2e² into a vector
        std::vector<std::pair<ui64, ui64>> square_root_pairs(unordered_square_root_pairs.begin(), unordered_square_root_pairs.end());

        // Sort the square root pairs of 2e²
        std::sort(square_root_pairs.begin(), square_root_pairs.end());

    }

}