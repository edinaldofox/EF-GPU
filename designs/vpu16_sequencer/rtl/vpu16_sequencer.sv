// In-order 16-word VPU16 program sequencer. Instructions remain stable until accepted.
module vpu16_sequencer (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        host_program_write_enable,
    input  logic [3:0]  host_program_write_address,
    input  logic [15:0] host_program_write_data,
    input  logic        start,
    input  logic [4:0]  program_length,
    input  logic        issue_accepted,
    output logic        issue_valid,
    output logic [15:0] instruction,
    output logic        running,
    output logic        halted,
    output logic [3:0]  program_counter
);
    logic [15:0] instruction_memory [0:15];
    integer index;

    assign issue_valid = running;
    assign instruction = instruction_memory[program_counter];

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (index = 0; index < 16; index = index + 1)
                instruction_memory[index] <= '0;
            running <= 1'b0;
            halted <= 1'b0;
            program_counter <= '0;
        end else begin
            if (host_program_write_enable && !running)
                instruction_memory[host_program_write_address] <= host_program_write_data;
            if (start && !running) begin
                program_counter <= '0;
                if (program_length == 5'd0 || program_length > 5'd16) begin
                    running <= 1'b0;
                    halted <= 1'b1;
                end else begin
                    running <= 1'b1;
                    halted <= 1'b0;
                end
            end else if (running && issue_accepted) begin
                if ({1'b0, program_counter} + 5'd1 >= program_length) begin
                    running <= 1'b0;
                    halted <= 1'b1;
                end else begin
                    program_counter <= program_counter + 4'd1;
                end
            end
        end
    end
endmodule
