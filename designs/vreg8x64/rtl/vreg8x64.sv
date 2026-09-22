// Eight 64-bit vector registers, each holding four 16-bit SIMD lanes.
// Register zero is a hard-wired zero source and ignores writes.
module vreg8x64 (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        write_enable,
    input  logic [2:0]  write_address,
    input  logic [63:0] write_data,
    input  logic [2:0]  read_address_a,
    input  logic [2:0]  read_address_b,
    output logic [63:0] read_data_a,
    output logic [63:0] read_data_b
);
    logic [63:0] registers [0:7];
    integer index;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (index = 0; index < 8; index = index + 1)
                registers[index] <= '0;
        end else if (write_enable && write_address != 3'd0) begin
            registers[write_address] <= write_data;
        end
    end

    always_comb begin
        read_data_a = read_address_a == 3'd0 ? '0 : registers[read_address_a];
        read_data_b = read_address_b == 3'd0 ? '0 : registers[read_address_b];
    end
endmodule
