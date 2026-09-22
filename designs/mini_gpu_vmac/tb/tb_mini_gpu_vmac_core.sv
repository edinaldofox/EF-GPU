`timescale 1ns/1ps

module tb_mini_gpu_vmac_core;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic host_write_enable = 1'b0;
    logic [2:0] host_write_address = '0;
    logic [63:0] host_write_data = '0;
    logic host_memory_write_enable = 1'b0;
    logic [3:0] host_memory_write_address = '0;
    logic [63:0] host_memory_write_data = '0;
    logic issue_valid = 1'b0;
    logic [15:0] instruction = '0;
    logic busy;
    logic done;
    logic queue_full;
    logic [2:0] debug_read_address = '0;
    logic [63:0] debug_read_data;
    logic [3:0] debug_memory_address = '0;
    logic [63:0] debug_memory_data;

    mini_gpu_vmac_core dut (.*);

    always #5 clk = ~clk;

    task automatic host_write(input logic [2:0] address, input logic [63:0] value);
        begin
            @(negedge clk);
            host_write_enable = 1'b1;
            host_write_address = address;
            host_write_data = value;
            @(negedge clk);
            host_write_enable = 1'b0;
        end
    endtask

    task automatic issue(input logic [15:0] value);
        begin
            @(negedge clk);
            instruction = value;
            issue_valid = 1'b1;
            @(negedge clk);
            issue_valid = 1'b0;
        end
    endtask

    task automatic host_memory_write(input logic [3:0] address, input logic [63:0] value);
        begin
            @(negedge clk);
            host_memory_write_enable = 1'b1;
            host_memory_write_address = address;
            host_memory_write_data = value;
            @(negedge clk);
            host_memory_write_enable = 1'b0;
        end
    endtask

    task automatic check_register(input logic [2:0] address, input logic [63:0] expected);
        begin
            debug_read_address = address;
            #1 assert (debug_read_data == expected)
                else $fatal(1, "register r%0d mismatch", address);
        end
    endtask

    task automatic check_memory(input logic [3:0] address, input logic [63:0] expected);
        begin
            debug_memory_address = address;
            #1 assert (debug_memory_data == expected)
                else $fatal(1, "scratchpad word %0d mismatch", address);
        end
    endtask

    initial begin
        repeat (2) @(posedge clk);
        rst_n = 1'b1;
        host_write(3'd1, 64'h0004_0003_0002_0001);
        host_write(3'd2, 64'h0008_0007_0006_0005);
        host_write(3'd3, 64'h0028_001e_0014_000a);
        host_memory_write(4'd13, 64'h0011_0022_0033_0044);
        check_register(3'd1, 64'h0004_0003_0002_0001);
        check_memory(4'd13, 64'h0011_0022_0033_0044);

        issue({4'h2, 3'd5, 5'd0, 4'd13});
        wait (busy);
        @(posedge done);
        check_register(3'd5, 64'h0011_0022_0033_0044);

        issue({4'h3, 3'd3, 5'd0, 4'd4});
        wait (busy);
        @(posedge done);
        check_memory(4'd4, 64'h0028_001e_0014_000a);

        issue({4'h1, 3'd4, 3'd1, 3'd2, 3'd3});
        wait (busy);
        @(posedge done);
        #1 assert (!busy) else $fatal(1, "core still busy after VMAC completion");
        check_register(3'd4, 64'h0048_0033_0020_000f);

        issue({4'hf, 3'd5, 3'd1, 3'd2, 3'd3});
        repeat (2) @(posedge clk);
        assert (!busy && !done) else $fatal(1, "invalid opcode changed core state");
        check_register(3'd5, 64'h0011_0022_0033_0044);

        issue({4'h1, 3'd0, 3'd1, 3'd2, 3'd3});
        wait (busy);
        @(posedge done);
        check_register(3'd0, '0);
        $display("mini GPU VMAC core RTL test passed");
        $finish;
    end
endmodule
