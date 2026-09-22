`timescale 1ns/1ps
module tb_fazyrv_ram_dp;
  logic clk_i=0,we_i=0; logic [4:0] waddr_i=0,raddr_a_i=0,raddr_b_i=0; logic [31:0] wdata_i=0; wire [31:0] rdata_a_o,rdata_b_o;
  fazyrv_ram_dp dut (.*); always #5 clk_i=~clk_i;
  initial begin
    @(negedge clk_i); we_i=1; waddr_i=3; wdata_i=32'hcafe_babe; @(posedge clk_i);
    @(negedge clk_i); we_i=0; raddr_a_i=3; raddr_b_i=3; @(posedge clk_i); #1;
    assert(rdata_a_o==32'hcafe_babe && rdata_b_o==32'hcafe_babe) else $fatal(1,"dual-port RAM readback mismatch");
    $display("FazyRV dual-port RAM smoke test passed"); $finish;
  end
endmodule
