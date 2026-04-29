#include "Quick64BitPrimes.hpp"
#include <cstdint>
#include "ModularArithmetic.hpp"
#include <vector>
#include <random>
#include <numeric>
#include <algorithm>

namespace q64bp {

    // ============================================================================================
    // Miller-Rabin primality test
    // Based on: https://cp-algorithms.com/algebra/primality_tests.html#miller-rabin-primality-test
    // ============================================================================================
    bool millerRabinPrimalityTest(std::uint_fast64_t number) {

        // No number less than two can be prime
        if (number < 2) { return false; }

        // Check small primes directly witch is faster than using the Miller-Rabin primality test
        // Values from https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test#Testing_against_small_sets_of_bases
        // These value are technically intended to be used as bases in the Miller-Rabin primality test
        // But they also happen to work great as a quick check for small primes
        for (std::uint_fast64_t prime : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}) {

            // If the number itself is the prime return true
            if (number == prime) { return true; }

            // If the number is divisible by the prime return false
            if (number % prime == 0) { return false; }

        }

        // Initialize the factor and exponent (d & s)
        std::uint_fast64_t factor = number - 1;
        std::uint_fast64_t exponent = 0;

        // Loop as long as factor is even using a bitwise AND check
        while (!(factor & 1)) {

            // Divide the factor by 2 using a right bit shift
            factor >>= 1;

            // Increase exponent
            exponent++;

        }

        // Deterministic set of bases that works for all 64-bit integers
        // Values from https://miller-rabin.appspot.com/
        for (std::uint_fast64_t base : {2, 325, 9375, 28178, 450775, 9780504, 1795265022}) {

            // If the base is a multiple of the number continue with the next base
            if (base % number == 0) { continue; }

            // Calculate a result using modular exponentiation
            std::uint_fast64_t result = ModularArithmetic::exponentiation(base, factor, number);

            // If the result is 1 or number - 1 continue with the next base
            if (result == 1 || result == number - 1) { continue; }

            // Loop up to exponent - 1 times
            // Or until the result == number - 1
            for (std::uint_fast64_t loop = 1; loop < exponent && result != number - 1; loop++) {

                // Square the result using modular multiplication
                result = ModularArithmetic::multiplication(result, result, number);

            }

            // If the result is not number - 1 then the number is a composite so return false
            if (result != number - 1) { return false; }

        }

