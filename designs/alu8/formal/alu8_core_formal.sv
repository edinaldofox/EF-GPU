module alu8_core_formal;
    (* anyconst *) logic [7:0] a;
    (* anyconst *) logic [7:0] b;
    (* anyconst *) logic [2:0] op;

    logic [7:0] y;
    logic       zero;
    logic       carry;
    logic       overflow;
    logic       error;
    logic [7:0] expected_y;
    logic       expected_carry;
    logic       expected_overflow;
    logic       expected_error;
    logic [8:0] expected_extended;
    (* keep *) logic fail;

    alu8_core dut (
        .a(a), .b(b), .op(op), .y(y), .zero(zero), .carry(carry),
        .overflow(overflow), .error(error)
    );

    always_comb begin
        expected_y        = 8'h00;
        expected_carry    = 1'b0;
        expected_overflow = 1'b0;
        expected_error    = 1'b0;
        expected_extended = 9'h000;

        case (op)
            3'b000: begin
                expected_extended = {1'b0, a} + {1'b0, b};
                expected_y        = expected_extended[7:0];
                expected_carry    = expected_extended[8];
                expected_overflow = ~(a[7] ^ b[7]) & (expected_y[7] ^ a[7]);
            end
            3'b001: begin
                expected_y        = a - b;
                expected_carry    = (a >= b);
                expected_overflow = (a[7] ^ b[7]) & (expected_y[7] ^ a[7]);
            end
            3'b010: expected_y = a & b;
            3'b011: expected_y = a | b;
            3'b100: expected_y = a ^ b;
            3'b101: expected_y = {7'b0, ($signed(a) < $signed(b))};
            3'b110: expected_y = a;
            default: expected_error = 1'b1;
        endcase

    end

    assign fail = (y != expected_y) |
                  (zero != (expected_y == 8'h00)) |
                  (carry != expected_carry) |
                  (overflow != expected_overflow) |
                  (error != expected_error);
endmodule
