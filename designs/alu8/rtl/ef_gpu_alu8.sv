module ef_gpu_alu8 (
    input  logic       clk,
    input  logic       rst_n,
    input  logic       en,
    input  logic [7:0] a,
    input  logic [7:0] b,
    input  logic [2:0] op,
    output logic [7:0] y,
    output logic       zero,
    output logic       carry,
    output logic       overflow,
    output logic       error
);
    logic [7:0] core_y;
    logic       core_zero;
    logic       core_carry;
    logic       core_overflow;
    logic       core_error;

    alu8_core core (
        .a(a), .b(b), .op(op), .y(core_y), .zero(core_zero),
        .carry(core_carry), .overflow(core_overflow), .error(core_error)
    );

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            y        <= 8'h00;
            zero     <= 1'b0;
            carry    <= 1'b0;
            overflow <= 1'b0;
            error    <= 1'b0;
        end else if (en) begin
            y        <= core_y;
            zero     <= core_zero;
            carry    <= core_carry;
            overflow <= core_overflow;
            error    <= core_error;
        end
    end
endmodule
