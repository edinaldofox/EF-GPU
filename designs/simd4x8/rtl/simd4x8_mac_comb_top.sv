module simd4x8_mac_comb_top (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        start,
    input  logic [31:0] a,
    input  logic [31:0] b,
    input  logic [63:0] acc,
    output logic        busy,
    output logic        done,
    output logic [63:0] result
);
    logic [15:0] p0, p1, p2, p3;
    logic [63:0] mac_value;

    mult8_comb lane0 (.a(a[7:0]),   .b(b[7:0]),   .product(p0));
    mult8_comb lane1 (.a(a[15:8]),  .b(b[15:8]),  .product(p1));
    mult8_comb lane2 (.a(a[23:16]), .b(b[23:16]), .product(p2));
    mult8_comb lane3 (.a(a[31:24]), .b(b[31:24]), .product(p3));

    assign mac_value = {
        acc[63:48] + p3,
        acc[47:32] + p2,
        acc[31:16] + p1,
        acc[15:0]  + p0
    };
    assign busy = 1'b0;

    always_ff @(posedge clk) begin
        done <= 1'b0;
        if (!rst_n) begin
            result <= '0;
        end else if (start) begin
            result <= mac_value;
            done   <= 1'b1;
        end
    end
endmodule
