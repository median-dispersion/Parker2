#ifndef PARKER2_TYPES_HPP
#define PARKER2_TYPES_HPP

#include <cstdint>

// Unsigned 64-bit integer alias
using ui64 = std::uint_fast64_t;

// Check if the __uint128_t type is available and set its alias
#ifdef __SIZEOF_INT128__
#define PARKER2_UI128_AVAILABLE
using ui128 = __uint128_t;
#endif

#endif