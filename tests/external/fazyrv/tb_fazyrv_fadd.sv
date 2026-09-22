`timescale 1ns/1ps
module tb_fazyrv_fadd;
  logic a_i, b_i, c_i; wire y_o, c_o, axorb_o, aandb_o;
  fazyrv_fadd dut (.*);
  initial begin
    a_i=0; b_i=0; c_i=0; #1 assert({c_o,y_o}==2'b00 && !axorb_o && !aandb_o) else $fatal(1,"0+0+0");
    a_i=1; b_i=0; c_i=1; #1 assert({c_o,y_o}==2'b10 && axorb_o && !aandb_o) else $fatal(1,"1+0+1");
    a_i=1; b_i=1; c_i=1; #1 assert({c_o,y_o}==2'b11 && !axorb_o && aandb_o) else $fatal(1,"1+1+1");
    $display("FazyRV full-adder smoke test passed"); $finish;
  end
endmodule
