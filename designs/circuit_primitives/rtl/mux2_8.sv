module mux2_8(input logic [7:0] a, b, input logic select, output logic [7:0] y);
    assign y = select ? b : a;
endmodule
