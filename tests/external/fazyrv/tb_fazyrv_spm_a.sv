`timescale 1ns/1ps
module tb_fazyrv_spm_a;
  logic clk_i=0,shft_i=0; logic [1:0] ser_i=0; logic [31:0] source_data=32'h1234_5678; wire [31:0] par_o; integer i;
  fazyrv_spm_a #(.CHUNKSIZE(2)) dut (.*); always #5 clk_i=~clk_i;
  initial begin
    for (i=0; i<16; i=i+1) begin
      @(negedge clk_i); shft_i=1; ser_i=source_data[i*2 +: 2]; @(posedge clk_i);
    end
    #1 assert(par_o==32'h1234_5678) else $fatal(1,"address serialization mismatch");
    $display("FazyRV address serializer smoke test passed"); $finish;
  end
endmodule
