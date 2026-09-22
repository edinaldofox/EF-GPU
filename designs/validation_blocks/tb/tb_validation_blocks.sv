`timescale 1ns/1ps
module tb_validation_blocks;
 logic clk=0,rst_n=0,in_valid=0,out_ready=0,write_enable=0,read_enable=0;logic[7:0]in_data=0,write_data=0,out_data,read_data;logic in_ready,out_valid,empty,full;
 register_slice slice(.*);fifo4 fifo(.*);always #5 clk=~clk;
 initial begin repeat(2)@(posedge clk);@(negedge clk)rst_n=1;in_valid=1;in_data=8'haa;@(posedge clk);#1 assert(out_valid&&out_data==8'haa);@(negedge clk)begin in_valid=0;out_ready=1;end @(posedge clk);#1 assert(in_ready&&!out_valid);@(negedge clk)begin write_enable=1;write_data=8'h11;end @(posedge clk);@(negedge clk)write_data=8'h22;@(posedge clk);@(negedge clk)write_enable=0;#1 assert(!empty&&read_data==8'h11);read_enable=1;@(posedge clk);#1 assert(read_data==8'h22);$display("validation blocks RTL test passed");$finish;end
endmodule
