// Minimal 16-bit vector instruction decoder for the EF-GPU VMAC path.
module vpu16_decode (
    input  logic [15:0] instruction,
    output logic        valid,
    output logic        is_vmac,
    output logic [2:0]  destination,
    output logic [2:0]  source_a,
    output logic [2:0]  source_b,
    output logic [2:0]  source_acc
);
    localparam logic [3:0] OPCODE_VMAC = 4'h1;

    assign destination = instruction[11:9];
    assign source_a = instruction[8:6];
    assign source_b = instruction[5:3];
    assign source_acc = instruction[2:0];
    assign is_vmac = instruction[15:12] == OPCODE_VMAC;
    assign valid = is_vmac;
endmodule
