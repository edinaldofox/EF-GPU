module tb_femtorv_step3;
  reg CLK = 0;
  reg RESET = 0;
  reg RXD = 0;
  wire [4:0] LEDS;
  wire TXD;
  SOC dut(.*);
  always #1 CLK = ~CLK;
  initial begin
    #0 assert(LEDS == 0 && TXD == 0);
    #262146 assert(LEDS == 5'd0 && TXD == 0);
    #524288 assert(LEDS == 5'd1 && TXD == 0);
    $display("FemtoRV step 3 pattern sequencer passed"); $finish;
  end
endmodule
