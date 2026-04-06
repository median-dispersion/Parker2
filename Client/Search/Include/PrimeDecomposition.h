#ifndef PRIME_DECOMPOSITION_H
#define PRIME_DECOMPOSITION_H

#include <vector>
#include <utility>
#include <cstdint>

// Get all prime factors of e² using trial division
std::vector<std::pair<std::uint_fast64_t, std::uint_fast64_t>> squaredTrialDivision1mod4(std::uint_fast64_t e);

#endif