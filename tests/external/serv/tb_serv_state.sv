module tb_serv_state;
  logic i_clk=0,i_rst=1,i_new_irq=0,i_alu_cmp=0,i_ctrl_misalign=0,i_sh_done=0,i_mem_misalign=0;
  logic i_bne_or_bge=0,i_cond_branch=0,i_dbus_en=0,i_two_stage_op=0,i_branch_op=0,i_shift_op=0,i_sh_right=0,i_alu_rd_sel1=0,i_rd_alu_en=0,i_e_op=0,i_rd_op=0,i_mdu_op=0,i_mdu_ready=0,i_dbus_ack=0,i_ibus_ack=0,i_rf_ready=0;
  wire o_init,o_cnt_en,o_cnt0,o_ibus_cyc;
  serv_state dut(.i_clk,.i_rst,.i_new_irq,.i_alu_cmp,.i_ctrl_misalign,.i_sh_done,.i_mem_misalign,.i_bne_or_bge,.i_cond_branch,.i_dbus_en,.i_two_stage_op,.i_branch_op,.i_shift_op,.i_sh_right,.i_alu_rd_sel1,.i_rd_alu_en,.i_e_op,.i_rd_op,.i_mdu_op,.i_mdu_ready,.i_dbus_ack,.i_ibus_ack,.i_rf_ready,.o_init,.o_cnt_en,.o_cnt0,.o_ibus_cyc);
  always #1 i_clk=~i_clk;
  initial begin
    #2;if(o_ibus_cyc!==1'b0)$fatal(1,"reset must gate instruction bus");
    i_rst=0;#1;if(o_ibus_cyc!==1'b1)$fatal(1,"reset release must request instruction fetch");
    i_ibus_ack=1;#2;i_ibus_ack=0;if(o_ibus_cyc!==1'b0)$fatal(1,"instruction acknowledgement must end bus cycle");
    i_two_stage_op=1;#1;if(o_init!==1'b1)$fatal(1,"two-stage operation must enter initialization");
    i_rf_ready=1;#2;i_rf_ready=0;if(!(o_cnt_en&&o_cnt0))$fatal(1,"register-file ready must start serial counter");
    $display("SERV state controller passed");$finish;
  end
endmodule
