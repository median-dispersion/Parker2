#ifndef PARKER2_SUM_OF_TWO_SQUARES_THEOREM
#define PARKER2_SUM_OF_TWO_SQUARES_THEOREM

#include "types.hpp"
#include <vector>
#include "Quick64BitPrimes/types.hpp"
#include <unordered_set>
#include <utility>
#include "hash.hpp"
#include "Quick64BitPrimes/fermat_sum_of_two_squares_theorem.hpp"
#include "brahmagupta_fibonacci_identity.hpp"
#include <vector>
#include <algorithm>
#include <stdexcept>

// ================================================================================================
// Use the sum of two squares theorem to count the number of uniques ways an integer can be represented as the sum of two squares
// Based on the prime factorization of that integer as long as all factors are in the form factor ≡ 1 (mod 4)
// ================================================================================================
ui64 sum_of_two_squares_count(const std::vector<q64bp::PrimeFactor>& prime_factors);

// ================================================================================================
// Get the sum of two squares representations of a prime factor in its raised form
// ================================================================================================
template <typename IntegerType>
std::unordered_set<std::pair<IntegerType, IntegerType>, PairHash<IntegerType>> prime_factor_sum_of_two_squares_representations(const q64bp::PrimeFactor& prime_factor) {

    // Get the sum of two squares representation of the prime factor in its non raised from
    // For example: 5⁴ -> 5¹ -> 5¹ = 1² + 2²
    std::pair<IntegerType, IntegerType> base_square_root_pair = q64bp::fermat_sum_of_two_squares_theorem(prime_factor.base);

    // Add the first sum of two squares representation to the set of all representations
    std::unordered_set<std::pair<IntegerType, IntegerType>, PairHash<IntegerType>> square_root_pairs = {base_square_root_pair};

    // Loop for the number of times the prime factor is raised to its exponent
    // Starting at 1 because the first sum of two squares representation was already computed in the first step and added
    // This will combine the set of all pairs with the base pair from the first step, prime factor exponent times
    // For example: combine the sum of two squares representation of 5¹ four times -> (1² + 2²) & (1² + 2²) & (1² + 2²) & (1² + 2²)
    // Resulting in the sum of two squares representations of 5⁴
    for (ui64 exponent = 1; exponent < prime_factor.exponent; ++exponent) {

        // Create a temporary new set of square root pairs to not alter the original set while looping through it
        std::unordered_set<std::pair<IntegerType, IntegerType>, PairHash<IntegerType>> new_square_root_pairs;

        // Loop through every pair in the set of all pairs
        // The set contains the sum of two squares representations of the prime factor raised to the current exponent value
        // For example: if exponent = 3, it would contain the sum of two squares representations of 5³
        // Combine every sum of two squares representation of 5³ one more time with the base representation of 5¹ to get the final representations of 5⁴
        for (const std::pair<IntegerType, IntegerType>& square_root_pair : square_root_pairs) {

            // Combine the pair from the set of all pairs with the base pair
            new_square_root_pairs.merge(brahmagupta_fibonacci_identity<IntegerType>(square_root_pair, base_square_root_pair));

        }

        // Set the original set to the new set
        square_root_pairs = new_square_root_pairs;

    }

    // Retrun the sum of two squares representations for the prime factor as a set of square root pairs
    return square_root_pairs;

}

