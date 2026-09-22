module tb_serv_rf_ram_w32_c4;
logic i_clk=0;logic [31:0] i_wdata;logic i_wen,i_ren;logic [5:0] i_waddr,i_raddr;wire [31:0] o_rdata;serv_rf_ram #(.width(32),.csr_regs(4),.depth(36)) dut(.*);always #1 i_clk=~i_clk;initial begin i_waddr=1;i_wdata=32'ha55a1234;i_wen=1;i_raddr=0;i_ren=0;#2 i_wen=0;i_raddr=1;i_ren=1;#2 if(o_rdata!=32'ha55a1234)$fatal(1,"read");i_raddr=0;#2 if(o_rdata!=0)$fatal(1,"x0");$display("SERV RF RAM W32 CSR passed");$finish;end
endmodule
