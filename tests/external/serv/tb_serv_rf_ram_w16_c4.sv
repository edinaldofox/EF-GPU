module tb_serv_rf_ram_w16_c4;
logic i_clk=0;logic [15:0] i_wdata;logic i_wen,i_ren;logic [6:0] i_waddr,i_raddr;wire [15:0] o_rdata;serv_rf_ram #(.width(16),.csr_regs(4),.depth(72)) dut(.*);always #1 i_clk=~i_clk;initial begin i_waddr=2;i_wdata=16'ha55a;i_wen=1;i_raddr=0;i_ren=0;#2 i_wen=0;i_raddr=2;i_ren=1;#2 if(o_rdata!=16'ha55a)$fatal(1,"read");i_raddr=0;#2 if(o_rdata!=0)$fatal(1,"x0");$display("SERV RF RAM W16 CSR passed");$finish;end
endmodule
