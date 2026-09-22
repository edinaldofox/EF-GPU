export DESIGN_NAME = simd4x8_mac_comb_top
export DESIGN_NICKNAME = simd4x8_mac_comb
export PLATFORM = sky130hd
export VERILOG_FILES = /work/designs/simd4x8/rtl/mult8_comb.sv /work/designs/simd4x8/rtl/simd4x8_mac_comb_top.sv
export SDC_FILE = /work/configs/openroad/simd4x8/comb/constraints.sdc
export CORE_UTILIZATION = 30
export TNS_END_PERCENT = 100
# The pinned image faults in repair_timing after CTS on this host. CTS itself runs.
export SKIP_CTS_REPAIR_TIMING = 1
# report_metrics triggers the same host-specific fault; retain flow logs instead.
export SKIP_REPORT_METRICS = 1
