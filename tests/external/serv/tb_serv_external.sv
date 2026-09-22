`timescale 1ns/1ps

// Smoke tests for the pinned SERV revision.  The RTL remains in a temporary
// checkout; this testbench is EF-GPU-authored evidence, not a redistributed
// copy of SERV.
module tb_serv_external;
  logic clk = 0;
  logic rst = 1;
  logic [31:0] i_ibus_adr = 0;
  logic i_ibus_cyc = 0;
  logic [31:0] i_wb_ibus_rdt = 0;
  logic i_wb_ibus_ack = 0;
  wire [31:0] o_ibus_rdt;
  wire o_ibus_ack;
  wire [31:0] o_wb_ibus_adr;
  wire o_wb_ibus_cyc;

  logic i_en = 0;
  logic i_cnt0 = 0;
  logic i_sub = 0;
  logic [1:0] i_bool_op = 0;
  logic i_cmp_eq = 0;
  logic i_cmp_sig = 0;
  logic [2:0] i_rd_sel = 0;
  logic i_rs1 = 0;
  logic i_op_b = 0;
  logic i_buf = 0;
  wire o_cmp;
  wire o_rd;

  serv_aligner aligner (.*);
  serv_alu alu (.*);

  always #5 clk = ~clk;

  initial begin
    repeat (2) @(posedge clk);
    @(negedge clk);
    rst = 0;

    // Aligned fetch forwards the address, acknowledge and 32-bit data.
    i_ibus_adr = 32'h0000_0000;
    i_ibus_cyc = 1;
    i_wb_ibus_rdt = 32'h1122_3344;
    i_wb_ibus_ack = 1;
    #1;
    assert (o_wb_ibus_adr == 32'h0000_0000) else $fatal(1, "aligned address mismatch");
    assert (o_wb_ibus_cyc == 1) else $fatal(1, "aligned cycle mismatch");
    assert (o_ibus_ack == 1) else $fatal(1, "aligned acknowledge mismatch");
    assert (o_ibus_rdt == 32'h1122_3344) else $fatal(1, "aligned data mismatch");
    @(posedge clk); #1;

    // A half-word offset causes the following response to be realigned.
    i_ibus_adr = 32'h0000_0002;
    #1 assert (o_ibus_ack == 0) else $fatal(1, "misaligned first response must wait");
    @(posedge clk); #1;
    i_wb_ibus_rdt = 32'haabb_ccdd;
    #1;
    assert (o_wb_ibus_adr == 32'h0000_0006) else $fatal(1, "misaligned address mismatch");
    assert (o_ibus_ack == 1) else $fatal(1, "realigned acknowledge mismatch");
    assert (o_ibus_rdt == 32'hccdd_1122) else $fatal(1, "realigned data mismatch");

    // Seed the serial ALU carry state, then check add, boolean OR and equality.
    i_wb_ibus_ack = 0;
    i_ibus_cyc = 0;
    i_sub = 0;
    @(posedge clk); #1;
    i_rs1 = 1;
    i_op_b = 0;
    i_rd_sel = 3'b001;
    #1 assert (o_rd == 1) else $fatal(1, "serial add mismatch");
    i_op_b = 1;
    i_rd_sel = 3'b100;
    i_bool_op = 2'b10;
    #1 assert (o_rd == 1) else $fatal(1, "serial boolean mismatch");
    i_rd_sel = 0;
    i_cmp_eq = 1;
    i_cnt0 = 1;
    #1 assert (o_cmp == 1) else $fatal(1, "serial equality mismatch");

    $display("SERV external smoke test passed");
    $finish;
  end
endmodule
