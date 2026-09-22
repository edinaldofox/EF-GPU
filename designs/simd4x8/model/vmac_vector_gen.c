#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "vmac_ref.h"

static uint32_t next_random(uint32_t *state) {
    *state = *state * 1664525U + 1013904223U;
    return *state;
}

static int write_vector(FILE *output, uint32_t a, uint32_t b, uint64_t acc) {
    return fprintf(output, "%08" PRIx32 " %08" PRIx32 " %016" PRIx64 " %016" PRIx64 "\n",
                   a, b, acc, ef_gpu_vmac4x8_ref(a, b, acc)) < 0;
}

int main(int argc, char **argv) {
    enum { RANDOM_VECTOR_COUNT = 128 };
    uint32_t state = 0x1badb002U;
    FILE *output;

    if (argc != 2) {
        fprintf(stderr, "usage: %s OUTPUT_FILE\n", argv[0]);
        return EXIT_FAILURE;
    }
    output = fopen(argv[1], "w");
    if (output == NULL) {
        perror(argv[1]);
        return EXIT_FAILURE;
    }

    if (write_vector(output, 0x00000000U, 0x00000000U, 0x0000000000000000ULL)
        || write_vector(output, 0x04030201U, 0x08070605U, 0x0028001e0014000aULL)
        || write_vector(output, 0xffffffffU, 0xffffffffU, 0x0000000000000000ULL)
        || write_vector(output, 0xffffffffU, 0xffffffffU, 0xffffffffffffffffULL)) {
        perror("writing fixed vectors");
        fclose(output);
        return EXIT_FAILURE;
    }

    for (unsigned index = 0; index < RANDOM_VECTOR_COUNT; ++index) {
        const uint32_t a = next_random(&state);
        const uint32_t b = next_random(&state);
        const uint64_t acc = ((uint64_t)next_random(&state) << 32) | next_random(&state);
        if (write_vector(output, a, b, acc)) {
            perror("writing random vectors");
            fclose(output);
            return EXIT_FAILURE;
        }
    }
    if (fclose(output) != 0) {
        perror("closing vector file");
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
