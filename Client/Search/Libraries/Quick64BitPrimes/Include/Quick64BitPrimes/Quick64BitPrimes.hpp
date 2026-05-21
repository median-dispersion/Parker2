// This file was heavily modified and is not safe to use for arbitrary inputs!
// A lot of input validation checks were removed for better performance in the search for a magic square of squares
// Most inputs now require the number to be odd, not prime, and in the form n ≡ 1 (mod 4)
// For a general, unmodified, and safe implementation, please look at: https://github.com/median-dispersion/Quick-64-Bit-Primes

#ifndef QUICK_64_BIT_PRIMES_HPP
#define QUICK_64_BIT_PRIMES_HPP

#include "Quick64BitPrimes/types.hpp"
#include "Quick64BitPrimes/miller_rabin_primality_test.hpp"
#include "Quick64BitPrimes/prime_decomposition.hpp"
#include "Quick64BitPrimes/tonelli_shanks_algorithm.hpp"
#include "Quick64BitPrimes/fermat_sum_of_two_squares_theorem.hpp"

#endif