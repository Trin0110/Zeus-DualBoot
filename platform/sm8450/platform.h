/* SPDX-License-Identifier: MIT */
#ifndef ZEUS_SM8450_PLATFORM_H
#define ZEUS_SM8450_PLATFORM_H

#include <stddef.h>
#include <stdint.h>

enum zeus_memory_result {
    ZEUS_MEMORY_OK = 0,
    ZEUS_MEMORY_INVALID = -1,
    ZEUS_MEMORY_OVERFLOW = -2,
    ZEUS_MEMORY_OVERLAP = -3,
    ZEUS_MEMORY_UNAVAILABLE = -4,
    ZEUS_MEMORY_RESERVED = -5
};

struct zeus_memory_region {
    uint64_t base;
    uint64_t size;
};

/* Caller-supplied, verified physical ranges only. No SM8450 addresses are
 * inferred here. RAM windows are disjoint. Reservations can overlap one another
 * and may lie outside RAM (e.g. device regions); all are exclusion intervals. */
struct zeus_memory_map {
    const struct zeus_memory_region *ram;
    size_t ram_count;
    const struct zeus_memory_region *reserved;
    size_t reserved_count;
};

int zeus_memory_map_validate(const struct zeus_memory_map *map);
/* An allocation must fit within one RAM window and avoid every reservation. */
int zeus_memory_require_usable(const struct zeus_memory_map *map,
                               struct zeus_memory_region allocation);

#endif
