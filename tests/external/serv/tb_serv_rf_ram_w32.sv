module tb_serv_rf_ram_w32;
  logic i_clk=0; logic [31:0] i_wdata; logic i_wen,i_ren; logic [4:0] i_waddr,i_raddr; wire [31:0] o_rdata;
  serv_rf_ram #(.width(32),.csr_regs(0),.depth(32)) dut(.*); always #1 i_clk=~i_clk;
  initial begin i_waddr=5'd5;i_wdata=32'ha55a1234;i_wen=1;i_raddr=0;i_ren=0;#2 i_wen=0;i_raddr=5;i_ren=1;#2 if(o_rdata!=32'ha55a1234)$fatal(1,"read mismatch");i_raddr=0;#2 if(o_rdata!=0)$fatal(1,"x0 mismatch");$display("SERV RF RAM W32 passed");$finish;end
endmodule
