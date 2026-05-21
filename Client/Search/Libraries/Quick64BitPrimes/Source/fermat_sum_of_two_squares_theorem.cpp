#include "Quick64BitPrimes/fermat_sum_of_two_squares_theorem.hpp"
#include "Quick64BitPrimes/types.hpp"
#include "Quick64BitPrimes/miller_rabin_primality_test.hpp"
#include "Quick64BitPrimes/tonelli_shanks_algorithm.hpp"
#include <optional>
#include <utility>

namespace q64bp {

    // ============================================================================================
    // Integer square root floor(sqrt(n))
    // Based on: https://en.wikipedia.org/wiki/Integer_square_root#Using_bitwise_operations
    // ============================================================================================
    ui64 integer_square_root(ui64 number) {

        // Initialize the square root
        ui64 square_root = 0;

        // Start with the highest power of four <= 2⁶⁴
        // 4611686018427387904 == static_cast<std::uint64_t>(1) << 62
        ui64 bit = 4611686018427387904;

        // Reduce the bit until it is the largest power of four <= number.
        while (bit > number) { bit >>= 2; }

        // Loop until all bits have been processed
        while (bit) {

            // Test whether adding this bit would keep the partial square root <= number.
            if (number >= square_root + bit) {

                // Subtract the trial value from the remainder
                number -= square_root + bit;

                // Shift current result down for next stage and add the bit
                square_root = (square_root >> 1) + bit;

            } else {

                // Reject the bit and just shift for next iteration
                square_root >>= 1;

            }

            // Move to the next lower power of four
            bit >>= 2;

        }

        // Return the square root
        return square_root;

    }

    // ============================================================================================
    // Get Fermat's sum of two squares representation of a prime (x² + y² = p)
    // ============================================================================================
    std::optional<std::pair<ui64, ui64>> fermat_sum_of_two_squares_theorem(ui64 prime) {

        // If the provided value is not prime return no valid solutions
        if (!miller_rabin_primality_test(prime)) { return {}; }

        // If the prime is two return the trivial solutions
        if (prime == 2) { return {{1, 1}}; }

        // If the prime in not in the form prime ≡ 1 (mod 4) return no valid solutions
        if ((prime & 3) != 1) { return {}; }

        // Set x to the prime
        ui64 x = prime;

        // Get r² ≡ p-1 (mod p) using Tonelli-Shanks
        // Use the "unsafe" function because at this point the prime is validated to be safe
        // Set y to the first result of the Tonelli-Shanks algorithm
        // For an odd prime in the form prime ≡ 1 (mod 4) at least one result is guaranteed
        ui64 y = tonelli_shanks_algorithm_unsafe(prime - 1, prime).first;

        // Run the Euclidean algorithm until y <= √prime
        while (y > prime / y) {

            // Get the remainder of x divided by y
            ui64 remainder = x % y;

            // Set x to the current divisor
            x = y;

            // Set y to the remainder
            y = remainder;

        }

        // Return the result
        return {{integer_square_root(prime - y * y), y}};

    }

}