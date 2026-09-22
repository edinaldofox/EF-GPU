#include "mini_gpu_vmac_ref.h"

#include <string.h>

void ef_gpu_mini_gpu_reset(ef_gpu_mini_gpu_vmac_ref *state) {
    memset(state, 0, sizeof(*state));
}

void ef_gpu_mini_gpu_write(ef_gpu_mini_gpu_vmac_ref *state, uint8_t address, uint64_t value) {
    if ((address & 7U) != 0U)
        state->registers[address & 7U] = value;
}

uint64_t ef_gpu_mini_gpu_read(const ef_gpu_mini_gpu_vmac_ref *state, uint8_t address) {
    return (address & 7U) == 0U ? 0U : state->registers[address & 7U];
}

void ef_gpu_mini_gpu_issue(ef_gpu_mini_gpu_vmac_ref *state, uint16_t instruction) {
    uint64_t result = 0;
    const uint8_t opcode = instruction >> 12;
    const uint8_t destination = (instruction >> 9) & 7U;
    const uint8_t source_a = (instruction >> 6) & 7U;
    const uint8_t source_b = (instruction >> 3) & 7U;
    const uint8_t source_acc = instruction & 7U;
    if (opcode != 1U)
        return;
    for (unsigned lane = 0; lane < 4; ++lane) {
        const uint64_t a = (ef_gpu_mini_gpu_read(state, source_a) >> (lane * 16)) & 0xffU;
        const uint64_t b = (ef_gpu_mini_gpu_read(state, source_b) >> (lane * 16)) & 0xffU;
        const uint64_t acc = (ef_gpu_mini_gpu_read(state, source_acc) >> (lane * 16)) & 0xffffU;
        result |= ((acc + a * b) & 0xffffU) << (lane * 16);
    }
    ef_gpu_mini_gpu_write(state, destination, result);
}
