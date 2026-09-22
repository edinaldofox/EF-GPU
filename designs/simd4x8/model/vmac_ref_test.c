#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "vmac_ref.h"

static void expect(uint32_t a, uint32_t b, uint64_t acc, uint64_t expected) {
    const uint64_t actual = ef_gpu_vmac4x8_ref(a, b, acc);
    if (actual != expected) {
        fprintf(stderr,
                "reference mismatch: a=%08" PRIx32 " b=%08" PRIx32
                " acc=%016" PRIx64 " got=%016" PRIx64 " expected=%016" PRIx64 "\n",
                a, b, acc, actual, expected);
        exit(EXIT_FAILURE);
    }
}

int main(void) {
    expect(0x04030201U, 0x08070605U, 0x0028001e0014000aULL,
           0x004800330020000fULL);
    expect(0x00000000U, 0xffffffffU, 0xffffffffffffffffULL,
           0xffffffffffffffffULL);
    expect(0xffffffffU, 0xffffffffU, 0x0000000000000000ULL,
           0xfe01fe01fe01fe01ULL);
    expect(0xffffffffU, 0xffffffffU, 0xffffffffffffffffULL,
           0xfe00fe00fe00fe00ULL);
    puts("VMAC C reference tests passed");
    return EXIT_SUCCESS;
}
