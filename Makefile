CC ?= cc
PYTHON ?= python3
CFLAGS ?= -std=c11 -O1 -g -Wall -Wextra -Werror
SANITIZERS ?= -fsanitize=address,undefined
SOURCES = drivers/display/display.c drivers/touch/touch.c drivers/storage/storage.c platform/sm8450/platform.c
HEADERS = drivers/display/display.h drivers/touch/touch.h drivers/storage/storage.h platform/sm8450/platform.h

.PHONY: all check host-test python-test config upstream-host upstream-check cross-check clean
all: build/libzeus-host.a

build:
	mkdir -p build

build/display.o: drivers/display/display.c $(HEADERS) | build
	$(CC) $(CFLAGS) -I. -c $< -o $@
build/touch.o: drivers/touch/touch.c $(HEADERS) | build
	$(CC) $(CFLAGS) -I. -c $< -o $@
build/platform.o: platform/sm8450/platform.c $(HEADERS) | build
	$(CC) $(CFLAGS) -I. -c $< -o $@
build/storage.o: drivers/storage/storage.c $(HEADERS) | build
	$(CC) $(CFLAGS) -I. -c $< -o $@
build/libzeus-host.a: build/display.o build/touch.o build/platform.o build/storage.o
	$(AR) rcs $@ $^

build/test-platform: $(SOURCES) tests/test_platform.c $(HEADERS) | build
	$(CC) $(CFLAGS) $(SANITIZERS) -I. $(SOURCES) tests/test_platform.c -o $@
host-test: build/test-platform
	./build/test-platform
python-test:
	$(PYTHON) -m unittest discover -s tests -v
config:
	$(PYTHON) -m boot.config devices/zeus/device.json
upstream-host:
	bash scripts/verify-vendored.sh
check: all host-test python-test config upstream-host
upstream-check:
	bash scripts/verify-upstreams.sh
cross-check:
	bash scripts/cross-check.sh
clean:
	rm -rf build
