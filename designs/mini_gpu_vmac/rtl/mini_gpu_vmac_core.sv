// First integrated EF-GPU execution core: decode, vector registers, VMAC, and scratchpad.
module mini_gpu_vmac_core #(
    parameter bit USE_ITERATIVE = 1'b0,
    parameter bit ENABLE_QUEUE = 1'b0
) (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        host_write_enable,
    input  logic [2:0]  host_write_address,
    input  logic [63:0] host_write_data,
    input  logic        host_memory_write_enable,
    input  logic [3:0]  host_memory_write_address,
    input  logic [63:0] host_memory_write_data,
    input  logic        issue_valid,
    input  logic [15:0] instruction,
    output logic        busy,
    output logic        done,
    output logic        queue_full,
    input  logic [2:0]  debug_read_address,
    output logic [63:0] debug_read_data,
    input  logic [3:0]  debug_memory_address,
    output logic [63:0] debug_memory_data
);
    logic decoded_valid;
    logic decoded_is_vmac;
    logic decoded_is_vload;
    logic decoded_is_vstore;
    logic [2:0] decoded_destination;
    logic [2:0] decoded_source_a;
    logic [2:0] decoded_source_b;
    logic [2:0] decoded_source_acc;
    logic [3:0] decoded_memory_address;
    logic [2:0] pending_destination;
    logic [3:0] pending_memory_address;
    logic [63:0] pending_store_data;
    logic pending_is_vmac;
    logic pending_is_vload;
    logic pending_is_vstore;
    logic [15:0] queued_instruction;
    logic queued_valid;
    logic [15:0] selected_instruction;
    logic direct_issue;
    logic queue_capture;
    logic queue_launch;
    logic issue_accept;
    logic execute_commit;
    logic execute_vmac;
    logic execute_memory;

    logic vreg_write_enable;
    logic [2:0] vreg_write_address;
    logic [63:0] vreg_write_data;
    logic [2:0] vreg_read_address_a;
    logic [63:0] vreg_read_data_a;
    logic [63:0] vreg_read_data_b;
    logic [63:0] vreg_read_data_c;

    logic scratchpad_write_enable;
    logic [3:0] scratchpad_write_address;
    logic [63:0] scratchpad_write_data;
    logic [3:0] scratchpad_read_address_a;
    logic [63:0] scratchpad_read_data_a;
    logic [63:0] scratchpad_read_data_b;

    logic [31:0] vmac_a;
    logic [31:0] vmac_b;
    logic vmac_busy;
    logic vmac_done;
    logic [63:0] vmac_result;

    vpu16_decode decode (
        .instruction(selected_instruction),
        .valid(decoded_valid),
        .is_vmac(decoded_is_vmac),
        .is_vload(decoded_is_vload),
        .is_vstore(decoded_is_vstore),
        .destination(decoded_destination),
        .source_a(decoded_source_a),
        .source_b(decoded_source_b),
        .source_acc(decoded_source_acc),
        .memory_address(decoded_memory_address)
    );

    assign selected_instruction = queue_launch ? queued_instruction : instruction;
    assign direct_issue = issue_valid && decoded_valid && !busy && !queued_valid;
    assign queue_capture = ENABLE_QUEUE && issue_valid && decoded_is_vmac && busy && !queued_valid;
    assign queue_launch = ENABLE_QUEUE && !busy && queued_valid;
    assign issue_accept = direct_issue || queue_launch;
    assign execute_vmac = busy && pending_is_vmac && vmac_done;
    assign execute_memory = busy && (pending_is_vload || pending_is_vstore);
    assign execute_commit = execute_vmac || execute_memory;
    assign queue_full = queued_valid;
    assign vreg_write_enable = execute_vmac || (execute_memory && pending_is_vload) ||
                               (host_write_enable && !busy && !issue_accept);
    assign vreg_write_address = (execute_vmac || (execute_memory && pending_is_vload)) ?
                                pending_destination : host_write_address;
    assign vreg_write_data = execute_vmac ? vmac_result :
                             (execute_memory && pending_is_vload) ? scratchpad_read_data_a : host_write_data;
    // Port A is debug while idle; store reads its source register at issue.
    assign vreg_read_address_a = issue_accept ?
                                 (decoded_is_vmac ? decoded_source_a : decoded_destination) : debug_read_address;

    assign scratchpad_write_enable = (execute_memory && pending_is_vstore) ||
                                     (host_memory_write_enable && !busy && !issue_accept);
    assign scratchpad_write_address = (execute_memory && pending_is_vstore) ?
                                      pending_memory_address : host_memory_write_address;
    assign scratchpad_write_data = (execute_memory && pending_is_vstore) ?
                                   pending_store_data : host_memory_write_data;
    assign scratchpad_read_address_a = issue_accept ? decoded_memory_address : pending_memory_address;
    assign debug_memory_data = scratchpad_read_data_b;

    vreg8x64 registers (
        .clk,
        .rst_n,
        .write_enable(vreg_write_enable),
        .write_address(vreg_write_address),
        .write_data(vreg_write_data),
        .read_address_a(vreg_read_address_a),
        .read_address_b(decoded_source_b),
        .read_address_c(decoded_source_acc),
        .read_data_a(vreg_read_data_a),
        .read_data_b(vreg_read_data_b),
        .read_data_c(vreg_read_data_c)
    );

    scratchpad16x64 scratchpad (
        .clk,
        .rst_n,
        .write_enable(scratchpad_write_enable),
        .write_address(scratchpad_write_address),
        .write_data(scratchpad_write_data),
        .read_address_a(scratchpad_read_address_a),
        .read_address_b(debug_memory_address),
        .read_data_a(scratchpad_read_data_a),
        .read_data_b(scratchpad_read_data_b)
    );

    // A/B vectors store one unsigned byte in the low bits of each 16-bit lane.
    assign vmac_a = {vreg_read_data_a[55:48], vreg_read_data_a[39:32],
                     vreg_read_data_a[23:16], vreg_read_data_a[7:0]};
    assign vmac_b = {vreg_read_data_b[55:48], vreg_read_data_b[39:32],
                     vreg_read_data_b[23:16], vreg_read_data_b[7:0]};
    assign debug_read_data = vreg_read_data_a;

    generate
        if (USE_ITERATIVE) begin : iterative_vmac
            simd4x8_mac_iter_top vmac (
                .clk, .rst_n, .start(issue_accept && decoded_is_vmac), .a(vmac_a), .b(vmac_b), .acc(vreg_read_data_c),
                .busy(vmac_busy), .done(vmac_done), .result(vmac_result)
            );
        end else begin : combinational_vmac
            simd4x8_mac_comb_top vmac (
                .clk, .rst_n, .start(issue_accept && decoded_is_vmac), .a(vmac_a), .b(vmac_b), .acc(vreg_read_data_c),
                .busy(vmac_busy), .done(vmac_done), .result(vmac_result)
            );
        end
    endgenerate

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            busy <= 1'b0;
            done <= 1'b0;
            pending_destination <= '0;
            pending_memory_address <= '0;
            pending_store_data <= '0;
            pending_is_vmac <= 1'b0;
            pending_is_vload <= 1'b0;
            pending_is_vstore <= 1'b0;
            queued_instruction <= '0;
            queued_valid <= 1'b0;
        end else begin
            done <= 1'b0;
            if (queue_capture) begin
                queued_instruction <= instruction;
                queued_valid <= 1'b1;
            end else if (queue_launch) begin
                queued_valid <= 1'b0;
            end
            if (execute_commit) begin
                busy <= 1'b0;
                done <= 1'b1;
            end else if (issue_accept) begin
                busy <= 1'b1;
                pending_destination <= decoded_destination;
                pending_memory_address <= decoded_memory_address;
                pending_store_data <= vreg_read_data_a;
                pending_is_vmac <= decoded_is_vmac;
                pending_is_vload <= decoded_is_vload;
                pending_is_vstore <= decoded_is_vstore;
            end
        end
    end
endmodule
