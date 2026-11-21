#include "types.hpp"
#include <string>
#include "Quick64BitPrimes/Quick64BitPrimes.hpp" // Modified from https://github.com/median-dispersion/Quick-64-Bit-Primes
#include <vector>
#include "sum_of_two_squares_theorem.hpp"
#include <unordered_set>
#include <utility>
#include "pair_hash.hpp"
#include <stdexcept>
#include "magic_square_offsets.hpp"
#include "helper_functions.hpp"
#include <iostream>
#include <chrono>
#include <limits>

// ================================================================================================
// Main
// ================================================================================================
int main(int, char *argv[]) {

    // Get the start and end index of the search range
    // Maximum value for e = 2⁶⁴-1
    ui64 start_index = std::stoull(argv[1]);
    ui64 end_index = std::stoull(argv[2]);

    // Set the print style of floating point values to a fixed number of 5 decimal places
    std::cout << std::fixed << std::setprecision(5);

    // Print the JSON initialization message
    std::cout<<"{\"type\":\"initialization\",\"start_index\":"<<start_index<<",\"end_index\":"<<end_index<<"}"<<std::endl;

    // Make sure the start index is at least 5
    if (start_index < 5) { start_index = 5; }

    // Make sure the start index is in the form start_index ≡ 1 (mod 4)
    // If it is not increase the start index to the next value that is in the form 1 (mod 4)
    // Maximum value for e = 2⁶⁴-4
    start_index += (1 - start_index % 4 + 4) % 4;

    // Initialize the number of solutions found in the search range
    ui64 solutions_found = 0;

    // Capture the start time
    auto start_time = std::chrono::steady_clock::now();

    // Initialize the last update time
    auto last_update_time = start_time;

    // Loop through every value in the search range where e ≡ 1 (mod 4)
    for (ui64 e = start_index; e < end_index; e += 4) {

        // Get the current time
        auto current_time = std::chrono::steady_clock::now();

        // Check if the update interval of 60 seconds has been reached
        if (current_time - last_update_time >= std::chrono::seconds(60)) {

            // Set the last update time to the current time
            last_update_time = current_time;

            // Get the current run time in seconds
            fp64 current_runtime_seconds = std::chrono::duration<fp64>(current_time - start_time).count();

            // Print a JSON update message
            std::cout<<"{\"type\":\"update\",\"current_runtime_seconds\":"<<current_runtime_seconds<<",\"current_index\":"<<e<<",\"solutions_found\":"<<solutions_found<<"}"<<std::endl;

        }

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
        // The sum of two squares representations will contain an additional pair of (0² + e²), witch is a correct representation, just not very usefull
        if (number_of_unique_sum_of_two_squares < 5) { continue; }

        // Get all sum of two squares representations of e² based on its prime factors
        // Excluding negative solutions and different ordering
        // Maximum value for e = 2⁶⁴-1
        std::unordered_set<std::pair<ui64, ui64>, PairHash> square_root_pairs = sum_of_two_squares_representations(prime_factors);

        // Check if the predicted and actually number of sum of two squares representations match
        if (square_root_pairs.size() != number_of_unique_sum_of_two_squares) { throw std::logic_error("Incorrect number of sum of two squares representations!"); }

        // Generate an ordered list of offsets (x and y) from the center value e that can be used to construct magic squares
        // Unsigned 128-bit integers must be used for overflow safety because an offset could be as large as e²
        // So for a value of e = 2⁶⁴-1 the offset would be (2⁶⁴-1)², which fits into an unsigned 128-bit integer
        // Technically unsigned 128-bit integer are only needed for values of e > 2³²
        // But that point will be reached so quickly that implementing a templated version seems unecessary
        // Maximum value for e = 2⁶⁴-1
        std::vector<ui128> magic_square_offsets = ordered_magic_square_offsets(square_root_pairs);

        // The list of offsets includes 0 which is a trivial solution that leads to duplicate values
        // Therefore the start index of the offset list is shifted by 1 to exclude the trivial solution
        // Setting this value to 0 will generate working magic square of squares that contain duplicate values
        ui64 y_start = 1;

        // Get the minimum and maximum offset values from the list
        ui128 minimum_offset = magic_square_offsets[y_start];
        ui128 maximum_offset = magic_square_offsets.back();

        // This loop loops through all offsets as x and y where x > y
        // Then check if x + y and x - y are also in the list of offsets
        // If they are a working magic square of squares is found so print the result
        for (ui64 x_index = y_start + 1; x_index < magic_square_offsets.size(); ++x_index) {

            // Get x
            ui128 x = magic_square_offsets[x_index];

            // Define an index for all values that are smaller or equal to x
            ui64 small_index = x_index;

            // Define an index for all values that are larger or equal to x
            ui64 large_index = x_index;

            // Loop through every value of y, where y < x
            for (ui64 y_index = y_start; y_index < x_index; ++y_index) {

                // Get y
                ui128 y = magic_square_offsets[y_index];

                // Calculate the x - y difference
                ui128 difference = x - y;

                // Check if x - y is less than the smallest offset
                // If it is, no larger y value will work so break the loop and continue with the next value for x
                if (difference < minimum_offset) { break; }

                // Check if x + y is more than the largest offset value, in an overflow safe way
                // If it is, no larger y value will work so break the loop and continue with the next value for x
                if (x > maximum_offset - y) { break; }

                // Calculate the x + y sum
                ui128 sum = x + y;

                // Loop through all offsets smaller or equal to x until one matches or falls short of the x - y difference
                while (magic_square_offsets[small_index] > difference) { --small_index; }

                // If the offset falls short of the difference it means that x - y is not in the list of offsets
                // Continue with the next value for y
                if (magic_square_offsets[small_index] != difference) { continue; }

                // Loop through all offsets larger or equal to x until one matches or exceeds the x + y sum
                while (magic_square_offsets[large_index] < sum) { ++large_index; }

                // If the x + y sum is also in the list of offsets a working magic square of squares is found
                if (magic_square_offsets[large_index] == sum) {

                    // Immediately print the center value and working offsets as JSON
                    std::cout<<"{\"type\":\"solution\",\"e\":"<<e<<",\"x\":"<<x<<",\"y\":"<<y<<"}"<<std::endl;

                    // Prevent overflows in the number of found solutions
                    // Finding 2⁶⁴-1 valid solutions in a given search range is EXTREMELY unlikely!
                    // And is indicative an implementation mistake
                    // Throw an exception if the number of found solutions is equal to 2⁶⁴-1
                    if (solutions_found == std::numeric_limits<ui64>::max()) {
                        throw std::overflow_error("Found to many solutions!");
                    }

                    // Increase the number of found solutions by one
                    ++solutions_found;

                }

            }

        }

    }

    // Capture the end time
    auto end_time = std::chrono::steady_clock::now();

    // Get the total runtime time in seconds
    fp64 total_runtime_seconds = std::chrono::duration<fp64>(end_time - start_time).count();

    // Print the final result as a JSON message
    std::cout<<"{\"type\":\"result\",\"total_runtime_seconds\":"<<total_runtime_seconds<<",\"solutions_found\":"<<solutions_found<<"}"<<std::endl;

    // Exit cleanly
    return 0;

}