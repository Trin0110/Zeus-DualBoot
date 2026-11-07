/* SPDX-License-Identifier: MIT */
#ifndef ZEUS_TOUCH_H
#define ZEUS_TOUCH_H

#include <stdint.h>

#define ZEUS_TOUCH_MAX_CONTACTS 32

enum zeus_touch_result {
    ZEUS_TOUCH_OK = 0,
    ZEUS_TOUCH_INVALID = -1,
    ZEUS_TOUCH_RANGE = -2,
    ZEUS_TOUCH_SEQUENCE = -3,
    ZEUS_TOUCH_UNSUPPORTED = -4,
    ZEUS_TOUCH_NO_EVENT = -5,
    ZEUS_TOUCH_IO = -6
};
enum zeus_touch_event_type { ZEUS_TOUCH_DOWN = 1, ZEUS_TOUCH_MOVE, ZEUS_TOUCH_UP };

struct zeus_touch_caps {
    int32_t minimum_x, maximum_x;
    int32_t minimum_y, maximum_y;
    int32_t minimum_pressure, maximum_pressure;
    uint32_t contacts;
};

struct zeus_touch_event {
    enum zeus_touch_event_type type;
    uint32_t contact;
    int32_t x, y, pressure;
};

struct zeus_touch {
    struct zeus_touch_caps caps;
    uint32_t active_contacts;
    int initialized;
};

/* A backend must return NO_EVENT when no complete event is available. */
struct zeus_touch_ops {
    int (*read_event)(void *context, struct zeus_touch_event *event);
};

int zeus_touch_initialize(struct zeus_touch *touch, const struct zeus_touch_caps *caps);
int zeus_touch_accept(struct zeus_touch *touch, const struct zeus_touch_event *event);
int zeus_touch_poll(struct zeus_touch *touch, const struct zeus_touch_ops *ops,
                    void *context, struct zeus_touch_event *event);

#endif
