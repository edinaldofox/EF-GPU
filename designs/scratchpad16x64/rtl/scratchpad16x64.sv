// Sixteen 64-bit vector words with two combinational read ports.
// This educational scratchpad is implemented as resettable registers, not an SRAM macro.
module scratchpad16x64 (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        write_enable,
    input  logic [3:0]  write_address,
    input  logic [63:0] write_data,
    input  logic [3:0]  read_address_a,
    input  logic [3:0]  read_address_b,
    output logic [63:0] read_data_a,
    output logic [63:0] read_data_b
);
    logic [63:0] memory [0:15];
    integer index;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (index = 0; index < 16; index = index + 1)
                memory[index] <= '0;
        end else if (write_enable) begin
            memory[write_address] <= write_data;
        end
    end

    always_comb begin
        read_data_a = memory[read_address_a];
        read_data_b = memory[read_address_b];
    end
endmodule
