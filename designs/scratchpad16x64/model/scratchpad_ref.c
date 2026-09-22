#include "scratchpad_ref.h"

#include <string.h>

void scratchpad16x64_reset(scratchpad16x64_t *scratchpad) {
    memset(scratchpad->words, 0, sizeof(scratchpad->words));
}

void scratchpad16x64_write(scratchpad16x64_t *scratchpad, uint8_t address, uint64_t data) {
    scratchpad->words[address & 0x0fU] = data;
}

uint64_t scratchpad16x64_read(const scratchpad16x64_t *scratchpad, uint8_t address) {
    return scratchpad->words[address & 0x0fU];
}
