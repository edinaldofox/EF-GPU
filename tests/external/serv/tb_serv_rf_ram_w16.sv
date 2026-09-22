module tb_serv_rf_ram_w16;
  logic i_clk=0; logic [15:0] i_wdata; logic i_wen,i_ren; logic [5:0] i_waddr,i_raddr; wire [15:0] o_rdata;
  serv_rf_ram #(.width(16),.csr_regs(0),.depth(64)) dut(.*); always #1 i_clk=~i_clk;
  initial begin i_waddr=6'd5;i_wdata=16'ha55a;i_wen=1;i_raddr=0;i_ren=0;#2 i_wen=0;i_raddr=5;i_ren=1;#2 if(o_rdata!=16'ha55a)$fatal(1,"read mismatch");i_raddr=0;#2 if(o_rdata!=0)$fatal(1,"x0 mismatch");$display("SERV RF RAM W16 passed");$finish;end
endmodule
