`timescale 1ns/1ps

// Functional smoke test for the pinned PicoRV32 iterative PCPI multiplier.
// The licensed source is fetched to a temporary directory by the verifier.
module tb_picorv32_pcpi_mul;
  logic clk = 0;
  logic resetn = 0;
  logic pcpi_valid = 0;
  logic [31:0] pcpi_insn = 0;
  logic [31:0] pcpi_rs1 = 0;
  logic [31:0] pcpi_rs2 = 0;
  wire pcpi_wr;
  wire [31:0] pcpi_rd;
  wire pcpi_wait;
  wire pcpi_ready;
  integer cycles;

  picorv32_pcpi_mul dut (.*);
  always #5 clk = ~clk;

  initial begin
    repeat (2) @(posedge clk);
    @(negedge clk);
    resetn = 1;
    pcpi_valid = 1;
    // RISC-V M-extension MUL: funct7=1, funct3=0, opcode=0110011.
    pcpi_insn = 32'b0000001_00000_00000_000_00000_0110011;
    pcpi_rs1 = 7;
    pcpi_rs2 = 9;
    @(negedge clk);
    pcpi_valid = 0;

    cycles = 0;
    while (!pcpi_ready && cycles < 40) begin
      @(posedge clk);
      cycles = cycles + 1;
    end
    assert (pcpi_ready && pcpi_wr) else $fatal(1, "PCPI multiplier did not complete");
    assert (pcpi_rd == 63) else $fatal(1, "PCPI multiplier result was %0d", pcpi_rd);
    $display("PicoRV32 PCPI multiplier smoke test passed in %0d cycles", cycles);
    $finish;
  end
endmodule
