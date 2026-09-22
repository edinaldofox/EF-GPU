module lfsr8(input logic clk,rst_n,load,input logic[7:0] seed,output logic[7:0] state);
 always_ff @(posedge clk or negedge rst_n) begin if(!rst_n)state<=8'h1;else if(load)state<=seed;else state<={state[6:0],state[7]^state[5]^state[4]^state[3]};end
endmodule
