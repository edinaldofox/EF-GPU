`timescale 1ns/1ps
module tb_serv_alu;
  logic clk = 0, i_en = 0, i_cnt0 = 0, i_sub = 0, i_cmp_eq = 0, i_cmp_sig = 0;
  logic [1:0] i_bool_op = 0;
  logic [2:0] i_rd_sel = 0;
  logic i_rs1 = 0, i_op_b = 0, i_buf = 0;
  wire o_cmp, o_rd;
  serv_alu dut (.*);
  always #5 clk = ~clk;
  initial begin
    @(posedge clk); #1;
    i_rs1 = 1; i_rd_sel = 3'b001;
    #1 assert (o_rd == 1) else $fatal(1, "serial add mismatch");
    i_op_b = 1; i_rd_sel = 3'b100; i_bool_op = 2'b10;
    #1 assert (o_rd == 1) else $fatal(1, "serial boolean mismatch");
    i_rd_sel = 0; i_cmp_eq = 1; i_cnt0 = 1;
    #1 assert (o_cmp == 1) else $fatal(1, "serial equality mismatch");
    $display("SERV ALU smoke test passed"); $finish;
  end
endmodule
