module priority8(input logic [7:0] request,output logic valid,output logic [2:0] index);
 integer i; always_comb begin valid=|request; index='0; for(i=0;i<8;i=i+1) if(request[i]) index=i[2:0]; end
endmodule
