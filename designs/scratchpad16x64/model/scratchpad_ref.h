#ifndef SCRATCHPAD_REF_H
#define SCRATCHPAD_REF_H

#include <stdint.h>

typedef struct {
    uint64_t words[16];
} scratchpad16x64_t;

void scratchpad16x64_reset(scratchpad16x64_t *scratchpad);
void scratchpad16x64_write(scratchpad16x64_t *scratchpad, uint8_t address, uint64_t data);
uint64_t scratchpad16x64_read(const scratchpad16x64_t *scratchpad, uint8_t address);

#endif
