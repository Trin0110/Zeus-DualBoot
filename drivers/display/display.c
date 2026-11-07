/* SPDX-License-Identifier: MIT */
#include "display.h"

int zeus_framebuffer_validate(const struct zeus_framebuffer *fb)
{
    if (fb == NULL || fb->pixels == NULL || fb->width == 0 || fb->height == 0)
        return ZEUS_DISPLAY_INVALID;
    if (fb->format != ZEUS_RGBX8888 && fb->format != ZEUS_BGRX8888)
        return ZEUS_DISPLAY_UNSUPPORTED;
    if (fb->width > SIZE_MAX / 4 || fb->stride_bytes < fb->width * 4 ||
        fb->stride_bytes % 4 != 0 || fb->height > SIZE_MAX / fb->stride_bytes)
        return ZEUS_DISPLAY_RANGE;
    if (fb->height * fb->stride_bytes > fb->capacity)
        return ZEUS_DISPLAY_RANGE;
    return ZEUS_DISPLAY_OK;
}

int zeus_framebuffer_fill(struct zeus_framebuffer *fb, size_t x, size_t y,
                          size_t width, size_t height,
                          uint8_t red, uint8_t green, uint8_t blue)
{
    int result = zeus_framebuffer_validate(fb);
    if (result != ZEUS_DISPLAY_OK)
        return result;
    if (x > fb->width || y > fb->height || width > fb->width - x ||
        height > fb->height - y)
        return ZEUS_DISPLAY_RANGE;
    for (size_t row = y; row < y + height; ++row) {
        for (size_t col = x; col < x + width; ++col) {
            volatile uint8_t *pixel = fb->pixels + row * fb->stride_bytes + col * 4;
            pixel[0] = fb->format == ZEUS_RGBX8888 ? red : blue;
            pixel[1] = green;
            pixel[2] = fb->format == ZEUS_RGBX8888 ? blue : red;
            pixel[3] = 0xff;
        }
    }
    return ZEUS_DISPLAY_OK;
}

int zeus_display_initialize(struct zeus_display *display)
{
    if (display == NULL)
        return ZEUS_DISPLAY_INVALID;
    if (display->ops == NULL || display->ops->initialize == NULL)
        return ZEUS_DISPLAY_UNSUPPORTED;
    return display->ops->initialize(display->context);
}

int zeus_display_power(struct zeus_display *display, int enabled)
{
    if (display == NULL || (enabled != 0 && enabled != 1))
        return ZEUS_DISPLAY_INVALID;
    if (display->ops == NULL || display->ops->power == NULL)
        return ZEUS_DISPLAY_UNSUPPORTED;
    return display->ops->power(display->context, enabled);
}

int zeus_display_brightness(struct zeus_display *display, uint32_t level)
{
    if (display == NULL)
        return ZEUS_DISPLAY_INVALID;
    if (display->ops == NULL || display->ops->brightness == NULL ||
        display->maximum_brightness == 0)
        return ZEUS_DISPLAY_UNSUPPORTED;
    if (level > display->maximum_brightness)
        return ZEUS_DISPLAY_RANGE;
    return display->ops->brightness(display->context, level);
}

int zeus_display_mode(struct zeus_display *display,
                      const struct zeus_display_mode *mode)
{
    if (display == NULL || mode == NULL || mode->width == 0 || mode->height == 0 ||
        mode->refresh_millihz == 0)
        return ZEUS_DISPLAY_INVALID;
    if (display->ops == NULL || display->ops->mode == NULL)
        return ZEUS_DISPLAY_UNSUPPORTED;
    return display->ops->mode(display->context, mode);
}

int zeus_display_suspend(struct zeus_display *display)
{
    if (display == NULL)
        return ZEUS_DISPLAY_INVALID;
    if (display->ops == NULL || display->ops->suspend == NULL)
        return ZEUS_DISPLAY_UNSUPPORTED;
    return display->ops->suspend(display->context);
}

int zeus_display_resume(struct zeus_display *display)
{
    if (display == NULL)
        return ZEUS_DISPLAY_INVALID;
    if (display->ops == NULL || display->ops->resume == NULL)
        return ZEUS_DISPLAY_UNSUPPORTED;
    return display->ops->resume(display->context);
}
