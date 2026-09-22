`timescale 1ns/1ps
module tb_instr_decode;
  reg reset=0; reg [31:0] instr=0;
  wire [6:0] opcode, funct7; wire [4:0] rd, rs1, rs2; wire [2:0] funct3; wire [31:0] imm;
  instr_decode dut (.*);
  initial begin
    #1 reset=1; #1 assert(opcode==0 && rd==0 && imm==0) else $fatal(1,"reset decode mismatch");
    reset=0; instr={12'hffd,5'd2,3'b000,5'd1,7'b0010011}; #1;
    assert(opcode==7'b0010011 && rd==1 && rs1==2 && imm==32'hffff_fffd) else $fatal(1,"I immediate mismatch");
    instr={7'b0000000,5'd4,5'd3,3'b000,5'd8,7'b1100011}; #1;
    assert(imm==8) else $fatal(1,"branch immediate mismatch");
    $display("rtl-riscv32 instruction decoder smoke test passed"); $finish;
  end
endmodule
