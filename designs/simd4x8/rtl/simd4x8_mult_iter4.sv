module simd4x8_mult_iter4 (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        start,
    input  logic [31:0] a,
    input  logic [31:0] b,
    output logic        busy,
    output logic        done,
    output logic [63:0] product
);
    logic busy0, busy1, busy2, busy3;
    logic done0, done1, done2, done3;

    mult8_iter lane0 (.clk, .rst_n, .start, .a(a[7:0]),   .b(b[7:0]),   .busy(busy0), .done(done0), .product(product[15:0]));
    mult8_iter lane1 (.clk, .rst_n, .start, .a(a[15:8]),  .b(b[15:8]),  .busy(busy1), .done(done1), .product(product[31:16]));
    mult8_iter lane2 (.clk, .rst_n, .start, .a(a[23:16]), .b(b[23:16]), .busy(busy2), .done(done2), .product(product[47:32]));
    mult8_iter lane3 (.clk, .rst_n, .start, .a(a[31:24]), .b(b[31:24]), .busy(busy3), .done(done3), .product(product[63:48]));

    assign busy = busy0 | busy1 | busy2 | busy3;
    assign done = done0 & done1 & done2 & done3;
endmodule
