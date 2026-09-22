`timescale 1ns/1ps
module tb_alu;
  reg [31:0] a, b; reg [4:0] alu_op;
  wire [31:0] result; wire zero, negative, carry, overflow;
  alu dut (.*);
  initial begin
    a=32'd7; b=32'd9; alu_op=5'b00001; #1;
    assert(result==16 && !zero && !negative && !carry && !overflow) else $fatal(1,"add mismatch");
    a=32'd3; b=32'd5; alu_op=5'b00011; #1;
    assert(result==32'hffff_fffe && negative && !carry) else $fatal(1,"subtract mismatch");
    a=32'h8000_0000; b=32'd1; alu_op=5'b01001; #1;
    assert(result==32'hc000_0000) else $fatal(1,"arithmetic shift mismatch");
    $display("rtl-riscv32 ALU smoke test passed"); $finish;
  end
endmodule
