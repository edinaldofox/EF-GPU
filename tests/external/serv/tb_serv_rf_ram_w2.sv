module tb_serv_rf_ram_w2;
  logic i_clk=0; logic [1:0] i_wdata; logic i_wen,i_ren; logic [8:0] i_waddr,i_raddr; wire [1:0] o_rdata;
  serv_rf_ram #(.width(2),.csr_regs(0),.depth(512)) dut(.*); always #1 i_clk=~i_clk;
  initial begin i_waddr=9'd16;i_wdata=2'b10;i_wen=1;i_raddr=0;i_ren=0;#2 i_wen=0;i_raddr=16;i_ren=1;#2 if(o_rdata!=2'b10)$fatal(1,"read mismatch");i_raddr=0;#2 if(o_rdata!=0)$fatal(1,"x0 mismatch");$display("SERV RF RAM W2 passed");$finish;end
endmodule
