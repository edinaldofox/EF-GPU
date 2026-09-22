module tb_femtorv_step1;
  reg CLK = 0;
  reg RESET = 0;
  reg RXD = 0;
  wire [4:0] LEDS;
  wire TXD;
  SOC dut(.*);
  always #1 CLK = ~CLK;
  initial begin
    #0 assert(LEDS == 0 && TXD == 0);
    #2 assert(LEDS == 5'd1 && TXD == 0);
    #4 assert(LEDS == 5'd3 && TXD == 0);
    $display("FemtoRV step 1 counter passed"); $finish;
  end
endmodule
