/* SPDX-License-Identifier: MIT */
#ifndef ZEUS_DISPLAY_H
#define ZEUS_DISPLAY_H

#include <stddef.h>
#include <stdint.h>

enum zeus_display_result {
    ZEUS_DISPLAY_OK = 0,
    ZEUS_DISPLAY_INVALID = -1,
    ZEUS_DISPLAY_RANGE = -2,
    ZEUS_DISPLAY_UNSUPPORTED = -3,
    ZEUS_DISPLAY_IO = -4
};

/* Byte order in memory; X is written as 0xff, never interpreted as alpha. */
enum zeus_pixel_format { ZEUS_RGBX8888 = 1, ZEUS_BGRX8888 = 2 };

struct zeus_framebuffer {
    volatile uint8_t *pixels;
    size_t capacity;
    size_t width;
    size_t height;
    size_t stride_bytes;
    enum zeus_pixel_format format;
};

/* Mapping and ownership must already be established by a trusted boot handoff.
 * These routines neither map physical memory nor infer a panel configuration.
 * CPU cache maintenance and display synchronization belong to the caller. */
int zeus_framebuffer_validate(const struct zeus_framebuffer *fb);
int zeus_framebuffer_fill(struct zeus_framebuffer *fb, size_t x, size_t y,
                          size_t width, size_t height,
                          uint8_t red, uint8_t green, uint8_t blue);

struct zeus_display_mode {
    uint32_t width;
    uint32_t height;
    uint32_t refresh_millihz;
};

/* No hardware backend is included. NULL operations return UNSUPPORTED. */
struct zeus_display_ops {
    int (*initialize)(void *context);
    int (*power)(void *context, int enabled);
    int (*brightness)(void *context, uint32_t level);
    int (*mode)(void *context, const struct zeus_display_mode *mode);
    int (*suspend)(void *context);
    int (*resume)(void *context);
};

struct zeus_display {
    const struct zeus_display_ops *ops;
    void *context;
    uint32_t maximum_brightness; /* Zero means the range is unknown. */
};

int zeus_display_initialize(struct zeus_display *display);
int zeus_display_power(struct zeus_display *display, int enabled);
int zeus_display_brightness(struct zeus_display *display, uint32_t level);
int zeus_display_mode(struct zeus_display *display,
                      const struct zeus_display_mode *mode);
int zeus_display_suspend(struct zeus_display *display);
int zeus_display_resume(struct zeus_display *display);

#endif
