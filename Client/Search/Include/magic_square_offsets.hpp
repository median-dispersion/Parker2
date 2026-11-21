#ifndef PARKER2_MAGIC_SQUARE_OFFSETS_HPP
#define PARKER2_MAGIC_SQUARE_OFFSETS_HPP

#include <vector>
#include "types.hpp"
#include <unordered_set>
#include <utility>
#include "pair_hash.hpp"

// ================================================================================================
// Generate an ordered list of offsets (x and y) from the center value e
// That can be used to construct magic squares
// ================================================================================================
std::vector<ui128> ordered_magic_square_offsets(const std::unordered_set<std::pair<ui64, ui64>, PairHash>& square_root_pairs);

#endif