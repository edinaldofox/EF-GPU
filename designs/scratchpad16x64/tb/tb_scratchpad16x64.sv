`timescale 1ns/1ps

module tb_scratchpad16x64;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic write_enable = 1'b0;
    logic [3:0] write_address = '0;
    logic [63:0] write_data = '0;
    logic [3:0] read_address_a = '0;
    logic [3:0] read_address_b = '0;
    logic [63:0] read_data_a;
    logic [63:0] read_data_b;

    scratchpad16x64 dut (.*);

    always #5 clk = ~clk;

    task automatic write_word(input logic [3:0] address, input logic [63:0] value);
        begin
            @(negedge clk);
            write_enable = 1'b1;
            write_address = address;
            write_data = value;
            @(negedge clk);
            write_enable = 1'b0;
        end
    endtask

    task automatic check_reads(
        input logic [3:0] address_a,
        input logic [63:0] expected_a,
        input logic [3:0] address_b,
        input logic [63:0] expected_b
    );
        begin
            read_address_a = address_a;
            read_address_b = address_b;
            #1 assert (read_data_a == expected_a)
                else $fatal(1, "read port A mismatch at word %0d", address_a);
            assert (read_data_b == expected_b)
                else $fatal(1, "read port B mismatch at word %0d", address_b);
        end
    endtask

    initial begin
        repeat (2) @(posedge clk);
        rst_n = 1'b1;
        check_reads(4'd0, '0, 4'd15, '0);

        write_word(4'd0, 64'h0011_0022_0033_0044);
        write_word(4'd15, 64'hffee_ddcc_bbaa_9988);
        check_reads(4'd0, 64'h0011_0022_0033_0044, 4'd15, 64'hffee_ddcc_bbaa_9988);

        write_word(4'd0, 64'hdead_beef_cafe_babe);
        check_reads(4'd0, 64'hdead_beef_cafe_babe, 4'd15, 64'hffee_ddcc_bbaa_9988);
        $display("Scratchpad16x64 RTL test passed");
        $finish;
    end
endmodule
