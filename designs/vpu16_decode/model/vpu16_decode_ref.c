#include "vpu16_decode_ref.h"

ef_gpu_vpu16_decode_result ef_gpu_vpu16_decode(uint16_t instruction) {
    const uint8_t opcode = instruction >> 12;
    const bool is_vmac = opcode == 0x1U;
    const bool is_vload = opcode == 0x2U;
    const bool is_vstore = opcode == 0x3U;
    return (ef_gpu_vpu16_decode_result){
        .valid = is_vmac || is_vload || is_vstore,
        .is_vmac = is_vmac,
        .is_vload = is_vload,
        .is_vstore = is_vstore,
        .destination = (instruction >> 9) & 0x7U,
        .source_a = (instruction >> 6) & 0x7U,
        .source_b = (instruction >> 3) & 0x7U,
        .source_acc = instruction & 0x7U,
        .memory_address = instruction & 0xfU,
    };
}
