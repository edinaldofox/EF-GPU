module mult8_iter (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        start,
    input  logic [7:0]  a,
    input  logic [7:0]  b,
    output logic        busy,
    output logic        done,
    output logic [15:0] product
);
    logic [15:0] accumulator;
    logic [15:0] multiplicand;
    logic [7:0]  multiplier;
    logic [2:0]  count;

    always_ff @(posedge clk) begin
        done <= 1'b0;
        if (!rst_n) begin
            accumulator  <= '0;
            multiplicand <= '0;
            multiplier   <= '0;
            count        <= '0;
            product      <= '0;
            busy         <= 1'b0;
        end else if (!busy) begin
            if (start) begin
                accumulator  <= '0;
                multiplicand <= {8'h00, a};
                multiplier   <= b;
                count        <= '0;
                busy         <= 1'b1;
            end
        end else if (count == 3'd7) begin
            // Include the final partial product before publishing the result.
            product <= accumulator + (multiplier[0] ? multiplicand : 16'h0000);
            busy    <= 1'b0;
            done    <= 1'b1;
        end else begin
            if (multiplier[0])
                accumulator <= accumulator + multiplicand;
            multiplicand <= multiplicand << 1;
            multiplier   <= multiplier >> 1;
            count        <= count + 3'd1;
        end
    end
endmodule