// ================================================================================================
// Get the sum of two squares representations of a number based on its prime factors
// ================================================================================================
template <typename IntegerType>
std::unordered_set<std::pair<IntegerType, IntegerType>, PairHash<IntegerType>> unordered_sum_of_two_squares_representations(const std::vector<q64bp::PrimeFactor>& prime_factors) {

    // This function has 3 main loops, the outer one that loops through every prime factor of the number
    // And two inner ones that loop through the sum of two squares representations of the number itself and its prime factors
    // The inner two loops combine all sum of two squares representations with each other
    // For example, in the first iteration of the outer loop, square_root_pairs will contain the sum of two squares representations of the first prime factor
    // It then gets the sum of two squares representations of the second prime factor and combines it with first in the two inner loops
    // After the first iteration, square_root_pairs will contain a combination of the sum of two squares representations of the first and second prime factor
    // In the second iteration of the outer loop it gets the representation of the third prime factor
    // In the two inner loops it once again combines every representation stored in square_root_pairs with the representation of the third prime factor
    // It does this until all prime factor representations have been combined with each other
    // Resulting in the sum of two squares representations of the whole number
    // This process is practically identical to the on in prime_factor_sum_of_two_squares_representations()
    // But for the whole number insted of just a single prime factor

    // Get the sum of two squares representations of the first prime factor
    // Store it in the set of all sum of two squares representations
    std::unordered_set<std::pair<IntegerType, IntegerType>, PairHash<IntegerType>> square_root_pairs = prime_factor_sum_of_two_squares_representations<IntegerType>(prime_factors.front());

    // Loop through every prime factor of the number, starting from the second prime factor
    // This is because the representation of the first prime factor was already computed in the inital step
    for (auto prime_factor = prime_factors.begin() + 1; prime_factor != prime_factors.end(); ++prime_factor) {

        // Get the sum of two squares representations of the current prime factor
        std::unordered_set<std::pair<IntegerType, IntegerType>, PairHash<IntegerType>> prime_factor_square_root_pairs = prime_factor_sum_of_two_squares_representations<IntegerType>(*prime_factor);

        // Create a temporary new set of square root pairs to not alter the original set while looping through it
        std::unordered_set<std::pair<IntegerType, IntegerType>, PairHash<IntegerType>> new_square_root_pairs;

        // Loop through every square root pair in sum of two squares representations of the number
        for (const std::pair<IntegerType, IntegerType>& square_root_pair : square_root_pairs) {

            // Loop through every square root pair in sum of two squares representations of the prime factor
            for (const std::pair<IntegerType, IntegerType>& prime_factor_square_root_pair : prime_factor_square_root_pairs) {

                // Combine the pair from the set of all pairs with the prime factor pair
                new_square_root_pairs.merge(brahmagupta_fibonacci_identity<IntegerType>(square_root_pair, prime_factor_square_root_pair));

            }

        }

        // Set the original set to the new set
        square_root_pairs = new_square_root_pairs;

    }

    // Retrun the sum of two squares representations of the number as a set of square root pairs
    return square_root_pairs;

}

// ================================================================================================
// Get all ordered and unique sum of two squares representations of a number based on its prime factors
// ================================================================================================
template <typename IntegerType>
std::vector<std::pair<IntegerType, IntegerType>> ordered_unique_sum_of_two_squares_representations(const std::vector<q64bp::PrimeFactor>& prime_factors) {

    // Get the sum of two squares representations of 2e² as a unordered set of square root pairs, based on the prime factors of 2e²
    // It uses the Brahmagupta-Fibonacci identity for this
    // And is NOT safe for all values of e when using unsigned 64-bit integers!
    // View comments in brahmagupta_fibonacci_identity.hpp for more info
    // Maximum value for e = √(((2⁶⁴-1)²)/2) if using unsigned 64-bit integers
    // Maximum value for e = √(((2¹²⁸-1)²)/2) if using unsigned 128-bit integers
    std::unordered_set<std::pair<IntegerType, IntegerType>, PairHash<IntegerType>> unordered_square_root_pairs = unordered_sum_of_two_squares_representations<IntegerType>(prime_factors);

    // Convert the unordered set of square root pairs of 2e² into a vector
    std::vector<std::pair<IntegerType, IntegerType>> square_root_pairs(unordered_square_root_pairs.begin(), unordered_square_root_pairs.end());

    // Sort the square root pairs of 2e²
    std::sort(square_root_pairs.begin(), square_root_pairs.end());

    // Get a reference to the last element in the list of square root pairs
    // The last pair will contain duplicate values
    // This is because 2e² can be represented as e² + e²
    // But because e² = e² the pair will contain duplicate values
    // This is mathematically sound and a correct sum of two squares representation
    // But for a magic square of squares that should contain no duplication values, not very usefull
    const std::pair<IntegerType, IntegerType>& last_square_root_pair = square_root_pairs.back();

    // Ensure the last pair actually contains duplicate values
    // If the pair contains distinct values something has gone wrong so throw an exception
    if (last_square_root_pair.first != last_square_root_pair.second) { throw std::logic_error("Square root pair contains distinct values!"); }

    // Remove the pair of duplicate values from the list of square root pairs
    square_root_pairs.pop_back();

    // Return the ordered and unique sum of two squares respresentations as a list of square root pairs
    return square_root_pairs;

}

#endif