#include "types.hpp"
#include <string>
#include "Quick64BitPrimes/Quick64BitPrimes.hpp" // Modified from https://github.com/median-dispersion/Quick-64-Bit-Primes
#include <vector>
#include "sum_of_two_squares_theorem.hpp"
#include <utility>
#include <stdexcept>

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

        // Get all ordered and unique sum of two squares representations of 2e² as a list of square root pairs
        std::vector<std::pair<ui64, ui64>> square_root_pairs = ordered_unique_sum_of_two_squares_representations<ui64>(prime_factors);

        // Check if the predicted and actually number of sum of two squares representations match
        // e² and 2e² should have the same number of representations because a prime factor of 2 does not contribute any new representations
        // With the exception that list will contain one less representation because one of the pairs is made up of duplicate values
        // This is why it compares against number_of_unique_sum_of_two_squares - 1
        // See sum_of_two_squares_theorem.hpp for more info about this
        // If the don't match throw an exception
        if (square_root_pairs.size() != number_of_unique_sum_of_two_squares - 1) { throw std::logic_error("Incorrect number of sum of two squares representations!"); }

    }

}