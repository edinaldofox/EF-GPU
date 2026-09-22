`timescale 1ns/1ps
module tb_fazyrv_cmp;
  logic [1:0] a_i, b_i; logic inv_msb_i; wire lo_o, gr_o;
  fazyrv_cmp #(.CHUNKSIZE(2)) dut (.*);
  initial begin
    a_i=1; b_i=2; inv_msb_i=0; #1 assert(lo_o && !gr_o) else $fatal(1,"unsigned lower");
    a_i=3; b_i=1; inv_msb_i=0; #1 assert(!lo_o && gr_o) else $fatal(1,"unsigned greater");
    a_i=2'b10; b_i=2'b01; inv_msb_i=1; #1 assert(lo_o && !gr_o) else $fatal(1,"signed lower");
    $display("FazyRV comparator smoke test passed"); $finish;
  end
endmodule
