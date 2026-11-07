/* SPDX-License-Identifier: MIT
 * All memory, modes, events and addresses here are synthetic host fixtures. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "drivers/display/display.h"
#include "drivers/touch/touch.h"
#include "drivers/storage/storage.h"
#include "platform/sm8450/platform.h"

static int failing_init(void *context) { (void)context; return ZEUS_DISPLAY_IO; }
static int no_event(void *context, struct zeus_touch_event *e)
{ (void)context; (void)e; return ZEUS_TOUCH_NO_EVENT; }
static int fake_read(void *context, uint64_t block, uint32_t count, void *out, size_t bytes)
{
    int *calls = context;
    ++*calls;
    assert(block == 17 && count == 1 && bytes == 512);
    memset(out, 0xa5, bytes);
    return ZEUS_STORAGE_OK;
}

int main(void)
{
    unsigned char pixels[40];
    memset(pixels, 0x77, sizeof(pixels));
    struct zeus_framebuffer fb = {pixels + 4, 32, 3, 2, 16, ZEUS_RGBX8888};
    assert(zeus_framebuffer_validate(&fb) == 0);
    assert(zeus_framebuffer_fill(&fb, 1, 0, 2, 2, 1, 2, 3) == 0);
    assert(pixels[8] == 1 && pixels[9] == 2 && pixels[10] == 3 && pixels[11] == 255);
    assert(pixels[0] == 0x77 && pixels[36] == 0x77 && pixels[16] == 0x77);
    fb.format = ZEUS_BGRX8888;
    assert(zeus_framebuffer_fill(&fb, 0, 0, 1, 1, 1, 2, 3) == 0);
    assert(pixels[4] == 3 && pixels[6] == 1);
    assert(zeus_framebuffer_fill(&fb, SIZE_MAX, 0, 1, 1, 0, 0, 0) == ZEUS_DISPLAY_RANGE);
    fb.capacity = 31;
    assert(zeus_framebuffer_validate(&fb) == ZEUS_DISPLAY_RANGE);
    fb.capacity = 32; fb.width = SIZE_MAX;
    assert(zeus_framebuffer_validate(&fb) == ZEUS_DISPLAY_RANGE);
    fb.width = 3; fb.height = SIZE_MAX;
    assert(zeus_framebuffer_validate(&fb) == ZEUS_DISPLAY_RANGE);
    struct zeus_display display = {0};
    assert(zeus_display_initialize(&display) == ZEUS_DISPLAY_UNSUPPORTED);
    assert(zeus_display_brightness(&display, 1) == ZEUS_DISPLAY_UNSUPPORTED);
    assert(zeus_display_suspend(&display) == ZEUS_DISPLAY_UNSUPPORTED);
    assert(zeus_display_power(&display, 2) == ZEUS_DISPLAY_INVALID);
    const struct zeus_display_ops display_ops = {.initialize = failing_init};
    display.ops = &display_ops;
    assert(zeus_display_initialize(&display) == ZEUS_DISPLAY_IO);

    struct zeus_touch touch = {0};
    struct zeus_touch_caps caps = {0, 100, 0, 200, 0, 255, 32};
    assert(zeus_touch_initialize(&touch, &caps) == 0);
    struct zeus_touch_event event = {ZEUS_TOUCH_MOVE, 31, 10, 20, 10};
    assert(zeus_touch_accept(&touch, &event) == ZEUS_TOUCH_SEQUENCE);
    event.type = ZEUS_TOUCH_DOWN;
    assert(zeus_touch_accept(&touch, &event) == 0);
    assert(zeus_touch_accept(&touch, &event) == ZEUS_TOUCH_SEQUENCE);
    event.type = ZEUS_TOUCH_MOVE; event.x = 101;
    assert(zeus_touch_accept(&touch, &event) == ZEUS_TOUCH_RANGE);
    event.x = 100;
    assert(zeus_touch_accept(&touch, &event) == 0);
    event.type = ZEUS_TOUCH_UP;
    assert(zeus_touch_accept(&touch, &event) == 0 && touch.active_contacts == 0);
    assert(zeus_touch_poll(&touch, NULL, NULL, &event) == ZEUS_TOUCH_UNSUPPORTED);
    const struct zeus_touch_ops touch_ops = {.read_event = no_event};
    assert(zeus_touch_poll(&touch, &touch_ops, NULL, &event) == ZEUS_TOUCH_NO_EVENT);
    caps.contacts = 33;
    assert(zeus_touch_initialize(&touch, &caps) == ZEUS_TOUCH_INVALID);
    assert(!touch.initialized);

    struct zeus_memory_region ram[] = {{0x1000, 0x1000}, {0x3000, 0x1000}};
    struct zeus_memory_region reserved[] = {{0x1800, 0x100}};
    struct zeus_memory_map map = {ram, 2, reserved, 1};
    assert(zeus_memory_map_validate(&map) == 0);
    assert(zeus_memory_require_usable(&map, (struct zeus_memory_region){0x1000, 0x800}) == 0);
    assert(zeus_memory_require_usable(&map, (struct zeus_memory_region){0x1700, 0x200}) == ZEUS_MEMORY_RESERVED);
    assert(zeus_memory_require_usable(&map, (struct zeus_memory_region){0x1900, 0x2000}) == ZEUS_MEMORY_UNAVAILABLE);
    assert(zeus_memory_require_usable(&map, (struct zeus_memory_region){UINT64_MAX, 1}) == ZEUS_MEMORY_OVERFLOW);
    assert(zeus_memory_require_usable(&map, (struct zeus_memory_region){0x1000, 0}) == ZEUS_MEMORY_INVALID);
    ram[1].base = 0x1100;
    assert(zeus_memory_map_validate(&map) == ZEUS_MEMORY_OVERLAP);
    int calls = 0;
    unsigned char block[513] = {0};
    struct zeus_storage storage = {512, 16, 4, fake_read, &calls};
    assert(zeus_storage_read(&storage, 1, 1, block, sizeof(block)) == 0);
    assert(calls == 1 && block[0] == 0xa5 && block[511] == 0xa5 && block[512] == 0);
    assert(zeus_storage_read(&storage, 3, 2, block, sizeof(block)) == ZEUS_STORAGE_RANGE);
    assert(zeus_storage_read(&storage, UINT64_MAX, 1, block, sizeof(block)) == ZEUS_STORAGE_RANGE);
    assert(zeus_storage_read(&storage, 1, 1, block, 511) == ZEUS_STORAGE_RANGE);
    assert(calls == 1);
    storage.read_blocks = NULL;
    assert(zeus_storage_read(&storage, 1, 1, block, sizeof(block)) == ZEUS_STORAGE_UNSUPPORTED);
    storage.first_block = UINT64_MAX;
    assert(zeus_storage_read(&storage, 0, 1, block, sizeof(block)) == ZEUS_STORAGE_RANGE);
    puts("PASS: framebuffer bounds/color/padding, unsupported callbacks, touch state/ranges, memory exclusions, read-only storage bounds");
    return 0;
}
