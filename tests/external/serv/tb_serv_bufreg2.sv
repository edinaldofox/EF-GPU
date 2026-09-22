module tb_serv_bufreg2;
  logic i_clk = 0;
  logic i_en, i_init, i_cnt7, i_cnt_done, i_sh_right;
  logic [1:0] i_lsb, i_bytecnt;
  logic i_op_b_sel, i_shift_op;
  logic i_rs2, i_imm;
  wire o_op_b, o_q, o_sh_done;
  wire [31:0] o_dat;
  logic i_load;
  logic [31:0] i_dat;
  serv_bufreg2 #(.W(1)) dut(.*);
  always #1 i_clk = ~i_clk;
  initial begin
    i_en = 0; i_init = 0; i_cnt7 = 0; i_cnt_done = 0; i_sh_right = 0;
    i_lsb = 0; i_bytecnt = 0; i_op_b_sel = 0; i_shift_op = 0;
    i_rs2 = 1; i_imm = 0; i_load = 1; i_dat = 32'ha1b2c3d4;
    #2 i_load = 0;
    assert(o_dat == 32'ha1b2c3d4 && o_q == 0);
    i_lsb = 2'd1; #1 assert(o_q == 1);
    i_op_b_sel = 0; #1 assert(o_op_b == 0);
    i_op_b_sel = 1; #1 assert(o_op_b == 1);
    $display("SERV buffer register 2 passed"); $finish;
  end
endmodule
