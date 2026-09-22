`timescale 1ns/1ps

module tb_simd4x8_mac;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic start = 1'b0;
    logic [31:0] a = '0;
    logic [31:0] b = '0;
    logic [63:0] acc = '0;
    logic comb_busy, comb_done, iter_busy, iter_done;
    logic [63:0] comb_result, iter_result;
    localparam logic [63:0] EXPECTED = {16'd72, 16'd51, 16'd32, 16'd15};

    simd4x8_mac_comb_top comb (.*,
        .busy(comb_busy), .done(comb_done), .result(comb_result));
    simd4x8_mac_iter_top iter (.*,
        .busy(iter_busy), .done(iter_done), .result(iter_result));

    always #5 clk = ~clk;

    initial begin
        repeat (2) @(posedge clk);
        rst_n = 1'b1;
        @(negedge clk);
        // lane 0: 10 + 1*5; lane 1: 20 + 2*6; lane 2: 30 + 3*7; lane 3: 40 + 4*8
        a = {8'd4, 8'd3, 8'd2, 8'd1};
        b = {8'd8, 8'd7, 8'd6, 8'd5};
        acc = {16'd40, 16'd30, 16'd20, 16'd10};
        start = 1'b1;
        @(negedge clk);
        start = 1'b0;

        @(posedge comb_done);
        #1 assert (comb_result == EXPECTED) else $fatal(1, "combinational VMAC mismatch");
        assert (!comb_busy) else $fatal(1, "combinational VMAC must not stall");

        @(posedge iter_busy);
        @(posedge iter_done);
        #1 assert (iter_result == EXPECTED) else $fatal(1, "iterative VMAC mismatch");
        assert (!iter_busy) else $fatal(1, "iterative VMAC busy after done");
        $display("SIMD4x8 VMAC testbench passed");
        $finish;
    end
endmodule
