module tb_femtorv_step4;
  reg CLK = 0;
  reg RESET = 0;
  reg RXD = 0;
  wire [4:0] LEDS;
  wire TXD;
  SOC dut(.*);
  always #1 CLK = ~CLK;
  initial begin
    #262146 assert(LEDS == 5'b11000 && TXD == 0);
    #524288 assert(LEDS == 5'b00100 && TXD == 0);
    $display("FemtoRV step 4 instruction decoder passed"); $finish;
  end
endmodule
