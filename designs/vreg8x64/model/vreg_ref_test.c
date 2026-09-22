#include "vreg_ref.h"

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
    ef_gpu_vreg8x64_ref state;
    ef_gpu_vreg8x64_reset(&state);
    expect(ef_gpu_vreg8x64_read(&state, 0), 0, "reset r0");
    expect(ef_gpu_vreg8x64_read(&state, 7), 0, "reset r7");
    ef_gpu_vreg8x64_write(&state, 1, UINT64_C(0x0011002200330044));
    ef_gpu_vreg8x64_write(&state, 7, UINT64_C(0xffeeddccbbaa9988));
    ef_gpu_vreg8x64_write(&state, 0, UINT64_C(0xffffffffffffffff));
    expect(ef_gpu_vreg8x64_read(&state, 1), UINT64_C(0x0011002200330044), "r1 write/read");
    expect(ef_gpu_vreg8x64_read(&state, 7), UINT64_C(0xffeeddccbbaa9988), "r7 write/read");
    expect(ef_gpu_vreg8x64_read(&state, 0), 0, "r0 ignores write");
    puts("VREG8x64 C reference tests passed");
    return EXIT_SUCCESS;
}
