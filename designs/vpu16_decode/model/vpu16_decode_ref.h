#ifndef EF_GPU_VPU16_DECODE_REF_H
#define EF_GPU_VPU16_DECODE_REF_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    bool valid;
    bool is_vmac;
    bool is_vload;
    bool is_vstore;
    uint8_t destination;
    uint8_t source_a;
    uint8_t source_b;
    uint8_t source_acc;
    uint8_t memory_address;
} ef_gpu_vpu16_decode_result;

ef_gpu_vpu16_decode_result ef_gpu_vpu16_decode(uint16_t instruction);

#endif
