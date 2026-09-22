#include "vreg_ref.h"

#include <string.h>

void ef_gpu_vreg8x64_reset(ef_gpu_vreg8x64_ref *state) {
    memset(state, 0, sizeof(*state));
}

void ef_gpu_vreg8x64_write(ef_gpu_vreg8x64_ref *state, uint8_t address, uint64_t value) {
    if ((address & 7U) != 0U)
        state->values[address & 7U] = value;
}

uint64_t ef_gpu_vreg8x64_read(const ef_gpu_vreg8x64_ref *state, uint8_t address) {
    return (address & 7U) == 0U ? 0U : state->values[address & 7U];
}
