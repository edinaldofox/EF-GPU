module tb_serv_rf_ram_w4;
  logic i_clk=0; logic [3:0] i_wdata; logic i_wen,i_ren; logic [7:0] i_waddr,i_raddr; wire [3:0] o_rdata;
  serv_rf_ram #(.width(4),.csr_regs(0),.depth(256)) dut(.*); always #1 i_clk=~i_clk;
  initial begin i_waddr=8'd8;i_wdata=4'ha;i_wen=1;i_raddr=0;i_ren=0;#2 i_wen=0;i_raddr=8;i_ren=1;#2 if(o_rdata!=4'ha)$fatal(1,"read mismatch");i_raddr=0;#2 if(o_rdata!=0)$fatal(1,"x0 mismatch");$display("SERV RF RAM W4 passed");$finish;end
endmodule
