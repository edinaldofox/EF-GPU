module tb_serv_rf_ram;
  logic i_clk = 0;
  logic [6:0] i_waddr, i_raddr;
  logic [7:0] i_wdata;
  logic i_wen, i_ren;
  wire [7:0] o_rdata;
  serv_rf_ram #(.width(8), .csr_regs(0), .depth(128)) dut(.*);
  always #1 i_clk = ~i_clk;
  initial begin
    i_waddr = 7'd5; i_wdata = 8'ha5; i_wen = 1; i_raddr = 0; i_ren = 0;
    #2 i_wen = 0; i_raddr = 7'd5; i_ren = 1; #2;
    assert(o_rdata == 8'ha5);
    i_raddr = 0; #2;
    assert(o_rdata == 8'h00);
    $display("SERV register-file RAM passed"); $finish;
  end
endmodule
