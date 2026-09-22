#ifndef EF_GPU_VPU16_DECODE_REF_H
#define EF_GPU_VPU16_DECODE_REF_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    bool valid;
    bool is_vmac;
    uint8_t destination;
    uint8_t source_a;
    uint8_t source_b;
    uint8_t source_acc;
} ef_gpu_vpu16_decode_result;

ef_gpu_vpu16_decode_result ef_gpu_vpu16_decode(uint16_t instruction);

#endif
