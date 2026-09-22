#ifndef EF_GPU_VREG_REF_H
#define EF_GPU_VREG_REF_H

#include <stdint.h>

typedef struct {
    uint64_t values[8];
} ef_gpu_vreg8x64_ref;

void ef_gpu_vreg8x64_reset(ef_gpu_vreg8x64_ref *state);
void ef_gpu_vreg8x64_write(ef_gpu_vreg8x64_ref *state, uint8_t address, uint64_t value);
uint64_t ef_gpu_vreg8x64_read(const ef_gpu_vreg8x64_ref *state, uint8_t address);

#endif
