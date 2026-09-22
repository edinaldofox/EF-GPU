module round_robin2(input logic clk,rst_n,input logic request0,request1,output logic grant0,grant1);
 logic prefer1;assign grant0=request0&&(!request1||!prefer1);assign grant1=request1&&(!request0||prefer1);always_ff@(posedge clk or negedge rst_n)if(!rst_n)prefer1<=0;else if(grant0)prefer1<=1;else if(grant1)prefer1<=0;
endmodule
