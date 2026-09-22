module simd4x8_mac_iter_top (
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
    logic        active;
    logic        mult_done;
    logic        mult_busy;
    logic [63:0] products;
    logic [63:0] saved_acc;
    logic [63:0] mac_value;

    simd4x8_mult_iter4 mults (
        .clk, .rst_n, .start(start && !active), .a, .b,
        .busy(mult_busy), .done(mult_done), .product(products)
    );

    assign mac_value = {
        saved_acc[63:48] + products[63:48],
        saved_acc[47:32] + products[47:32],
        saved_acc[31:16] + products[31:16],
        saved_acc[15:0]  + products[15:0]
    };
    assign busy = active;

    always_ff @(posedge clk) begin
        done <= 1'b0;
        if (!rst_n) begin
            active    <= 1'b0;
            saved_acc <= '0;
            result    <= '0;
        end else if (start && !active) begin
            active    <= 1'b1;
            saved_acc <= acc;
        end else if (active && mult_done) begin
            result <= mac_value;
            active <= 1'b0;
            done   <= 1'b1;
        end
    end
endmodule
