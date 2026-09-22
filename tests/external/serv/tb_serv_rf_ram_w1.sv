module tb_serv_rf_ram_w1;
  logic i_clk=0, i_wdata, i_wen, i_ren; logic [9:0] i_waddr,i_raddr; wire o_rdata;
  serv_rf_ram #(.width(1),.csr_regs(0),.depth(1024)) dut(.*); always #1 i_clk=~i_clk;
  initial begin i_waddr=10'd32;i_wdata=1;i_wen=1;i_raddr=0;i_ren=0;#2 i_wen=0;i_raddr=32;i_ren=1;#2 if(o_rdata!=1)$fatal(1,"read mismatch");i_raddr=0;#2 if(o_rdata!=0)$fatal(1,"x0 mismatch");$display("SERV RF RAM W1 passed");$finish;end
endmodule
