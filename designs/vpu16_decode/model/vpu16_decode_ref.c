#include "vpu16_decode_ref.h"

ef_gpu_vpu16_decode_result ef_gpu_vpu16_decode(uint16_t instruction) {
    const bool is_vmac = (instruction >> 12) == 0x1U;
    return (ef_gpu_vpu16_decode_result){
        .valid = is_vmac,
        .is_vmac = is_vmac,
        .destination = (instruction >> 9) & 0x7U,
        .source_a = (instruction >> 6) & 0x7U,
        .source_b = (instruction >> 3) & 0x7U,
        .source_acc = instruction & 0x7U,
    };
}
