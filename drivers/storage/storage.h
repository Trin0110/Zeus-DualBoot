/* SPDX-License-Identifier: MIT */
#ifndef ZEUS_STORAGE_H
#define ZEUS_STORAGE_H
#include <stddef.h>
#include <stdint.h>

enum zeus_storage_result {
    ZEUS_STORAGE_OK = 0, ZEUS_STORAGE_INVALID = -1, ZEUS_STORAGE_RANGE = -2,
    ZEUS_STORAGE_UNSUPPORTED = -3, ZEUS_STORAGE_IO = -4
};

/* A read-only logical view. There is deliberately no write operation.
 * Backend must obey the output size and report failures; this API cannot prevent
 * a malicious backend from touching hardware. No UFS backend is provided. */
struct zeus_storage {
    uint32_t block_size;
    uint64_t first_block;
    uint64_t block_count;
    int (*read_blocks)(void *context, uint64_t absolute_block, uint32_t count,
                       void *output, size_t bytes);
    void *context;
};
int zeus_storage_read(const struct zeus_storage *storage, uint64_t relative_block,
                      uint32_t count, void *output, size_t capacity);
#endif
