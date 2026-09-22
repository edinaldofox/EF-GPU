`timescale 1ns/1ps

module tb_ef_gpu_alu8;
    logic clk = 1'b0;
    logic rst_n;
    logic en;
    logic [7:0] a;
    logic [7:0] b;
    logic [2:0] op;
    logic [7:0] y;
    logic zero;
    logic carry;
    logic overflow;
    logic error;

    ef_gpu_alu8 dut (.*);

    always #5 clk = ~clk;

    task automatic apply_and_check(
        input logic [2:0] next_op,
        input logic [7:0] next_a,
        input logic [7:0] next_b,
        input logic [7:0] expected_y,
        input logic expected_carry,
        input logic expected_overflow,
        input logic expected_error
    );
        begin
            @(negedge clk);
            op = next_op;
            a = next_a;
            b = next_b;
            en = 1'b1;
            @(posedge clk);
            #1;
            assert (y == expected_y) else $fatal(1, "unexpected y");
            assert (zero == (expected_y == 8'h00)) else $fatal(1, "unexpected zero");
            assert (carry == expected_carry) else $fatal(1, "unexpected carry");
            assert (overflow == expected_overflow) else $fatal(1, "unexpected overflow");
            assert (error == expected_error) else $fatal(1, "unexpected error");
        end
    endtask

    initial begin
        rst_n = 1'b0;
        en = 1'b0;
        a = '0;
        b = '0;
        op = '0;
        @(posedge clk);
        #1;
        assert ({y, zero, carry, overflow, error} == '0) else $fatal(1, "reset failed");
        rst_n = 1'b1;

        apply_and_check(3'b000, 8'hff, 8'h01, 8'h00, 1'b1, 1'b0, 1'b0);
        apply_and_check(3'b001, 8'h00, 8'h01, 8'hff, 1'b0, 1'b0, 1'b0);
        apply_and_check(3'b010, 8'ha5, 8'h3c, 8'h24, 1'b0, 1'b0, 1'b0);
        apply_and_check(3'b011, 8'ha5, 8'h3c, 8'hbd, 1'b0, 1'b0, 1'b0);
        apply_and_check(3'b100, 8'ha5, 8'h3c, 8'h99, 1'b0, 1'b0, 1'b0);
        apply_and_check(3'b101, 8'h80, 8'h01, 8'h01, 1'b0, 1'b0, 1'b0);
        apply_and_check(3'b110, 8'h5a, 8'hff, 8'h5a, 1'b0, 1'b0, 1'b0);
        apply_and_check(3'b111, 8'h12, 8'h34, 8'h00, 1'b0, 1'b0, 1'b1);

        @(negedge clk);
        en = 1'b0;
        a = 8'h00;
        b = 8'h00;
        op = 3'b000;
        @(posedge clk);
        #1;
        assert (y == 8'h00 && error) else $fatal(1, "enable retention failed");
        $display("ALU8 testbench passed");
        $finish;
    end
endmodule
