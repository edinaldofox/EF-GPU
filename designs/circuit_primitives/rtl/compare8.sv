module compare8(input logic [7:0] a, b, output logic equal, less_than);
    assign equal = a == b;
    assign less_than = a < b;
endmodule
