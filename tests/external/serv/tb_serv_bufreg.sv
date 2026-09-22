module tb_serv_bufreg;
  logic i_clk=0,i_cnt0=0,i_cnt1=0,i_cnt_done=0,i_en=0,i_init=0,i_mdu_op=0;
  logic i_rs1_en=0,i_imm_en=0,i_clr_lsb=0,i_shift_op=0,i_right_shift_op=0,i_sh_signed=0;
  logic [2:0] i_shamt=0; logic i_rs1=0,i_imm=0;
  wire [1:0] o_lsb; wire o_q; wire [31:0] o_dbus_adr,o_ext_rs1;
  serv_bufreg dut(.*);
  always #1 i_clk=~i_clk;
  initial begin
    #2;
    i_en=1;i_init=1;i_cnt0=1;
    #2;
    #2;
    i_rs1=1;i_rs1_en=1;
    #2;
    i_rs1=0;
    #2;
    if(o_lsb!==2'b01 || o_q!==1'b1)$fatal(1,"serial low-bit alignment mismatch");
    $display("SERV buffer register passed");$finish;
  end
endmodule
