module tb_serv_decode;
  logic clk=0,i_wb_en=0; logic [31:2] i_wb_rdt=0;
  wire o_dbus_en,o_rd_op,o_rd_mem_en,o_branch_op,o_cond_branch,o_bufreg_clr_lsb;
  wire o_mem_signed,o_mem_word,o_mem_half,o_mem_cmd,o_op_b_source;
  serv_decode dut(.clk,.i_wb_rdt,.i_wb_en,.o_dbus_en,.o_rd_op,.o_rd_mem_en,.o_branch_op,.o_cond_branch,.o_bufreg_clr_lsb,.o_mem_signed,.o_mem_word,.o_mem_half,.o_mem_cmd,.o_op_b_source);
  always #1 clk=~clk;
  task load_instruction(input logic [31:0] instruction);
    i_wb_rdt=instruction>>2;i_wb_en=1;#2;i_wb_en=0;
  endtask
  initial begin
    load_instruction(32'h00002083);
    if(!(o_dbus_en&&o_rd_op&&o_rd_mem_en&&o_mem_signed&&o_mem_word&&!o_mem_half&&!o_mem_cmd))$fatal(1,"load decode mismatch");
    load_instruction(32'h00102023);
    if(!(o_dbus_en&&!o_rd_op&&o_rd_mem_en&&o_mem_cmd&&o_mem_signed&&o_mem_word&&o_op_b_source))$fatal(1,"store decode mismatch");
    load_instruction(32'h00000063);
    if(!(o_branch_op&&o_cond_branch&&o_bufreg_clr_lsb&&!o_rd_op&&!o_dbus_en))$fatal(1,"branch decode mismatch");
    $display("SERV instruction decoder passed");$finish;
  end
endmodule
