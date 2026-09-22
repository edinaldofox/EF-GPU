`timescale 1ns/1ps
module tb_serv_aligner;
  logic clk = 0, rst = 1, i_ibus_cyc = 0, i_wb_ibus_ack = 0;
  logic [31:0] i_ibus_adr = 0, i_wb_ibus_rdt = 0;
  wire [31:0] o_ibus_rdt, o_wb_ibus_adr;
  wire o_ibus_ack, o_wb_ibus_cyc;
  serv_aligner dut (.*);
  always #5 clk = ~clk;
  initial begin
    repeat (2) @(posedge clk); @(negedge clk); rst = 0;
    i_ibus_cyc = 1; i_wb_ibus_rdt = 32'h1122_3344; i_wb_ibus_ack = 1;
    #1 assert (o_ibus_ack && o_ibus_rdt == 32'h1122_3344 && o_wb_ibus_adr == 0)
       else $fatal(1, "aligned fetch mismatch");
    @(posedge clk); #1; i_ibus_adr = 2;
    #1 assert (!o_ibus_ack) else $fatal(1, "misaligned fetch must wait");
    @(posedge clk); #1; i_wb_ibus_rdt = 32'haabb_ccdd;
    #1 assert (o_ibus_ack && o_wb_ibus_adr == 6 && o_ibus_rdt == 32'hccdd_1122)
       else $fatal(1, "realigned fetch mismatch");
    $display("SERV aligner smoke test passed"); $finish;
  end
endmodule
