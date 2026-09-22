#include "mini_gpu_vmac_ref.h"

#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

static void expect(uint64_t actual, uint64_t expected, const char *label) {
    if (actual != expected) {
        fprintf(stderr, "%s: got=%016" PRIx64 " expected=%016" PRIx64 "\n", label, actual, expected);
        exit(EXIT_FAILURE);
    }
}

int main(void) {
    ef_gpu_mini_gpu_vmac_ref state;
    ef_gpu_mini_gpu_reset(&state);
    ef_gpu_mini_gpu_write(&state, 1, UINT64_C(0x0004000300020001));
    ef_gpu_mini_gpu_write(&state, 2, UINT64_C(0x0008000700060005));
    ef_gpu_mini_gpu_write(&state, 3, UINT64_C(0x0028001e0014000a));
    ef_gpu_mini_gpu_issue(&state, 0x1853U);  // VMAC r4, r1, r2, r3
    expect(ef_gpu_mini_gpu_read(&state, 4), UINT64_C(0x004800330020000f), "VMAC result");
    ef_gpu_mini_gpu_issue(&state, 0x1e54U);  // VMAC r7, r1, r2, r4
    expect(ef_gpu_mini_gpu_read(&state, 7), UINT64_C(0x00680048002c0014), "dependent VMAC result");
    ef_gpu_mini_gpu_issue(&state, 0xf184U);  // invalid opcode must not write r0/r1/etc.
    expect(ef_gpu_mini_gpu_read(&state, 4), UINT64_C(0x004800330020000f), "invalid opcode");
    ef_gpu_mini_gpu_issue(&state, 0x1053U);  // VMAC r0, r1, r2, r3
    expect(ef_gpu_mini_gpu_read(&state, 0), 0, "r0 destination");
    puts("mini GPU VMAC C reference tests passed");
    return EXIT_SUCCESS;
}
