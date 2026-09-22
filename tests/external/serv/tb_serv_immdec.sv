module tb_serv_immdec;
  logic i_clk = 0;
  logic i_cnt_en, i_cnt_done;
  logic [3:0] i_immdec_en, i_ctrl;
  logic i_csr_imm_en, i_wb_en;
  logic [31:7] i_wb_rdt;
  wire [4:0] o_rd_addr, o_rs1_addr, o_rs2_addr;
  wire o_csr_imm, o_imm;
  serv_immdec dut(.*);
  always #1 i_clk = ~i_clk;
  initial begin
    i_cnt_en = 0; i_cnt_done = 0; i_immdec_en = 0; i_csr_imm_en = 0; i_ctrl = 0;
    i_wb_en = 1; i_wb_rdt = {25{1'b1}};
    #2 i_wb_en = 0;
    if (o_rd_addr != 5'h1f || o_rs1_addr != 5'h1f || o_rs2_addr != 5'h1f) $fatal(1, "register address decode mismatch");
    if (o_csr_imm != 1 || o_imm != 1) $fatal(1, "immediate decode mismatch");
    i_csr_imm_en = 1; i_ctrl = 4'b0001; #1;
    if (o_imm != 1) $fatal(1, "CSR immediate selection mismatch");
    $display("SERV immediate decoder passed"); $finish;
  end
endmodule
