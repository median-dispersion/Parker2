#include "sum_of_two_squares_theorem.hpp"
#include "types.hpp"
#include <vector>
#include "Quick64BitPrimes/types.hpp"
#include <unordered_set>
#include <utility>
#include "pair_hash.hpp"
#include "Quick64BitPrimes/fermat_sum_of_two_squares_theorem.hpp"
#include "brahmagupta_fibonacci_identity.hpp"
#include <iterator>

// ================================================================================================
// Use the sum of two squares theorem to count the number of uniques ways an integer can be represented as the sum of two squares
// Based on the prime factorization of that integer as long as all factors are in the form factor ≡ 1 (mod 4)
// ================================================================================================
ui64 sum_of_two_squares_count(const std::vector<q64bp::PrimeFactor>& prime_factors) {

    // All prime factors passed to this function must be in the form factor ≡ 1 (mod 4)
    // Otherwise the result will be incorrect!

    // This function is safe for all unsigned 64 bit integers that meet the input criteria
    // An unsigned 64 bit integer can have at most 15 prime factors
    // Because the first 16 primes multiplied together would overflow the unsigned 64 bit integer range
    // For prime factors in the form factor ≡ 1 (mod 4) this number will be even less
    // 15 prime factors with an exponent of 2 would result in a maximum number of solution of 57'395'628
    // 57'395'628 < 2⁶⁴-1

    // Initialize the number of solutions to the sum of two squares theorem
    ui64 solutions = 4;

    // Loop through all prime factors
    for (const q64bp::PrimeFactor& prime_factor : prime_factors) {

        // Update the number of solutions to the sum of two squares theorem
        solutions *= prime_factor.exponent + 1;

    }

    // Return the number of solutions
    // Divide by 8 using bit shifts to compensate for unique ordering and negative solutions
    // Add one to compensate for squareness, this only applies because its e² and not just e!
    return (solutions >> 3) + 1;

}

// ================================================================================================
// Get the sum of two squares representations of a prime factor in its raised form
// ================================================================================================
std::unordered_set<std::pair<ui64, ui64>, PairHash> prime_factor_sum_of_two_squares_representations(const q64bp::PrimeFactor& prime_factor) {

    // Get the sum of two squares representation of the prime factor in its non raised from
    // For example: 5⁴ -> 5¹ -> 5¹ = 1² + 2²
    std::pair<ui64, ui64> base_square_root_pair = q64bp::fermat_sum_of_two_squares_theorem(prime_factor.base);

    // Add the first sum of two squares representation to the set of all representations
    std::unordered_set<std::pair<ui64, ui64>, PairHash> square_root_pairs = {base_square_root_pair};

    // Loop for the number of times the prime factor is raised to its exponent
    // Starting at 1 because the first sum of two squares representation was already computed in the first step and added
    // This will combine the set of all pairs with the base pair from the first step, prime factor exponent times
    // For example: combine the sum of two squares representation of 5¹ four times -> (1² + 2²) & (1² + 2²) & (1² + 2²) & (1² + 2²)
    // Resulting in the sum of two squares representations of 5⁴
    for (ui64 exponent = 1; exponent < prime_factor.exponent; ++exponent) {

        // Create a temporary new set of square root pairs to not alter the original set while looping through it
        std::unordered_set<std::pair<ui64, ui64>, PairHash> new_square_root_pairs;

        // Loop through every pair in the set of all pairs
        // The set contains the sum of two squares representations of the prime factor raised to the current exponent value
        // For example: if exponent = 3, it would contain the sum of two squares representations of 5³
        // Combine every sum of two squares representation of 5³ one more time with the base representation of 5¹ to get the final representations of 5⁴
        for (const std::pair<ui64, ui64>& square_root_pair : square_root_pairs) {

            // Combine the pair from the set of all pairs with the base pair
            new_square_root_pairs.merge(brahmagupta_fibonacci_identity(square_root_pair, base_square_root_pair));

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
std::unordered_set<std::pair<ui64, ui64>, PairHash> sum_of_two_squares_representations(const std::vector<q64bp::PrimeFactor>& prime_factors) {

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
    std::unordered_set<std::pair<ui64, ui64>, PairHash> square_root_pairs = prime_factor_sum_of_two_squares_representations(prime_factors.front());

    // Loop through every prime factor of the number, starting from the second prime factor
    // This is because the representation of the first prime factor was already computed in the inital step
    for (auto prime_factor = std::next(prime_factors.begin()); prime_factor != prime_factors.end(); ++prime_factor) {

        // Get the sum of two squares representations of the current prime factor
        std::unordered_set<std::pair<ui64, ui64>, PairHash> prime_factor_square_root_pairs = prime_factor_sum_of_two_squares_representations(*prime_factor);

        // Create a temporary new set of square root pairs to not alter the original set while looping through it
        std::unordered_set<std::pair<ui64, ui64>, PairHash> new_square_root_pairs;

        // Loop through every square root pair in sum of two squares representations of the number
        for (const std::pair<ui64, ui64>& square_root_pair : square_root_pairs) {

            // Loop through every square root pair in sum of two squares representations of the prime factor
            for (const std::pair<ui64, ui64>& prime_factor_square_root_pair : prime_factor_square_root_pairs) {

                // Combine the pair from the set of all pairs with the prime factor pair
                new_square_root_pairs.merge(brahmagupta_fibonacci_identity(square_root_pair, prime_factor_square_root_pair));

            }

        }

        // Set the original set to the new set
        square_root_pairs = new_square_root_pairs;

    }

    // Retrun the sum of two squares representations of the number as a set of square root pairs
    return square_root_pairs;

}