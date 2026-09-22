#ifndef EF_GPU_VMAC_REF_H
#define EF_GPU_VMAC_REF_H

#include <stdint.h>

/* Four unsigned 8-bit products accumulated into independent 16-bit lanes. */
uint64_t ef_gpu_vmac4x8_ref(uint32_t a, uint32_t b, uint64_t acc);

#endif
