#include "scratchpad_ref.h"

#include <assert.h>
#include <stdio.h>

int main(void) {
    scratchpad16x64_t scratchpad;

    scratchpad16x64_reset(&scratchpad);
    assert(scratchpad16x64_read(&scratchpad, 0U) == 0U);
    assert(scratchpad16x64_read(&scratchpad, 15U) == 0U);

    scratchpad16x64_write(&scratchpad, 0U, UINT64_C(0x0011002200330044));
    scratchpad16x64_write(&scratchpad, 15U, UINT64_C(0xffeeddccbbaa9988));
    assert(scratchpad16x64_read(&scratchpad, 0U) == UINT64_C(0x0011002200330044));
    assert(scratchpad16x64_read(&scratchpad, 15U) == UINT64_C(0xffeeddccbbaa9988));

    scratchpad16x64_write(&scratchpad, 0U, UINT64_C(0xdeadbeefcafebabe));
    assert(scratchpad16x64_read(&scratchpad, 0U) == UINT64_C(0xdeadbeefcafebabe));

    printf("Scratchpad16x64 C reference test passed\n");
    return 0;
}
