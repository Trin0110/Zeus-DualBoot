/* SPDX-License-Identifier: MIT */
#include "platform.h"

static int region_validate(struct zeus_memory_region region)
{
    if (region.size == 0)
        return ZEUS_MEMORY_INVALID;
    if (region.size > UINT64_MAX - region.base)
        return ZEUS_MEMORY_OVERFLOW;
    return ZEUS_MEMORY_OK;
}

static int overlaps(struct zeus_memory_region a, struct zeus_memory_region b)
{
    return a.base < b.base + b.size && b.base < a.base + a.size;
}

int zeus_memory_map_validate(const struct zeus_memory_map *map)
{
    if (map == NULL || map->ram == NULL || map->ram_count == 0 ||
        (map->reserved_count != 0 && map->reserved == NULL))
        return ZEUS_MEMORY_INVALID;
    for (size_t i = 0; i < map->ram_count; ++i) {
        int result = region_validate(map->ram[i]);
        if (result != ZEUS_MEMORY_OK)
            return result;
    }
    for (size_t i = 0; i < map->reserved_count; ++i) {
        int result = region_validate(map->reserved[i]);
        if (result != ZEUS_MEMORY_OK)
            return result;
    }
    for (size_t i = 0; i < map->ram_count; ++i)
        for (size_t j = i + 1; j < map->ram_count; ++j)
            if (overlaps(map->ram[i], map->ram[j]))
                return ZEUS_MEMORY_OVERLAP;
    return ZEUS_MEMORY_OK;
}

int zeus_memory_require_usable(const struct zeus_memory_map *map,
                               struct zeus_memory_region allocation)
{
    int result = zeus_memory_map_validate(map);
    if (result != ZEUS_MEMORY_OK)
        return result;
    result = region_validate(allocation);
    if (result != ZEUS_MEMORY_OK)
        return result;
    for (size_t i = 0; i < map->reserved_count; ++i)
        if (overlaps(allocation, map->reserved[i]))
            return ZEUS_MEMORY_RESERVED;
    for (size_t i = 0; i < map->ram_count; ++i)
        if (allocation.base >= map->ram[i].base &&
            allocation.base + allocation.size <= map->ram[i].base + map->ram[i].size)
            return ZEUS_MEMORY_OK;
    return ZEUS_MEMORY_UNAVAILABLE;
}
