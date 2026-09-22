`timescale 1ns/1ps
module tb_benchmark_blocks;
 logic clk=0,rst_n=0,load=0,request0=0,request1=0;logic[7:0]seed=0,state;logic grant0,grant1; lfsr8 lfsr(.*);round_robin2 rr(.*);always #5 clk=~clk;
 initial begin repeat(2)@(posedge clk);@(negedge clk)begin rst_n=1;load=1;seed=8'ha5;end @(posedge clk);@(negedge clk)load=0;#1 assert(state==8'ha5);@(posedge clk);#1 assert(state!=8'ha5);request0=1;request1=1;#1 assert(grant0&&!grant1);@(posedge clk);#1 assert(!grant0&&grant1);$display("benchmark blocks RTL test passed");$finish;end
endmodule
