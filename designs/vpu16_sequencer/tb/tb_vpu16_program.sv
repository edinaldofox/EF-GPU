`timescale 1ns/1ps

module tb_vpu16_program;
    logic clk = 1'b0;
    logic rst_n = 1'b0;
    logic host_program_write_enable = 1'b0;
    logic [3:0] host_program_write_address = '0;
    logic [15:0] host_program_write_data = '0;
    logic start = 1'b0;
    logic [4:0] program_length = 5'd5;
    logic issue_valid, issue_accepted, running, halted;
    logic [15:0] instruction;
    logic [3:0] program_counter;
    logic host_memory_write_enable = 1'b0;
    logic [3:0] host_memory_write_address = '0;
    logic [63:0] host_memory_write_data = '0;
    logic core_busy, core_done, issue_ready, queue_full;
    logic [2:0] debug_read_address = '0;
    logic [63:0] debug_read_data;
    logic [3:0] debug_memory_address = '0;
    logic [63:0] debug_memory_data;

    vpu16_sequencer sequencer (.*);
    mini_gpu_vmac_core core (
        .clk, .rst_n,
        .host_write_enable(1'b0), .host_write_address('0), .host_write_data('0),
        .host_memory_write_enable, .host_memory_write_address, .host_memory_write_data,
        .issue_valid, .instruction, .issue_ready, .issue_accepted,
        .busy(core_busy), .done(core_done), .queue_full,
        .debug_read_address, .debug_read_data, .debug_memory_address, .debug_memory_data
    );

    always #5 clk = ~clk;

    task automatic write_program(input logic [3:0] address, input logic [15:0] value);
        begin
            @(negedge clk); host_program_write_enable = 1'b1; host_program_write_address = address; host_program_write_data = value;
            @(negedge clk); host_program_write_enable = 1'b0;
        end
    endtask

    task automatic write_memory(input logic [3:0] address, input logic [63:0] value);
        begin
            @(negedge clk); host_memory_write_enable = 1'b1; host_memory_write_address = address; host_memory_write_data = value;
            @(negedge clk); host_memory_write_enable = 1'b0;
        end
    endtask

    initial begin
        repeat (2) @(posedge clk);
        rst_n = 1'b1;
        write_memory(4'd1, 64'h0004_0003_0002_0001);
        write_memory(4'd2, 64'h0008_0007_0006_0005);
        write_memory(4'd3, 64'h0028_001e_0014_000a);
        write_program(4'd0, {4'h2, 3'd1, 5'd0, 4'd1});
        write_program(4'd1, {4'h2, 3'd2, 5'd0, 4'd2});
        write_program(4'd2, {4'h2, 3'd3, 5'd0, 4'd3});
        write_program(4'd3, {4'h1, 3'd4, 3'd1, 3'd2, 3'd3});
        write_program(4'd4, {4'h3, 3'd4, 5'd0, 4'd4});
        @(negedge clk); start = 1'b1;
        @(negedge clk); start = 1'b0;
        wait (halted);
        @(posedge core_done);
        debug_memory_address = 4'd4;
        #1 assert (debug_memory_data == 64'h0048_0033_0020_000f)
            else $fatal(1, "program result mismatch");
        assert (!running && !core_busy) else $fatal(1, "program did not quiesce");
        $display("VPU16 sequencer integration test passed");
        $finish;
    end
endmodule
