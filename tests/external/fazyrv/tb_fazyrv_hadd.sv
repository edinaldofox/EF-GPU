`timescale 1ns/1ps
module tb_fazyrv_hadd;
  logic a_i, b_i; wire y_o, c_o;
  fazyrv_hadd dut (.*);
  initial begin
    a_i=0; b_i=0; #1 assert({c_o,y_o}==2'b00) else $fatal(1,"0+0");
    a_i=0; b_i=1; #1 assert({c_o,y_o}==2'b01) else $fatal(1,"0+1");
    a_i=1; b_i=0; #1 assert({c_o,y_o}==2'b01) else $fatal(1,"1+0");
    a_i=1; b_i=1; #1 assert({c_o,y_o}==2'b10) else $fatal(1,"1+1");
    $display("FazyRV half-adder smoke test passed"); $finish;
  end
endmodule
