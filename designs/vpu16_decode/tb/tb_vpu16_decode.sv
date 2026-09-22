`timescale 1ns/1ps

module tb_vpu16_decode;
    logic [15:0] instruction;
    logic valid;
    logic is_vmac;
    logic is_vload;
    logic is_vstore;
    logic [2:0] destination;
    logic [2:0] source_a;
    logic [2:0] source_b;
    logic [2:0] source_acc;
    logic [3:0] memory_address;

    vpu16_decode dut (.*);

    task automatic check_decode(
        input logic [15:0] value,
        input logic expected_valid,
        input logic expected_vmac,
        input logic expected_vload,
        input logic expected_vstore,
        input logic [2:0] expected_destination,
        input logic [2:0] expected_source_a,
        input logic [2:0] expected_source_b,
        input logic [2:0] expected_source_acc,
        input logic [3:0] expected_memory_address
    );
        begin
            instruction = value;
            #1 assert (valid == expected_valid) else $fatal(1, "valid mismatch for %h", value);
            assert (is_vmac == expected_vmac) else $fatal(1, "VMAC flag mismatch for %h", value);
            assert (is_vload == expected_vload) else $fatal(1, "VLOAD flag mismatch for %h", value);
            assert (is_vstore == expected_vstore) else $fatal(1, "VSTORE flag mismatch for %h", value);
            assert (destination == expected_destination) else $fatal(1, "destination mismatch for %h", value);
            assert (source_a == expected_source_a) else $fatal(1, "source A mismatch for %h", value);
            assert (source_b == expected_source_b) else $fatal(1, "source B mismatch for %h", value);
            assert (source_acc == expected_source_acc) else $fatal(1, "accumulator mismatch for %h", value);
            assert (memory_address == expected_memory_address) else $fatal(1, "memory address mismatch for %h", value);
        end
    endtask

    initial begin
        check_decode({4'h1, 3'd6, 3'd2, 3'd5, 3'd7}, 1'b1, 1'b1, 1'b0, 1'b0, 3'd6, 3'd2, 3'd5, 3'd7, 4'hf);
        check_decode({4'h2, 3'd5, 5'd0, 4'hd}, 1'b1, 1'b0, 1'b1, 1'b0, 3'd5, 3'd0, 3'd1, 3'd5, 4'hd);
        check_decode({4'h3, 3'd3, 5'd0, 4'h4}, 1'b1, 1'b0, 1'b0, 1'b1, 3'd3, 3'd0, 3'd0, 3'd4, 4'h4);
        check_decode({4'hf, 3'd7, 3'd0, 3'd1, 3'd6}, 1'b0, 1'b0, 1'b0, 1'b0, 3'd7, 3'd0, 3'd1, 3'd6, 4'he);
        $display("VPU16 decode RTL test passed");
        $finish;
    end
endmodule
