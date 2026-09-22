#include "vmac_ref.h"

uint64_t ef_gpu_vmac4x8_ref(uint32_t a, uint32_t b, uint64_t acc) {
    uint64_t result = 0;

    for (unsigned lane = 0; lane < 4; ++lane) {
        const unsigned a_lane = (a >> (lane * 8)) & 0xffU;
        const unsigned b_lane = (b >> (lane * 8)) & 0xffU;
        const unsigned acc_lane = (acc >> (lane * 16)) & 0xffffU;
        const unsigned lane_result = (acc_lane + a_lane * b_lane) & 0xffffU;

        result |= (uint64_t)lane_result << (lane * 16);
    }
    return result;
}
