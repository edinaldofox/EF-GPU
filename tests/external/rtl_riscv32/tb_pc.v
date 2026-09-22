`timescale 1ns/1ps
module tb_pc;
  reg clk=0, reset=0; reg [31:0] pc_next=0; wire [31:0] pc;
  pc dut (.*); always #5 clk=~clk;
  initial begin
    #1 reset=1; #1 assert(pc==0) else $fatal(1,"reset mismatch");
    @(negedge clk); reset=0; pc_next=32'h100; @(posedge clk); #1;
    assert(pc==32'h100) else $fatal(1,"increment mismatch");
    $display("rtl-riscv32 PC smoke test passed"); $finish;
  end
endmodule
