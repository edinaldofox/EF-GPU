module counter4(input logic clk, rst_n, enable, output logic [3:0] value);
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) value <= '0;
        else if (enable) value <= value + 4'd1;
    end
endmodule
