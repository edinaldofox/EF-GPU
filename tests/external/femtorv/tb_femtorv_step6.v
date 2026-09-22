module tb_femtorv_step6;
  reg CLK=0,RESET=0,RXD=0; wire [4:0] LEDS; wire TXD;
  SOC dut(.*); defparam dut.CW.SLOW=4; always #1 CLK=~CLK;
  initial begin
    #100;
    if(LEDS!==5'b00100)$fatal(1,"ALU sequence writeback mismatch");
    $display("FemtoRV step 6 ALU sequence passed");$finish;
  end
endmodule