        // Return that the number is a prime
        return true;

    }

    // ============================================================================================
    // Prime decomposition using trial division
    // ============================================================================================
    bool trialDivision(
        std::uint_fast64_t number,
        std::vector<std::uint_fast64_t>& primes
    ) {

        // Loop through every odd factor up to the square root of the number
        for(std::uint_fast64_t factor = 3; factor * factor <= number; factor += 2) {

            // Check if the number is divisible by the factor
            if (number % factor == 0) {

                // If the prime factor is not in the form factor ≡ 1 (mod 4) return no valid prime factors
                if (factor % 4 != 1) { return false; }

                // Loop as long as the number is divisible by the factor
                while (number % factor == 0) {

                    // Divide out the prime factor
                    number /= factor;

                    // Add the prime factor to the list of primes
                    primes.push_back(factor);

                }

            }

        }

        // If the number is still more than one, it is a prime
        if (number > 1) {

            // If the prime factor is not in the form factor ≡ 1 (mod 4) return no valid prime factors
            if (number % 4 != 1) { return false; }

            // Add the prime factor to the list of primes
            primes.push_back(number);

        }

        // Return that all prime factors where valid
        return true;

    }

    // ============================================================================================
    // Polynomial function f(x) = (x² + c) mod m
    // ============================================================================================
    std::uint_fast64_t polynomial(
        std::uint_fast64_t variable,
        std::uint_fast64_t constant,
        std::uint_fast64_t modulus
    ) {
        return ModularArithmetic::addition(ModularArithmetic::multiplication(variable, variable, modulus), constant, modulus);
    }

    // ============================================================================================
    // Integer factorization using Pollard's rho algorithm and Brent's cycle detection method
    // ============================================================================================
    std::uint_fast64_t pollardBrentFactorization(std::uint_fast64_t number) {

        // If the number is divisible by two return a factor of two
        if (!(number & 1)) { return 2; }

        // Initialize the random number generator
        static std::mt19937_64 rng(std::random_device{}());

        // Get a uniform distribution to choose a random starting postion for the variable of the polynomial function
        // The range is 2 to number - 2
        // This is to avoid trivial or degenerate cases
        std::uniform_int_distribution<std::uint_fast64_t> variableDistribution(2, number - 2);

        // Get a uniform distribution to choose a random constant for the polynomial function
        // The range is 1 to number - 1
        // Defined as 1 to number - 2 because number - 2 will later be skipped by adding one
        std::uniform_int_distribution<std::uint_fast64_t> constantDistribution(1, number - 2);

        // Loop until a nontrivial factor is found
        while (true) {

            // Set the tortoise to a random starting position in the allowed range
            std::uint_fast64_t tortoise = variableDistribution(rng);

            // Set the hare to the same starting position as the tortoise
            std::uint_fast64_t hare = tortoise;

            // Set the backup position to the position of the tortoise and hare
            std::uint_fast64_t backup = tortoise;

            // Get a random value in the allowed range for the constant in the polynomial function
            std::uint_fast64_t constant = constantDistribution(rng);

            // Skip constant = number - 2
            // By adding one to the constant
            if (constant == number - 2) { constant++; }

            // Batch size for Brent's optimization (controls how often the greatest common divisor is computed)
            // A value of 128 seems like a good value for all ranges
            std::uint_fast64_t batchSize = 128;

            // Initialize cycle length (doubles each phase)
            std::uint_fast64_t phaseLength = 1;

            // Initialize the product of differences (used for batched greatest common divisor calculations)
            std::uint_fast64_t product = 1;

            // Initialize the factor
            std::uint_fast64_t factor = 1;

            // Loop until a factor is found
            while (factor == 1) {

                // Teleport the tortoise to current hare position (start of new phase)
                tortoise = hare;

                // Advance hare by the phase length (explore sequence)
                for (std::uint_fast64_t index = 0; index < phaseLength; index++) {

                    // Advance the hare position
                    hare = polynomial(hare, constant, number);

                }

                // Track how many steps have been taken
                std::uint_fast64_t step = 0;

                // Process the phase in batches
                while (step < phaseLength && factor == 1) {

                    // Save current hare position in case the fallback is required
                    backup = hare;

                    // Process up to the batch size or the remaining steps in the phase
                    for (std::uint_fast64_t index = 0; index < batchSize && index < phaseLength - step; index++) {

                        // Advance the hare position
                        hare = polynomial(hare, constant, number);

                        // Multiply accumulated product by |tortoise - hare| mod number
                        product = ModularArithmetic::multiplication(
                            product,
                            tortoise < hare ? hare - tortoise : tortoise - hare,
                            number
                        );

                    }

                    // Compute the greatest common divisor of the accumulated product and the number
                    factor = std::gcd(product, number);

                    // Move forward by the batch size
                    step += batchSize;

                }

                // Double the phase length for next iteration using a left bit shift
                phaseLength <<= 1;

            }

            // Check if the found factor is the number itself
            // Do the fallback check
            if (factor == number) {

                do {

                    // Advance the backup position one step at a time
                    backup = polynomial(backup, constant, number);

                    // Compute greatest common divisor of |tortoise - backup| and the number
                    factor = std::gcd(
                        tortoise < backup ? backup - tortoise : tortoise - backup,
                        number
                    );

                // Loop until a factor is found
                } while (factor == 1);

            }

            // Return the factor if it is nontrivial
            if (factor < number) { return factor; }

            // If the factor is still the number itself retry from the top with new random values for the polynomial function

        }

    }

    // ============================================================================================
    // Prime decomposition
    // ============================================================================================
    std::vector<PrimeFactor> squaredPrimeDecomposition1mod4(std::uint_fast64_t number) {

        // Any number passed to this function must be:
        // number >= 2
        // number == odd
        // number % 4 == 1
        // Otherwise it might produce incorrect results

        // No number less than two can be broken down into prime factors
        if (number < 2) { return {}; }

        // Initialize a list for all factors and all primes
        std::vector<std::uint_fast64_t> factors;
        std::vector<std::uint_fast64_t> primes;

        // Reserve size for 64 entries
        // An unsigned 64-bit integer can only have 64 factors
        // 2⁶⁴ = 2 x 2 x 2 ... 64 times
        factors.reserve(64);
        primes.reserve(64);

        // Add the number to the list of factors
        factors.push_back(number);

        // Loop until there are no more factors
        while (!factors.empty()) {

            // Get the latest factor from the list of all factors
            std::uint_fast64_t factor = factors.back();

            // Remove the latest factor from the list of all factors
            factors.pop_back();

            // Check if the latest factor is a prime
            if (millerRabinPrimalityTest(factor)) {

                // If the prime factor is not in the form factor ≡ 1 (mod 4) return no valid prime factors
                if (factor % 4 != 1) { return {}; }

                // Add the latest factor to the list of primes
                primes.push_back(factor);

                // Continue with the next factor
                continue;

            }

            // Check if the factor is less than 30'000'000
            if (factor < 30'000'000) {

                // Use trial division to break down the number into prime factors
                // Trial division is generally faster for small numbers up to around 30 million
                // The trial division will return false if it finds any factor that is not in the form factor ≡ 1 (mod 4)
                // In that case retrun no valid prime factors
                if (!trialDivision(factor, primes)) { return {}; }

                // Continue with the next factor
                continue;

            }

            // Break down the latest factor into a new factor and deduce the other new factor
            std::uint_fast64_t newFactor1 = pollardBrentFactorization(factor);
            std::uint_fast64_t newFactor2 = factor / newFactor1;

            // Add the two new factors to the list of all factors
            factors.push_back(newFactor1);
            factors.push_back(newFactor2);

        }

        // Sort the list of primes
        std::sort(primes.begin(), primes.end());

        // Initialize a list of all prime factors
        std::vector<PrimeFactor> primeFactors;

        // Reserve space for 15 prime factors
        // An unsigned 64-bit integer can only have 15 prime factors
        // Because the first 16 primes multiplied together would overflow the 64-bit range
        primeFactors.reserve(15);

        // Loop through the list of primes
        for (std::uint_fast64_t index = 0; index < primes.size();) {

            // Initialize the prime factor base and exponent
            std::uint_fast64_t base = primes[index];
            std::uint_fast64_t exponent = 0;

            // Check if the next prime is the same as the current prime
            while (base == primes[index] && index < primes.size()) {

                // Increase the exponent by two
                // This is because at this point the number is treaded as if it is squared
                // Any prime factor exponent of a squared number is twice that of the unsquared number
                exponent += 2;

                // Continue with the next prime in the list
                index++;

            }

            // Add the prime factor
            primeFactors.emplace_back(base, exponent);

        }

        // Return the list of prime factors
        return primeFactors;

    }

}