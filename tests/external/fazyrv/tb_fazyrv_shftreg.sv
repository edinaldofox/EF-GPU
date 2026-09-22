`timescale 1ns/1ps
module tb_fazyrv_shftreg;
  logic clk_i=0, shft_i=0; logic [1:0] dat_i=0; wire [1:0] dat_o; wire [31:0] dbg_o;
  fazyrv_shftreg #(.CHUNKSIZE(2)) dut (.*);
  always #5 clk_i=~clk_i;
  initial begin
    @(negedge clk_i); shft_i=1; dat_i=2'b10; @(posedge clk_i); #1;
    assert(dbg_o==32'h8000_0000) else $fatal(1,"first shift mismatch");
    @(negedge clk_i); dat_i=2'b01; @(posedge clk_i); #1;
    assert(dbg_o==32'h6000_0000) else $fatal(1,"second shift mismatch");
    $display("FazyRV shift-register smoke test passed"); $finish;
  end
endmodule
