/* SPDX-License-Identifier: MIT */
#include "storage.h"

int zeus_storage_read(const struct zeus_storage *storage, uint64_t relative_block,
                      uint32_t count, void *output, size_t capacity)
{
    if (storage == NULL || output == NULL || count == 0 ||
        storage->block_size < 512 || storage->block_size > 65536 ||
        (storage->block_size & (storage->block_size - 1)) != 0 || storage->block_count == 0)
        return ZEUS_STORAGE_INVALID;
    if (storage->block_count > UINT64_MAX - storage->first_block ||
        relative_block >= storage->block_count || count > storage->block_count - relative_block ||
        count > SIZE_MAX / storage->block_size || (size_t)count * storage->block_size > capacity)
        return ZEUS_STORAGE_RANGE;
    if (storage->read_blocks == NULL)
        return ZEUS_STORAGE_UNSUPPORTED;
    return storage->read_blocks(storage->context, storage->first_block + relative_block,
                                count, output, (size_t)count * storage->block_size);
}
