module mult8_comb (
    input  logic [7:0]  a,
    input  logic [7:0]  b,
    output logic [15:0] product
);
    // The synthesis tool chooses the adder tree and standard cells for this operator.
    assign product = a * b;
endmodule
