#ifndef PARKER2_HELPER_FUNCTIONS_HPP
#define PARKER2_HELPER_FUNCTIONS_HPP

#include "types.hpp"
#include <type_traits>
#include <iostream>

// ================================================================================================
// A helper function for casting non standard integer types
// This is mainly intended for casting unsigned 128-bit integers into GMP integers
// But obviously also works for most other integer types
// ================================================================================================
template <typename IntegerType1, typename IntegerType2>
IntegerType1 integer_cast(const IntegerType2& value) {

    // If the target type is a GMP integer and the source type is an unsigned 128-bit integer
    // And unsigned 128-bit integers are available
    #ifdef PARKER2_UI128_AVAILABLE
    if constexpr (std::is_same_v<IntegerType1, gmpi> && std::is_same_v<IntegerType2, ui128>) {

        // Split the unsigned 128-bit integer into a low and high part
        ui64 low = static_cast<ui64>(value);
        ui64 high = static_cast<ui64>(value >> 64);

        // Set the GMP integer to the high part
        gmpi result = high;

        // Shift the high part by 64 bits
        result <<= 64;

        // Add the low part
        result += low;

        // Return the GMP integer
        return result;

    } else
    #endif

    // Cast the value into the new integer type
    return static_cast<IntegerType1>(value);

}

// ================================================================================================
// Overload the << operator to support printing of unsigned 128-bit integers
// ================================================================================================
#ifdef PARKER2_UI128_AVAILABLE
std::ostream& operator<<(std::ostream& stream, ui128 value);
#endif

#endif