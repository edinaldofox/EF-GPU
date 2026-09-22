module shifter8(input logic [7:0] value, input logic [2:0] amount, input logic right, output logic [7:0] result);
    assign result = right ? value >> amount : value << amount;
endmodule
