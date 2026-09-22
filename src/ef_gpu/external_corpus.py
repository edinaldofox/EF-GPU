"""Materialize a small, reviewed external RTL corpus from pinned checkouts."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ef_gpu.circuit_data import validate_circuit_dataset


ROOT = Path(__file__).resolve().parents[2]

SOURCES: dict[str, dict[str, str]] = {
    "serv": {
        "repository": "https://github.com/olofk/serv.git",
        "commit": "f200eb2ed7b69ac1c6b8eddd47654522aeee5ce8",
        "license": "ISC",
        "license_path": "LICENSE",
        "license_sha256": "d9a1bd691f04280a8369a4aa69b6be20c0e2ee6d164a17ad8a8ef49da8ea0ea9",
    },
    "picorv32": {
        "repository": "https://github.com/YosysHQ/picorv32.git",
        "commit": "ef203c2b0a3fb793280f5114941416c425c5b461",
        "license": "ISC",
        "license_path": "COPYING",
        "license_sha256": "041ebc727233e5bf096dd41260cbb81014d3d29ca007a15f3b1807d4e9ff288e",
    },
    "rtl-riscv32": {
        "repository": "https://github.com/VaradaGovind/rtl-riscv32.git",
        "commit": "c8b8d95d15d8099b02091cf9a6ed53686541e096",
        "license": "MIT",
        "license_path": "LICENSE",
        "license_sha256": "5d77a4df434a9f088476a91acefa0f98c46b39ae60e89e8213c4a460ae7fef4e",
    },
    "fazyrv": {
        "repository": "https://github.com/meiniKi/FazyRV.git",
        "commit": "c8d9c7971b91c0c166aef6c236f1134b2c6ac1a1",
        "license": "MIT",
        "license_path": "rtl/LICENSE.txt",
        "license_sha256": "31beba5b18f79bd120e371525c603f057952effd4d6436a584073f3e50537edc",
    },
    "learn-fpga": {
        "repository": "https://github.com/BrunoLevy/learn-fpga.git",
        "commit": "5c08c870315c09ccd9ec64ccde20ab3375b3f273",
        "license": "BSD-3-Clause",
        "license_path": "LICENSE",
        "license_sha256": "dae852f7354066fe13901a60a49ac4f7e45b9ae16fec901e12e24218da0ea999",
    },
    "fma-rtl": {
        "repository": "https://github.com/Tachyum-Open-Source/fma-rtl.git",
        "commit": "1e7221349e7b18b1e20f4b301f3b7a34b5ebd490",
        "license": "Apache-2.0",
        "license_path": "LICENSE",
        "license_sha256": "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    },
}

EXAMPLES: tuple[dict[str, Any], ...] = (
    {
        "id": "serv-alu-001",
        "source_id": "serv",
        "split": "train",
        "design_family": "serv_serial_alu",
        "source_path": "rtl/serv_alu.v",
        "testbench": "tests/external/serv/tb_serv_alu.sv",
        "specification": "Implement the pinned SERV one-bit serial ALU with add, boolean and compare datapaths.",
        "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_alu",
    },
    {
        "id": "serv-aligner-001",
        "source_id": "serv",
        "split": "train",
        "design_family": "serv_instruction_aligner",
        "source_path": "rtl/serv_aligner.v",
        "testbench": "tests/external/serv/tb_serv_aligner.sv",
        "specification": "Implement the pinned SERV instruction-bus aligner, including half-word realignment after a misaligned fetch.",
        "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_aligner",
    },
    {
        "id": "serv-rf-ram-001",
        "source_id": "serv",
        "split": "train",
        "design_family": "serv_parameterized_register_file_ram",
        "source_path": "rtl/serv_rf_ram.v",
        "testbench": "tests/external/serv/tb_serv_rf_ram.sv",
        "specification": "Implement the pinned SERV parameterized synchronous register-file RAM, including masked reads of architectural register x0.",
        "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_rf_ram",
    },
    {
        "id": "serv-rf-ram-w1-001", "source_id": "serv", "split": "train", "design_family": "serv_register_file_ram_1_bit_lane", "source_path": "rtl/serv_rf_ram.v", "testbench": "tests/external/serv/tb_serv_rf_ram_w1.sv", "specification": "Implement the pinned SERV register-file RAM configured for one-bit serial lanes and 1024 words, preserving x0 masking.", "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_rf_ram_w1"},
    {
        "id": "serv-rf-ram-w2-001", "source_id": "serv", "split": "train", "design_family": "serv_register_file_ram_2_bit_lane", "source_path": "rtl/serv_rf_ram.v", "testbench": "tests/external/serv/tb_serv_rf_ram_w2.sv", "specification": "Implement the pinned SERV register-file RAM configured for two-bit lanes and 512 words, preserving x0 masking.", "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_rf_ram_w2"},
    {
        "id": "serv-rf-ram-w4-001", "source_id": "serv", "split": "train", "design_family": "serv_register_file_ram_4_bit_lane", "source_path": "rtl/serv_rf_ram.v", "testbench": "tests/external/serv/tb_serv_rf_ram_w4.sv", "specification": "Implement the pinned SERV register-file RAM configured for four-bit lanes and 256 words, preserving x0 masking.", "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_rf_ram_w4"},
    {
        "id": "serv-rf-ram-w16-001", "source_id": "serv", "split": "train", "design_family": "serv_register_file_ram_16_bit_lane", "source_path": "rtl/serv_rf_ram.v", "testbench": "tests/external/serv/tb_serv_rf_ram_w16.sv", "specification": "Implement the pinned SERV register-file RAM configured for sixteen-bit lanes and 64 words, preserving x0 masking.", "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_rf_ram_w16"},
    {
        "id": "serv-rf-ram-w32-001", "source_id": "serv", "split": "train", "design_family": "serv_register_file_ram_32_bit_lane", "source_path": "rtl/serv_rf_ram.v", "testbench": "tests/external/serv/tb_serv_rf_ram_w32.sv", "specification": "Implement the pinned SERV register-file RAM configured for thirty-two-bit lanes and 32 words, preserving x0 masking.", "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_rf_ram_w32"},
    {
        "id": "serv-rf-ram-w8-c4-001", "source_id": "serv", "split": "train", "design_family": "serv_register_file_ram_8_bit_lane_with_csrs", "source_path": "rtl/serv_rf_ram.v", "testbench": "tests/external/serv/tb_serv_rf_ram_w8_c4.sv", "specification": "Implement the pinned SERV register-file RAM configured for eight-bit lanes, four CSR slots and 144 words.", "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_rf_ram_w8_c4"},
    {
        "id": "serv-rf-ram-w16-c4-001", "source_id": "serv", "split": "train", "design_family": "serv_register_file_ram_16_bit_lane_with_csrs", "source_path": "rtl/serv_rf_ram.v", "testbench": "tests/external/serv/tb_serv_rf_ram_w16_c4.sv", "specification": "Implement the pinned SERV register-file RAM configured for sixteen-bit lanes, four CSR slots and 72 words.", "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_rf_ram_w16_c4"},
    {
        "id": "serv-rf-ram-w32-c4-001", "source_id": "serv", "split": "train", "design_family": "serv_register_file_ram_32_bit_lane_with_csrs", "source_path": "rtl/serv_rf_ram.v", "testbench": "tests/external/serv/tb_serv_rf_ram_w32_c4.sv", "specification": "Implement the pinned SERV register-file RAM configured for thirty-two-bit lanes, four CSR slots and 36 words.", "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_rf_ram_w32_c4"},
    {
        "id": "serv-bufreg-001",
        "source_id": "serv",
        "split": "train",
        "design_family": "serv_serial_address_and_shift_buffer",
        "source_path": "rtl/serv_bufreg.v",
        "testbench": "tests/external/serv/tb_serv_bufreg.sv",
        "specification": "Implement the pinned SERV one-bit serial buffer for address construction and shift data, including low-bit alignment output.",
        "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_bufreg",
    },
    {
        "id": "serv-bufreg2-001",
        "source_id": "serv",
        "split": "train",
        "design_family": "serv_store_data_and_shift_buffer",
        "source_path": "rtl/serv_bufreg2.v",
        "testbench": "tests/external/serv/tb_serv_bufreg2.sv",
        "specification": "Implement the pinned SERV one-bit buffer for load/store data and shift state, with byte-lane extraction and selectable operand B.",
        "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_bufreg2",
    },
    {
        "id": "serv-state-001",
        "source_id": "serv",
        "split": "train",
        "design_family": "serv_serial_execution_state_controller",
        "source_path": "rtl/serv_state.v",
        "testbench": "tests/external/serv/tb_serv_state.sv",
        "specification": "Implement the pinned SERV bit-serial execution state controller with reset-gated instruction fetch and four-phase counter enable.",
        "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_state",
    },
    {
        "id": "serv-decode-001",
        "source_id": "serv",
        "split": "train",
        "design_family": "serv_riscv_instruction_control_decoder",
        "source_path": "rtl/serv_decode.v",
        "testbench": "tests/external/serv/tb_serv_decode.sv",
        "specification": "Implement the pinned SERV registered RISC-V instruction decoder for load, store and conditional-branch control signals.",
        "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_decode",
    },
    {
        "id": "serv-immdec-001",
        "source_id": "serv",
        "split": "train",
        "design_family": "serv_serial_immediate_and_register_decoder",
        "source_path": "rtl/serv_immdec.v",
        "testbench": "tests/external/serv/tb_serv_immdec.sv",
        "specification": "Implement the pinned SERV serial immediate decoder with shared register-address state, CSR immediate extraction and immediate-bit selection.",
        "verification_command": "./scripts/verify-external-rtl.sh serv && ./scripts/synth-external-rtl.sh serv serv_immdec",
    },
    {
        "id": "picorv32-pcpi-mul-001",
        "source_id": "picorv32",
        "split": "benchmark",
        "design_family": "picorv32_iterative_pcpi_multiplier",
        "source_path": "picorv32.v",
        "module": "picorv32_pcpi_mul",
        "testbench": "tests/external/picorv32/tb_picorv32_pcpi_mul.sv",
        "specification": "Implement the pinned PicoRV32 iterative PCPI multiplier for the RISC-V M-extension MUL instruction.",
        "verification_command": "./scripts/verify-external-rtl.sh picorv32 && ./scripts/synth-external-rtl.sh picorv32 picorv32_pcpi_mul",
    },
    {
        "id": "rtl-riscv32-pc-001",
        "source_id": "rtl-riscv32",
        "split": "validation",
        "design_family": "rtl_riscv32_program_counter",
        "source_path": "RiscV-32bit/RiscV-32bit.srcs/sources_1/new/pc.v",
        "testbench": "tests/external/rtl_riscv32/tb_pc.v",
        "specification": "Implement the pinned RTL-RISCV32 program counter with asynchronous reset and synchronous next-PC capture.",
        "verification_command": "./scripts/verify-external-rtl.sh rtl-riscv32 && ./scripts/synth-external-rtl.sh rtl-riscv32 pc",
    },
    {
        "id": "femtorv-step1-001",
        "source_id": "learn-fpga",
        "split": "validation",
        "design_family": "femtorv_tutorial_five_bit_blinker",
        "source_path": "FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step1.v",
        "testbench": "tests/external/femtorv/tb_femtorv_step1.v",
        "specification": "Implement the pinned FemtoRV tutorial five-bit synchronous LED counter with a constant inactive UART transmitter.",
        "verification_command": "./scripts/verify-external-rtl.sh learn-fpga && ./scripts/synth-external-rtl.sh learn-fpga SOC",
    },
    {
        "id": "femtorv-step2-001",
        "source_id": "learn-fpga",
        "split": "validation",
        "design_family": "femtorv_tutorial_clock_divided_counter",
        "source_path": "FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step2.v",
        "dependencies": ("FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/clockworks.v", "FemtoRV/RTL/PLL/femtopll.v"),
        "testbench": "tests/external/femtorv/tb_femtorv_step2.v",
        "specification": "Implement the pinned FemtoRV five-bit counter gated by the tutorial clock divider and active-high reset input.",
        "verification_command": "./scripts/verify-external-rtl.sh learn-fpga && ./scripts/synth-external-rtl.sh learn-fpga SOC_step2",
    },
    {
        "id": "femtorv-step3-001",
        "source_id": "learn-fpga",
        "split": "validation",
        "design_family": "femtorv_tutorial_bram_led_pattern",
        "source_path": "FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step3.v",
        "dependencies": ("FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/clockworks.v", "FemtoRV/RTL/PLL/femtopll.v"),
        "testbench": "tests/external/femtorv/tb_femtorv_step3.v",
        "specification": "Implement the pinned FemtoRV tutorial LED pattern sequencer backed by initialized on-chip memory and a divided clock.",
        "verification_command": "./scripts/verify-external-rtl.sh learn-fpga && ./scripts/synth-external-rtl.sh learn-fpga SOC_step3",
    },
    {
        "id": "femtorv-step4-001",
        "source_id": "learn-fpga",
        "split": "validation",
        "design_family": "femtorv_tutorial_instruction_class_decoder",
        "source_path": "FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step4.v",
        "dependencies": ("FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/clockworks.v", "FemtoRV/RTL/PLL/femtopll.v"),
        "testbench": "tests/external/femtorv/tb_femtorv_step4.v",
        "specification": "Implement the pinned FemtoRV tutorial instruction-memory fetcher and RISC-V opcode-class decoder, exposing instruction class through LEDs.",
        "verification_command": "./scripts/verify-external-rtl.sh learn-fpga && ./scripts/synth-external-rtl.sh learn-fpga SOC_step4",
    },
    {
        "id": "femtorv-step5-001",
        "source_id": "learn-fpga",
        "split": "validation",
        "design_family": "femtorv_tutorial_fetch_execute_state_machine",
        "source_path": "FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/step5.v",
        "dependencies": ("FemtoRV/TUTORIALS/FROM_BLINKER_TO_RISCV/clockworks.v", "FemtoRV/RTL/PLL/femtopll.v"),
        "testbench": "tests/external/femtorv/tb_femtorv_step5.v",
        "specification": "Implement the pinned FemtoRV tutorial three-state fetch, register-read and execute controller.",
        "verification_command": "./scripts/verify-external-rtl.sh learn-fpga && ./scripts/synth-external-rtl.sh learn-fpga SOC_step5",
    },
    {
        "id": "fazyrv-hadd-001",
        "source_id": "fazyrv",
        "split": "train",
        "design_family": "fazyrv_half_adder",
        "source_path": "rtl/fazyrv_hadd.v",
        "testbench": "tests/external/fazyrv/tb_fazyrv_hadd.sv",
        "specification": "Implement the pinned FazyRV one-bit half-adder with sum and carry outputs.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_hadd",
    },
    {
        "id": "fazyrv-fadd-001",
        "source_id": "fazyrv",
        "split": "train",
        "design_family": "fazyrv_full_adder",
        "source_path": "rtl/fazyrv_fadd.v",
        "dependencies": ("rtl/fazyrv_hadd.v",),
        "testbench": "tests/external/fazyrv/tb_fazyrv_fadd.sv",
        "specification": "Implement the pinned FazyRV one-bit full-adder and its half-adder dependency.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_fadd",
    },
    {
        "id": "fazyrv-cmp-001",
        "source_id": "fazyrv",
        "split": "train",
        "design_family": "fazyrv_chunk_comparator",
        "source_path": "rtl/fazyrv_cmp.v",
        "testbench": "tests/external/fazyrv/tb_fazyrv_cmp.sv",
        "specification": "Implement the pinned FazyRV parameterized chunk comparator, including signed-MSB inversion.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_cmp",
    },
    {
        "id": "fazyrv-shftreg-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_shift_register",
        "source_path": "rtl/fazyrv_shftreg.sv", "testbench": "tests/external/fazyrv/tb_fazyrv_shftreg.sv",
        "specification": "Implement the pinned FazyRV parameterized serial shift register.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_shftreg",
    },
    {
        "id": "fazyrv-ram-sp-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_single_port_ram",
        "source_path": "rtl/fazyrv_ram_sp.sv", "testbench": "tests/external/fazyrv/tb_fazyrv_ram_sp.sv",
        "specification": "Implement the pinned FazyRV synchronous single-port register RAM.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_ram_sp",
    },
    {
        "id": "fazyrv-ram-dp-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_dual_port_ram",
        "source_path": "rtl/fazyrv_ram_dp.sv", "testbench": "tests/external/fazyrv/tb_fazyrv_ram_dp.sv",
        "specification": "Implement the pinned FazyRV synchronous dual-read-port register RAM.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_ram_dp",
    },
    {
        "id": "fazyrv-align-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_memory_aligner",
        "source_path": "rtl/fazyrv_align.sv", "testbench": "tests/external/fazyrv/tb_fazyrv_align.sv",
        "specification": "Implement the pinned FazyRV memory-bus aligner for aligned and half-word-offset transactions.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_align",
    },
    {
        "id": "fazyrv-spm-a-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_address_serializer",
        "source_path": "rtl/fazyrv_spm_a.sv", "testbench": "tests/external/fazyrv/tb_fazyrv_spm_a.sv",
        "specification": "Implement the pinned FazyRV serial-to-parallel 32-bit address register.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_spm_a",
    },
    {
        "id": "fazyrv-pc-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_serial_program_counter",
        "source_path": "rtl/fazyrv_pc.sv", "dependencies": ("rtl/fazyrv_hadd.v",), "testbench": "tests/external/fazyrv/tb_fazyrv_pc.sv",
        "specification": "Implement the pinned FazyRV serial program counter with configurable boot address and half-adder dependency.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_pc",
    },
    {
        "id": "fazyrv-rvc-001", "source_id": "fazyrv", "split": "train", "design_family": "fazyrv_compressed_instruction_decoder",
        "source_path": "rtl/fazyrv_rvc.sv", "testbench": "tests/external/fazyrv/tb_fazyrv_rvc.sv",
        "specification": "Implement the pinned FazyRV compressed-instruction decoder with acknowledgement-qualified compressed flag.",
        "verification_command": "./scripts/verify-external-rtl.sh fazyrv && ./scripts/synth-external-rtl.sh fazyrv fazyrv_rvc",
    },
    {
        "id": "fma-mux2-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_two_way_mux", "source_path": "mux2.v", "testbench": "tests/external/fma/tb_mux2.v", "specification": "Implement the pinned Tachyum parameterized two-way multiplexer.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl mux2"},
    {
        "id": "fma-mux5d-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_one_hot_five_way_mux", "source_path": "mux5d.v", "testbench": "tests/external/fma/tb_mux5d.v", "specification": "Implement the pinned Tachyum five-way one-hot multiplexer.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl mux5d"},
    {
        "id": "fma-dff-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_parameterized_dff", "source_path": "dff.v", "testbench": "tests/external/fma/tb_dff.v", "specification": "Implement the pinned Tachyum parameterized rising-edge D flip-flop.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl dff"},
    {
        "id": "fma-dffe-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_enabled_dff", "source_path": "dffe.v", "testbench": "tests/external/fma/tb_dffe.v", "specification": "Implement the pinned Tachyum parameterized enabled D flip-flop.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl dffe"},
    {
        "id": "fma-incrementer-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_parameterized_incrementer", "source_path": "incrementer.v", "testbench": "tests/external/fma/tb_incrementer.v", "specification": "Implement the pinned Tachyum parameterized incrementer with carry output.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl incrementer"},
    {
        "id": "fma-incrementer8-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_eight_bit_incrementer", "source_path": "incrementer_8.v", "testbench": "tests/external/fma/tb_incrementer_8.v", "specification": "Implement the pinned Tachyum eight-bit incrementer with carry output.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl incrementer_8"},
    {
        "id": "fma-adder10-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_ten_bit_adder_with_carry_in", "source_path": "adder10.v", "testbench": "tests/external/fma/tb_adder10.v", "specification": "Implement the pinned Tachyum ten-bit adder with carry input and output.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl adder10"},
    {
        "id": "fma-adder10-no-cin-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_ten_bit_adder", "source_path": "adder10_no_cin.v", "testbench": "tests/external/fma/tb_adder10_no_cin.v", "specification": "Implement the pinned Tachyum ten-bit adder without carry input.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl adder10_no_cin"},
    {
        "id": "fma-adder13-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_thirteen_bit_adder", "source_path": "adder13.v", "testbench": "tests/external/fma/tb_adder13.v", "specification": "Implement the pinned Tachyum thirteen-bit adder with carry input and output.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl adder13"},
    {
        "id": "fma-incrementer11-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_eleven_bit_incrementer", "source_path": "incrementer_11.v", "testbench": "tests/external/fma/tb_incrementer_11.v", "specification": "Implement the pinned Tachyum eleven-bit incrementer with carry output.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl incrementer_11"},
    {
        "id": "fma-adder13-no-cin-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_thirteen_bit_adder_without_carry_in", "source_path": "adder13_no_cin.v", "testbench": "tests/external/fma/tb_adder13_no_cin.v", "specification": "Implement the pinned Tachyum thirteen-bit adder without carry input.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl adder13_no_cin"},
    {
        "id": "fma-adder161-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_161_bit_adder", "source_path": "adder161_no_cin_no_cout.v", "testbench": "tests/external/fma/tb_adder161_no_cin_no_cout.v", "specification": "Implement the pinned Tachyum 161-bit adder without carry ports.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl adder161_no_cin_no_cout"},
    {
        "id": "fma-adder162-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_162_bit_adder", "source_path": "adder162_no_cin.v", "testbench": "tests/external/fma/tb_adder162_no_cin.v", "specification": "Implement the pinned Tachyum 162-bit adder with carry output.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl adder162_no_cin"},
    {
        "id": "fma-left-shifter28-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_28_bit_left_shifter", "source_path": "left_shifter_28.v", "testbench": "tests/external/fma/tb_left_shifter_28.v", "specification": "Implement the pinned Tachyum 28-bit variable left shifter.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl left_shifter_28"},
    {
        "id": "fma-left-shifter76-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_76_bit_left_shifter", "source_path": "left_shifter_76.v", "testbench": "tests/external/fma/tb_left_shifter_76.v", "specification": "Implement the pinned Tachyum 76-bit variable left shifter.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl left_shifter_76"},
    {
        "id": "fma-left-shifter163-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_163_bit_left_shifter", "source_path": "left_shifter_163.v", "testbench": "tests/external/fma/tb_left_shifter_163.v", "specification": "Implement the pinned Tachyum 163-bit variable left shifter.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl left_shifter_163"},
    {
        "id": "fma-right-shifter26-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_26_bit_right_shifter_with_outside_bits", "source_path": "right_shifter_26_with_outside_bits.v", "testbench": "tests/external/fma/tb_right_shifter_26_with_outside_bits.v", "specification": "Implement the pinned Tachyum 26-bit logical right shifter with outside-bit output.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl right_shifter_26_with_outside_bits"},
    {
        "id": "fma-right-shifter74-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_74_bit_right_shifter_with_outside_bits", "source_path": "right_shifter_74_with_outside_bits.v", "testbench": "tests/external/fma/tb_right_shifter_74_with_outside_bits.v", "specification": "Implement the pinned Tachyum 74-bit logical right shifter with outside-bit output.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl right_shifter_74_with_outside_bits"},
    {
        "id": "fma-right-shifter161-001", "source_id": "fma-rtl", "split": "benchmark", "design_family": "fma_161_bit_right_shifter_with_outside_bits", "source_path": "right_shifter_161_with_outside_bits.v", "testbench": "tests/external/fma/tb_right_shifter_161_with_outside_bits.v", "specification": "Implement the pinned Tachyum 161-bit logical right shifter with outside-bit output.", "verification_command": "./scripts/verify-external-rtl.sh fma-rtl && ./scripts/synth-external-rtl.sh fma-rtl right_shifter_161_with_outside_bits"},
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_module(source: str, module: str) -> str:
    """Keep one Verilog module rather than ingesting an unrelated monolithic file."""
    start = re.search(rf"(?m)^module\s+{re.escape(module)}(?:\s|#|\()", source)
    if start is None:
        raise ValueError(f"module not found in reviewed source: {module}")
    end = re.search(r"(?m)^endmodule\b", source[start.start() :])
    if end is None:
        raise ValueError(f"unterminated reviewed module: {module}")
    return source[start.start() : start.start() + end.end()] + "\n"


def _checked_source_root(source_id: str, root: Path) -> dict[str, str]:
    source = SOURCES[source_id]
    if not root.is_dir():
        raise ValueError(f"{source_id} checkout does not exist: {root}")
    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    if head != source["commit"]:
        raise ValueError(f"{source_id} checkout commit mismatch: {head}")
    if _sha256(root / source["license_path"]) != source["license_sha256"]:
        raise ValueError(f"{source_id} license checksum mismatch")
    return source


def build_external_circuit_corpus(output: Path, source_roots: dict[str, Path]) -> dict[str, Any]:
    """Write verbatim, license-preserving examples from reviewed temporary checkouts."""
    if output.exists():
        raise ValueError(f"external corpus output already exists: {output}")
    checked = {source_id: _checked_source_root(source_id, source_roots[source_id]) for source_id in SOURCES}
    records: list[dict[str, Any]] = []
    for example in EXAMPLES:
        source = checked[example["source_id"]]
        relative_paths = (*example.get("dependencies", ()), example["source_path"])
        source_paths = [source_roots[example["source_id"]] / relative_path for relative_path in relative_paths]
        testbench_path = ROOT / example["testbench"]
        if not all(path.is_file() for path in source_paths) or not testbench_path.is_file():
            raise ValueError(f"missing reviewed example input for {example['id']}")
        rtl_parts = []
        for relative_path, source_path in zip(relative_paths, source_paths, strict=True):
            source_text = source_path.read_text(encoding="utf-8")
            rtl_parts.append(_extract_module(source_text, example["module"]) if relative_path == example["source_path"] and "module" in example else source_text)
        rtl = "\n".join(rtl_parts)
        license_text = (source_roots[example["source_id"]] / source["license_path"]).read_text(encoding="utf-8")
        rtl = f"/* External source license ({source['license']}):\n{license_text.rstrip()}\n*/\n\n{rtl}"
        testbench = testbench_path.read_text(encoding="utf-8")
        records.append(
            {
                "schema_version": "1.0",
                "id": example["id"],
                "split": example["split"],
                "design_family": example["design_family"],
                "task": "specification-to-systemverilog-with-testbench",
                "input": {"specification": example["specification"], "context": "Pinned external RTL reference; preserve its license notice."},
                "target": {"systemverilog": rtl, "testbench": testbench},
                "verification": {"rtl_simulation": "passed", "synthesis": "passed", "command": example["verification_command"]},
                "provenance": {
                    "source": source["repository"],
                    "license": source["license"],
                    "reviewed": True,
                    "source_commit": source["commit"],
                    "source_paths": [*relative_paths, example["testbench"]],
                    "source_sha256": {**{relative_path: _sha256(source_path) for relative_path, source_path in zip(relative_paths, source_paths, strict=True)}, example["testbench"]: _sha256(testbench_path)},
                    "license_sha256": source["license_sha256"],
                    "dependencies": list(example.get("dependencies", ())),
                    "transformation": (
                        "verbatim selected RTL file preceded by its complete license text; EF-GPU-authored focused smoke testbench appended as separate target field"
                        if "module" not in example
                        else f"verbatim extraction of module {example['module']} from a monolithic reviewed RTL file, preceded by its complete license text; EF-GPU-authored focused smoke testbench appended as separate target field"
                    ),
                },
            }
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")
    validation = validate_circuit_dataset(output)
    benchmark = [record for record in records if record["split"] == "benchmark"]
    benchmark_bytes = "".join(json.dumps(record, sort_keys=True) + "\n" for record in benchmark).encode()
    manifest = {
        "schema_version": "1.0",
        "command": "build-external-circuit-corpus",
        "output": str(output),
        "output_sha256": _sha256(output),
        "benchmark_records": [record["id"] for record in benchmark],
        "frozen_benchmark_sha256": hashlib.sha256(benchmark_bytes).hexdigest(),
        "created_at_utc": datetime.now(UTC).isoformat(),
        "validation": validation,
        "training_status": "candidate-data-only; below Sprint 3 volume floor and no model weights trained",
    }
    output.with_suffix(output.suffix + ".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
