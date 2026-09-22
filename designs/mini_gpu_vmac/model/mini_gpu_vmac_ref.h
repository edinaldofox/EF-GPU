#ifndef EF_GPU_MINI_GPU_VMAC_REF_H
#define EF_GPU_MINI_GPU_VMAC_REF_H

#include <stdint.h>

typedef struct {
    uint64_t registers[8];
    uint64_t scratchpad[16];
} ef_gpu_mini_gpu_vmac_ref;

void ef_gpu_mini_gpu_reset(ef_gpu_mini_gpu_vmac_ref *state);
void ef_gpu_mini_gpu_write(ef_gpu_mini_gpu_vmac_ref *state, uint8_t address, uint64_t value);
void ef_gpu_mini_gpu_issue(ef_gpu_mini_gpu_vmac_ref *state, uint16_t instruction);
uint64_t ef_gpu_mini_gpu_read(const ef_gpu_mini_gpu_vmac_ref *state, uint8_t address);
void ef_gpu_mini_gpu_memory_write(ef_gpu_mini_gpu_vmac_ref *state, uint8_t address, uint64_t value);
uint64_t ef_gpu_mini_gpu_memory_read(const ef_gpu_mini_gpu_vmac_ref *state, uint8_t address);

#endif
