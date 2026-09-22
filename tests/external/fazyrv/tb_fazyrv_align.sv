`timescale 1ns/1ps
module tb_fazyrv_align;
  logic clk_i=0,rst_in=0,wb_core_stb_i=0,wb_mem_ack_i=0; logic [31:0] wb_core_adr_i=0,wb_mem_dat_i=0;
  wire [31:0] wb_core_dat_o,wb_mem_adr_o; wire wb_core_ack_o,wb_mem_stb_o;
  fazyrv_align dut (.*); always #5 clk_i=~clk_i;
  initial begin
    @(posedge clk_i); @(negedge clk_i); rst_in=1; wb_core_stb_i=1; wb_mem_ack_i=1; wb_mem_dat_i=32'h1122_3344;
    #1 assert(wb_core_ack_o && wb_core_dat_o==32'h1122_3344 && wb_mem_adr_o==0) else $fatal(1,"aligned fetch mismatch");
    @(posedge clk_i); #1; wb_core_adr_i=2;
    #1 assert(!wb_core_ack_o) else $fatal(1,"misaligned first response must wait");
    @(posedge clk_i); #1; wb_mem_dat_i=32'haabb_ccdd;
    #1 assert(wb_core_ack_o && wb_mem_adr_o==4 && wb_core_dat_o==32'hccdd_1122) else $fatal(1,"realigned fetch mismatch");
    $display("FazyRV aligner smoke test passed"); $finish;
  end
endmodule
