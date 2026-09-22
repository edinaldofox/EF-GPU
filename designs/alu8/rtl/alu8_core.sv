module alu8_core (
    input  logic [7:0] a,
    input  logic [7:0] b,
    input  logic [2:0] op,
    output logic [7:0] y,
    output logic       zero,
    output logic       carry,
    output logic       overflow,
    output logic       error
);
    logic [8:0] extended_result;

    always_comb begin
        y               = 8'h00;
        carry           = 1'b0;
        overflow        = 1'b0;
        error           = 1'b0;
        extended_result = 9'h000;

        unique case (op)
            3'b000: begin // ADD
                extended_result = {1'b0, a} + {1'b0, b};
                y               = extended_result[7:0];
                carry           = extended_result[8];
                overflow        = ~(a[7] ^ b[7]) & (y[7] ^ a[7]);
            end
            3'b001: begin // SUB
                y        = a - b;
                carry    = (a >= b); // one means no unsigned borrow
                overflow = (a[7] ^ b[7]) & (y[7] ^ a[7]);
            end
            3'b010: y = a & b;
            3'b011: y = a | b;
            3'b100: y = a ^ b;
            3'b101: y = {7'b0, ($signed(a) < $signed(b))};
            3'b110: y = a;
            default: error = 1'b1;
        endcase

        zero = (y == 8'h00);
    end
endmodule
