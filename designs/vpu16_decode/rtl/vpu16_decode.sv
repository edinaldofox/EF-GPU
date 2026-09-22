// Minimal 16-bit vector instruction decoder for the EF-GPU compute and local-memory path.
module vpu16_decode (
    input  logic [15:0] instruction,
    output logic        valid,
    output logic        is_vmac,
    output logic        is_vload,
    output logic        is_vstore,
    output logic [2:0]  destination,
    output logic [2:0]  source_a,
    output logic [2:0]  source_b,
    output logic [2:0]  source_acc,
    output logic [3:0]  memory_address
);
    localparam logic [3:0] OPCODE_VMAC = 4'h1;
    localparam logic [3:0] OPCODE_VLOAD = 4'h2;
    localparam logic [3:0] OPCODE_VSTORE = 4'h3;

    assign destination = instruction[11:9];
    assign source_a = instruction[8:6];
    assign source_b = instruction[5:3];
    assign source_acc = instruction[2:0];
    assign memory_address = instruction[3:0];
    assign is_vmac = instruction[15:12] == OPCODE_VMAC;
    assign is_vload = instruction[15:12] == OPCODE_VLOAD;
    assign is_vstore = instruction[15:12] == OPCODE_VSTORE;
    assign valid = is_vmac || is_vload || is_vstore;
endmodule
