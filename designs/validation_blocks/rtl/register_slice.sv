module register_slice(input logic clk,rst_n,input logic in_valid,input logic [7:0] in_data,output logic in_ready,input logic out_ready,output logic out_valid,output logic [7:0] out_data);
 assign in_ready=!out_valid||out_ready;
 always_ff @(posedge clk or negedge rst_n) begin if(!rst_n) begin out_valid<=0;out_data<='0;end else if(in_ready) begin out_valid<=in_valid;if(in_valid)out_data<=in_data;end end
endmodule
