`timescale 1ns/1ps
module tb_circuit_primitives;
 logic clk=0,rst_n=0,enable=0,select,right,request0,request1; logic [7:0] a,b,value; logic [2:0] amount; logic [7:0] mux_y,shift_result; logic [3:0] count; logic equal,less_than,grant0,grant1;
 mux2_8 mux(.*,.y(mux_y)); counter4 counter(.*,.value(count)); shifter8 shifter(.*,.result(shift_result)); compare8 compare(.*); arbiter2 arbiter(.*);
 always #5 clk=~clk;
 initial begin
   a=8'h12;b=8'h34;select=0;right=0;amount=3;request0=0;request1=0;
   #1 assert(mux_y==8'h12); select=1; #1 assert(mux_y==8'h34);
   value=8'h03; #1 assert(shift_result==8'h18); right=1; #1 assert(shift_result==8'h00);
   a=8'h03;b=8'h04; #1 assert(!equal&&less_than); b=8'h03; #1 assert(equal&&!less_than);
   request1=1; #1 assert(!grant0&&grant1); request0=1; #1 assert(grant0&&!grant1);
   repeat(2) @(posedge clk); @(negedge clk); rst_n=1; enable=1; repeat(3) @(posedge clk); #1 assert(count==3);
   $display("circuit primitives RTL test passed"); $finish;
 end
endmodule
