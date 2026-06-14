#include "types.hpp"
#include <string>
#include "Quick64BitPrimes/Quick64BitPrimes.hpp" // Modified from https://github.com/median-dispersion/Quick-64-Bit-Primes
#include <vector>
#include "sum_of_two_squares_theorem.hpp"
#include <utility>
#include <stdexcept>
#include "helper_functions.hpp"
#include <cstddef>
#include <iostream>

// ================================================================================================
// Search loop
// ================================================================================================
template <typename IntegerType, typename PairType>
void search(
    ui64 start_index,
    ui64 end_index
) {

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
        // When using unsigned 64-bit integers this function is NOT safe for all values of e!
        // For more information view the comments in sum_of_two_squares_theorem.hpp and brahmagupta_fibonacci_identity.hpp
        // However because it is a template function unsigned 128-bit integer can be used making it safe for all values of e
        // Witch integer type is used is decided by the end index of the search range in the main() function
        // Maximum value for e = √(((2⁶⁴-1)²)/2) if using unsigned 64-bit integers
        // Maximum value for e = √(((2¹²⁸-1)²)/2) if using unsigned 128-bit integers
        std::vector<std::pair<PairType, PairType>> square_root_pairs = ordered_unique_sum_of_two_squares_representations<PairType>(prime_factors);

        // Check if the predicted and actually number of sum of two squares representations match
        // e² and 2e² should have the same number of representations because a prime factor of 2 does not contribute any new representations
        // With the exception that list will contain one less representation because one of the pairs is made up of duplicate values
        // This is why it compares against number_of_unique_sum_of_two_squares - 1
        // See sum_of_two_squares_theorem.hpp for more info about this
        // If the don't match throw an exception
        if (square_root_pairs.size() != number_of_unique_sum_of_two_squares - 1) { throw std::logic_error("Incorrect number of sum of two squares representations!"); }

        // Calculate e² directly
        // Casting it into a wide enough integer type to perfrom all calculations safely
        IntegerType e_squared = integer_cast<IntegerType>(e) * e;

        // Calculate the magic sum, i.e. 3e²
        IntegerType magic_sum = 3 * e_squared;

        // Loop through all possible combinations of square root pair positions
        // Each pair must be placed so that its values surround the center value e
        // Rotations and mirrors of magic squares can be excluded by positioning the pairs based on their size
        // For example the pair with the smallest value will always be placed in the center column
        // With its smaller value at the bottom and its larger value at the top
        // Once the first three pairs have be positioned and verified that they all sum up to 3e²
        // The top and bottom row can be tested and checked if they also add up to the magic sum
        // If they do, the last pair can be determined and also checked against the magic sum
        // If all row, columns and diagonals sum up to 3e² a valid magic square of squares has been constructed!
        for (std::size_t pair_1 = 0; pair_1 < square_root_pairs.size() - 3; ++pair_1) {
            for (std::size_t pair_2 = pair_1 + 1; pair_2 < square_root_pairs.size() - 2; ++pair_2) {
                for (std::size_t pair_4 = pair_2 + 2; pair_4 < square_root_pairs.size(); ++pair_4) {

                    // Cast the pair values into a wide enough integer type to perfrom calculations safely
                    // This also gives them their appropriate variable names
                    IntegerType a = integer_cast<IntegerType>(square_root_pairs[pair_2].first);
                    IntegerType b = integer_cast<IntegerType>(square_root_pairs[pair_1].second);
                    IntegerType c = integer_cast<IntegerType>(square_root_pairs[pair_4].first);
                    IntegerType g = integer_cast<IntegerType>(square_root_pairs[pair_4].second);
                    IntegerType h = integer_cast<IntegerType>(square_root_pairs[pair_1].first);
                    IntegerType i = integer_cast<IntegerType>(square_root_pairs[pair_2].second);

                    // Square the magic square values
                    IntegerType a_squared = a * a;
                    IntegerType b_squared = b * b;
                    IntegerType c_squared = c * c;
                    IntegerType g_squared = g * g;
                    IntegerType h_squared = h * h;
                    IntegerType i_squared = i * i;

                    // Calculate the sum of the center column and both diagonals of the magic
                    // All sums must be exactly 3e², i.e. the magic sum
                    IntegerType column_2 = b_squared + e_squared + h_squared;
                    IntegerType diagonal_1 = a_squared + e_squared + i_squared;
                    IntegerType diagonal_2 = c_squared + e_squared + g_squared;

                    // Throw an exception if the sums are not equal to the magic sum
                    // This means that the sum of two squares representation failed and returned an incorrect result
                    // This should never be the case unless there is a mistake in the implementation
                    // This is a guard against implementation mistakes and prevents silent overflow errors
                    if (column_2 != magic_sum || diagonal_1 != magic_sum || diagonal_2 != magic_sum) {
                        throw std::logic_error("Incorrect magic sum!");
                    }

                    // Calculate the sum of the top and bottom row of the magic square
                    IntegerType row_1 = a_squared + b_squared + c_squared;
                    IntegerType row_3 = g_squared + h_squared + i_squared;

                    // If the sums are not equal to the magic sum, continue with the next combination of pairs
                    // This is the main validity check for a magic square of squares
                    // In the case this check passes, every other check that follows is also very likely to pass!
                    if (row_1 != magic_sum || row_3 != magic_sum) { continue; }

                    // Loop through all possible combinations fro the last pair
                    for (std::size_t pair_3 = pair_2 + 1; pair_3 < pair_4; ++pair_3) {

                        // Cast the remaining pair values into a wide enough integer type to perfrom calculations safely
                        // This also gives them their appropriate variable names
                        IntegerType d = integer_cast<IntegerType>(square_root_pairs[pair_3].second);
                        IntegerType f = integer_cast<IntegerType>(square_root_pairs[pair_3].first);

                        // Square the remaining magic square values
                        IntegerType d_squared = d * d;
                        IntegerType f_squared = f * f;

                        // Calculate the sum of the center row of the magic square
                        // This sum must be exactly 3e², i.e. the magic sum
                        IntegerType row_2 = d_squared + e_squared + f_squared;

                        // Throw an exception if the sum is not equal to the magic sum
                        // This means that the sum of two squares representation failed and returned an incorrect result
                        // This should never be the case unless there is a mistake in the implementation
                        // This is a guard against implementation mistakes and prevents silent overflow errors
                        if (row_2 != magic_sum) {
                            throw std::logic_error("Incorrect magic sum!");
                        }

                        // Calculate the sum of the left and right column of the magic square
                        IntegerType column_1 = a_squared + d_squared + g_squared;
                        IntegerType column_3 = c_squared + f_squared + i_squared;

                        // If the sums are not equal to the magic sum, continue with the next combination of pairs
                        if (column_1 != magic_sum || column_3 != magic_sum) { continue; }

                        // All checks were passed successfully, and a magic square of squares was found!
                        // Immediately print the valid solution as JSON
                        std::cout<<"{\"type\":\"solution\",\"a\":"<<a<<",\"b\":"<<b<<",\"c\":"<<c<<",\"d\":"<<d<<",\"e\":"<<e<<",\"f\":"<<f<<",\"g\":"<<g<<",\"h\":"<<h<<",\"i\":"<<i<<"}"<<std::endl;

                    }

                }
            }
        }

    }

}

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

    // When the main search loop tries to construct a potential magic square of squares
    // The top and bottom row as well as the left and right column could become as large as 4e² while going through all pair combinations
    // When e is sufficiently large enough, 4e² will overflow an ordinary 64-bit integer
    // Therefore, depending on end index of the search range, i.e. the largest value e can become
    // Different levels of integer precision are chosen to construct the magic square of squares
    // This avoids overflows while keeping performance as fast as possible until more precision is needed
    // IMPORTANT: 4e² was determined experimentally!
    // There might be a chance this is not correct and the actual maximum value might be as large as 5e² or 6e²
    // 6e² is guaranteed to be the limit because any value in the sum of two squares representation can be at most 2e², therfore 3 values x 2e² = 6e²
    // If 4e² is incorrect it will cause silent overflows near the upper unsigned 128-bit integer range before it switches to using GMP
    // However for this to occur the end index of the search range must be close to 2⁶³
    // So when starting a search from 0 this becomes a none issue because of the sheer scale of that number
    // The overflows only become a concern when searching in the range from √((2¹²⁸-1)/4) to √((2¹²⁸-1)/6)
    // For an absolute correctness guarantee when searching in that range
    // A switchover point of √((2¹²⁸-1)/6) instead of √((2¹²⁸-1)/4) can be used to decide when to switch from using unsigned 128-bit integers to using GMP
    // But I'm relatively confident that 4e² is in fact the largest any row or column can become
    // For search ranges below √((2⁶⁴-1)/4) all values of e have been tested
    // And none had any row or columns that summed up to a value larger than 4e²
    // Therefore √((2⁶⁴-1)/4) is safe as the switchover point from using unsigned 64-bit to using unsigned 128-bit or GMP

    // If the search range ends before ~ √((2⁶⁴-1)/4) or 2.147*10⁹ use unsigned 64-bit integers
    if (end_index < 2'147'000'000) {
        search<ui64, ui64>(start_index, end_index);
    }

    // If the search range ends before ~ √((2¹²⁸-1)/4) or 9.223*10¹⁸ use unsigned 128-bit integers
    // But only if unsigned 128-bit integers are available, else switch to GMP directly
    // Also keep using unsigned 64-bit integers for the sum of two squares representations
    #ifdef PARKER2_UI128_AVAILABLE
    else if (end_index < 9'223'000'000'000'000'000) {
        search<ui128, ui64>(start_index, end_index);
    }
    #endif

    // If the end index of the search range is too large for limited integer types
    else {

        // When reaching the upper limits of the unsigend 64-bit integer range
        // Unsigend 64-bit integers are no longer wide enough for all sum of two squares representations of 2e²
        // For more information view the comments in sum_of_two_squares_theorem.hpp and brahmagupta_fibonacci_identity.hpp
        // Therefore an additional switch form using unsigned 64-bit integers to unsigned 128-bit integers is needed
        // This switch only affects the integer types used in the sum of two squares representations
        // And not the ones used in the final magic square construction

        // If the search range ends before ~ √(((2⁶⁴-1)²)/2) or 1.304*10¹⁹
        if (end_index < 13'040'000'000'000'000'000ULL) {

            // Use GMP for the construction of the magic square
            // And use unsigned 64-bit integers for the sum of two squares representations
            search<gmpi, ui64>(start_index, end_index);

        // If the end index of the search range is too large
        // To use unsigned 64-bit integers for the sum of two squares representations
        } else {

            // Use GMP for the construction of the magic square
            // And use unsigned 128-bit integer for the sum of two squares representations
            // But only if unsigned 128-bit integers are available
            // Else throw an exception if the end index of the search range is too large
            #ifdef PARKER2_UI128_AVAILABLE
            search<gmpi, ui128>(start_index, end_index);
            #else
            throw std::invalid_argument("The end index of the search range is too large!");
            #endif

        }

    }

}