#include "vpu16_decode_ref.h"

#include <stdio.h>
#include <stdlib.h>

static void expect(bool condition, const char *label) {
    if (!condition) {
        fprintf(stderr, "decode reference test failed: %s\n", label);
        exit(EXIT_FAILURE);
    }
}

int main(void) {
    const ef_gpu_vpu16_decode_result vmac = ef_gpu_vpu16_decode(0x1caFU);
    const ef_gpu_vpu16_decode_result vload = ef_gpu_vpu16_decode(0x2a0dU);
    const ef_gpu_vpu16_decode_result vstore = ef_gpu_vpu16_decode(0x3604U);
    const ef_gpu_vpu16_decode_result invalid = ef_gpu_vpu16_decode(0xfcaFU);
    expect(vmac.valid && vmac.is_vmac, "VMAC opcode");
    expect(vmac.destination == 6 && vmac.source_a == 2 && vmac.source_b == 5 && vmac.source_acc == 7,
           "VMAC fields");
    expect(vload.valid && vload.is_vload && !vload.is_vmac && !vload.is_vstore,
           "VLOAD opcode");
    expect(vload.destination == 5 && vload.memory_address == 13, "VLOAD fields");
    expect(vstore.valid && vstore.is_vstore && !vstore.is_vmac && !vstore.is_vload,
           "VSTORE opcode");
    expect(vstore.destination == 3 && vstore.memory_address == 4, "VSTORE fields");
    expect(!invalid.valid && !invalid.is_vmac, "invalid opcode");
    expect(invalid.destination == 6 && invalid.source_a == 2 && invalid.source_b == 5 && invalid.source_acc == 7,
           "invalid opcode fields remain observable");
    puts("VPU16 decode C reference tests passed");
    return EXIT_SUCCESS;
}
