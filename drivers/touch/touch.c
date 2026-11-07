/* SPDX-License-Identifier: MIT */
#include "touch.h"
#include <stddef.h>

static int caps_valid(const struct zeus_touch_caps *caps)
{
    return caps != NULL && caps->minimum_x < caps->maximum_x &&
        caps->minimum_y < caps->maximum_y &&
        caps->minimum_pressure <= caps->maximum_pressure && caps->contacts > 0 &&
        caps->contacts <= ZEUS_TOUCH_MAX_CONTACTS;
}

int zeus_touch_initialize(struct zeus_touch *touch, const struct zeus_touch_caps *caps)
{
    if (touch == NULL)
        return ZEUS_TOUCH_INVALID;
    touch->initialized = 0;
    touch->active_contacts = 0;
    if (!caps_valid(caps))
        return ZEUS_TOUCH_INVALID;
    touch->caps = *caps;
    touch->initialized = 1;
    return ZEUS_TOUCH_OK;
}

int zeus_touch_accept(struct zeus_touch *touch, const struct zeus_touch_event *event)
{
    if (touch == NULL || event == NULL || !touch->initialized || !caps_valid(&touch->caps))
        return ZEUS_TOUCH_INVALID;
    if (event->type != ZEUS_TOUCH_DOWN && event->type != ZEUS_TOUCH_MOVE &&
        event->type != ZEUS_TOUCH_UP)
        return ZEUS_TOUCH_INVALID;
    if (event->contact >= touch->caps.contacts || event->x < touch->caps.minimum_x ||
        event->x > touch->caps.maximum_x || event->y < touch->caps.minimum_y ||
        event->y > touch->caps.maximum_y || event->pressure < touch->caps.minimum_pressure ||
        event->pressure > touch->caps.maximum_pressure)
        return ZEUS_TOUCH_RANGE;
    uint32_t mask = UINT32_C(1) << event->contact;
    int active = (touch->active_contacts & mask) != 0;
    if ((event->type == ZEUS_TOUCH_DOWN && active) ||
        (event->type != ZEUS_TOUCH_DOWN && !active))
        return ZEUS_TOUCH_SEQUENCE;
    if (event->type == ZEUS_TOUCH_DOWN)
        touch->active_contacts |= mask;
    else if (event->type == ZEUS_TOUCH_UP)
        touch->active_contacts &= ~mask;
    return ZEUS_TOUCH_OK;
}

int zeus_touch_poll(struct zeus_touch *touch, const struct zeus_touch_ops *ops,
                    void *context, struct zeus_touch_event *event)
{
    if (touch == NULL || event == NULL || !touch->initialized || !caps_valid(&touch->caps))
        return ZEUS_TOUCH_INVALID;
    if (ops == NULL || ops->read_event == NULL)
        return ZEUS_TOUCH_UNSUPPORTED;
    struct zeus_touch_event candidate = {0};
    int result = ops->read_event(context, &candidate);
    if (result != ZEUS_TOUCH_OK)
        return result;
    result = zeus_touch_accept(touch, &candidate);
    if (result == ZEUS_TOUCH_OK)
        *event = candidate;
    return result;
}
