module popcount8(input logic [7:0] value,output logic [3:0] count);
 integer i; always_comb begin count='0; for(i=0;i<8;i=i+1) count=count+value[i]; end
endmodule
