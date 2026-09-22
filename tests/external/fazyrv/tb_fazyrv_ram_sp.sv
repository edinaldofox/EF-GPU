`timescale 1ns/1ps
module tb_fazyrv_ram_sp;
  logic clk_i=0,we_i=0; logic [4:0] waddr_i=0,raddr_i=0; logic [31:0] wdata_i=0; wire [31:0] rdata_o;
  fazyrv_ram_sp dut (.*); always #5 clk_i=~clk_i;
  initial begin
    @(negedge clk_i); we_i=1; waddr_i=5; wdata_i=32'h1234_5678; @(posedge clk_i);
    @(negedge clk_i); we_i=0; raddr_i=5; @(posedge clk_i); #1;
    assert(rdata_o==32'h1234_5678) else $fatal(1,"single-port RAM readback mismatch");
    $display("FazyRV single-port RAM smoke test passed"); $finish;
  end
endmodule
