#include "magic_square_offsets.hpp"
#include <vector>
#include "types.hpp"
#include <unordered_set>
#include <utility>
#include "pair_hash.hpp"
#include <algorithm>

// ================================================================================================
// Generate an ordered list of offsets (x and y) from the center value e
// That can be used to construct magic squares
// ================================================================================================
std::vector<ui128> ordered_magic_square_offsets(const std::unordered_set<std::pair<ui64, ui64>, PairHash>& square_root_pairs) {

    // List of offsets
    std::vector<ui128> magic_square_offsets;

    // Reserve size
    magic_square_offsets.reserve(square_root_pairs.size());

    // Loop through all square root pairs
    for (const std::pair<ui64, ui64>& square_root_pair : square_root_pairs) {

        // Calculate an offset
        // The calculation is performed using unsigned 128-bit integers
        // This is because an offset could be as large as e²
        // So for a value of e = 2⁶⁴-1 the offset would be (2⁶⁴-1)², which fits into an unsigned 128-bit integer
        magic_square_offsets.push_back(static_cast<ui128>(2) * square_root_pair.first * square_root_pair.second);

    };

    // Sort the list
    std::sort(magic_square_offsets.begin(), magic_square_offsets.end());

    // Return the list of offsets
    return magic_square_offsets;

}