#include "Quick64BitPrimes/tonelli_shanks_algorithm.hpp"
#include "Quick64BitPrimes/types.hpp"
#include "Quick64BitPrimes/modular_arithmetic.hpp"
#include "Quick64BitPrimes/miller_rabin_primality_test.hpp"
#include <optional>
#include <utility>
#include <stdexcept>

namespace q64bp {

    // ============================================================================================
    // Get the square roots of a number modulo a prime using the Tonelli-Shanks algorithm (r² ≡ n (mod p))
    // Based on the GO implementation: https://rosettacode.org/wiki/Tonelli-Shanks_algorithm#Go
    // ============================================================================================
    std::pair<ui64, ui64> tonelli_shanks_algorithm_unsafe(
        ui64 number,
        ui64 prime
    ) {

        // Any input passed to this function must be:
        // number % prime != 0
        // prime == must be prime
        // prime == must be odd
        // Legendre symbol == 1
        // Otherwise it is unsafe to use!
        // These checks are guaranteed by calling this function through tonelli_shanks_algorithm()

        // If the prime is in the form prime ≡ 3 (mod 4) use the fast path
        // Use bitwise tricks to perform the modular operation
        if ((prime & 3) == 3) {

            // Calculate the square root directly
            // Prime + 1 is safe because the largest 64-bit prime + 1 will not overflow
            ui64 square_root = modular_exponentiation(number, (prime + 1) >> 2, prime);

            // Return the result
            return {square_root, prime - square_root};

        }

        // If the prime is in the form prime ≡ 5 (mod 8) use the fast path
        // Use bitwise tricks to perform the modular operation
        if ((prime & 7) == 5) {

            // For the case that prime ≡ 5 (mod 8) there are two different direct calculations

            // Page 11: http://koclab.cs.ucsb.edu/teaching/ecc/eccPapers/Doche-ch11.pdf
            // Cases for prime ≡ 5 (mod 8):
            // n^{(p-1)/4} = 1
            // n^{(p-1)/4} = -1

            // This path always assumes the first case (=1), then calculates the first square root
            // It checks if the square root is valid and if not corrects the result to match the second case
            // After that it returns the valid square roots

            // Calculate the square root directly
            // Prime + 3 is safe because the largest 64-bit prime + 3 will not overflow
            ui64 square_root = modular_exponentiation(number, (prime + 3) >> 3, prime);

            // Check if the square root is in the incorrect form
            if (modular_multiplication(square_root, square_root, prime) != number) {

                // Calculate the correction factor
                ui64 correction = modular_exponentiation(2, (prime - 1) >> 2, prime);

                // Apply the correction factor
                square_root = modular_multiplication(square_root, correction, prime);

            }

            // Return the result
            return {square_root, prime - square_root};

        }

        // Initialize the factor and exponent
        // Writing prime - 1 as factor^exponent
        ui64 factor = prime - 1;
        ui64 exponent = 0;

        // Loop as long as factor is even using a bitwise AND check
        // Factoring out all powers of two from prime - 1
        while (!(factor & 1)) {

            // Divide the factor by 2 using a right bit shift
            factor >>= 1;

            // Increase exponent
            exponent++;

        }

        // Initialize the quadratic non-residue
        ui64 quadratic_non_residue = 2;

        // Find a quadratic non-residue by repeatedly checking if the Legendre symbol is not -1
        // Increasing the quadratic non-residue variable by one each loop and checking again
        // For an odd prime a quadratic non-residue must exist
        // If for whatever reason the quadratic non-residue can't be found, it will only loop up to prime
        while (
            quadratic_non_residue < prime &&
            modular_exponentiation(quadratic_non_residue, (prime - 1) >> 1, prime) != prime - 1
        ) { quadratic_non_residue++; }

        // Check if no quadratic non-residue was found and throw an exception
        // With properly guarded inputs this will never happen and should be mathematically impossible
        if (quadratic_non_residue >= prime) { throw std::logic_error("Invalid quadratic non-residue!"); }

        // Initialize the variables for the Tonelli-Shanks iteration
        ui64 square_root = modular_exponentiation(number, (factor + 1) >> 1, prime);
        ui64 current_factor = modular_exponentiation(quadratic_non_residue, factor, prime);
        ui64 current_residue = modular_exponentiation(number, factor, prime);
        ui64 current_exponent = exponent;

        // Loop until a solution is found
        // With a Legendre symbol of 1 and an odd prime a solution must exist so this will terminate
        while (current_residue != 1) {

            // Initialize variables for exponent search
            ui64 temporary_factor = current_residue;
            ui64 new_exponent = 0;

            // Find the smallest new exponent such that t^(2^i) ≡ 1 (mod p)
            while (temporary_factor != 1 && new_exponent + 1 < current_exponent) {

                temporary_factor = modular_multiplication(temporary_factor, temporary_factor, prime);
                new_exponent++;

            }

            // Check if the Tonelli-Shanks invariant holds, a failure could lead to an infinite loop
            // With properly guarded inputs this will never happen and should be mathematically impossible
            if (new_exponent >= current_exponent) { throw std::logic_error("Invariant failure!"); }

            // Initialize variables for factor search
            // For valid Tonelli-Shanks inputs, current_exponent can never be 0, so no underflow or infinite loop risk
            ui64 temporary_exponent = current_exponent - new_exponent - 1;
            ui64 new_factor = current_factor;

            // Find the new factor such that b = c^(2^(m - i - 1)) mod p
            while (temporary_exponent) {

                new_factor = modular_multiplication(new_factor, new_factor, prime);
                temporary_exponent--;

            }

            // Update variables according to the algorithm
            square_root = modular_multiplication(square_root, new_factor, prime);
            current_factor = modular_multiplication(new_factor, new_factor, prime);
            current_residue = modular_multiplication(current_residue, current_factor, prime);
            current_exponent = new_exponent;

        }

        // Return the result
        return {square_root, prime - square_root};

    }

    // ============================================================================================
    // Get the square roots of a number modulo a prime using the Tonelli-Shanks algorithm (r² ≡ n (mod p))
    // Input validation before the main algorithm
    // ============================================================================================
    std::optional<std::pair<ui64, std::optional<ui64>>> tonelli_shanks_algorithm(
        ui64 number,
        ui64 prime
    ) {

        // If the provided value is not prime return no valid solutions
        if (!miller_rabin_primality_test(prime)) { return {}; }

        // If the prime is two return the trivial solution
        if (prime == 2) { return {{number & 1, {}}}; }

        // If the number exceeds the prime reduce it under modular arithmetic
        if (number >= prime) { number %= prime; }

        // If the number is zero return the trivial solution
        if (number == 0) { return {{0, {}}}; }

        // If the Legendre symbol is not one return no solution
        if (modular_exponentiation(number, (prime - 1) >> 1, prime) != 1) { return {}; }

        // Run the main Tonelli-Shanks algorithm and return the result
        return tonelli_shanks_algorithm_unsafe(number, prime);

    }

}