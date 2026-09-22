`timescale 1ns/1ps
module tb_fazyrv_pc;
  logic clk_i=0,rst_in=0,inc_i=0,shift_i=0,is_rvc_i=0; logic [1:0] din_i=0;
  wire [1:0] pc_ser_o,pc_ser_inc_o; wire [31:0] pc_o;
  fazyrv_pc #(.CHUNKSIZE(2),.BOOTADR(32'hdead_beef)) dut (.*);
  always #5 clk_i=~clk_i;
  initial begin
    @(posedge clk_i); #1 assert(pc_o==32'hdead_beef) else $fatal(1,"PC reset mismatch");
    @(negedge clk_i); rst_in=1; shift_i=1; din_i=2'b01; @(posedge clk_i); #1;
    assert(pc_o==32'h77ab_6fbb) else $fatal(1,"PC serial shift mismatch");
    $display("FazyRV program counter smoke test passed"); $finish;
  end
endmodule
