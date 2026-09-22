`timescale 1ns/1ps
module tb_training_blocks;
 logic[7:0] a,b,value; logic[1:0] op; logic[7:0] sum,y; logic carry,valid; logic[2:0] index; logic[3:0] count; logic[7:0] request;
 add8 add(.*); bitwise8 bits(.*); priority8 priority_encoder(.*); popcount8 pop(.*);
 initial begin
  a=8'hff;b=1;op=0;request=0;value=0;#1 assert(sum==0&&carry); assert(y==1);
  op=1;#1 assert(y==8'hff);op=2;#1 assert(y==8'hfe);op=3;#1 assert(y==0);
  request=8'b00101000;#1 assert(valid&&index==3'd5); value=8'b10101101;#1 assert(count==5);
  $display("training blocks RTL test passed");$finish;
 end
endmodule
