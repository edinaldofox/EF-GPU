module tb_femtorv_step7;
  reg CLK=0,RESET=0,RXD=0; wire [4:0] LEDS; wire TXD;
  SOC dut(.*); defparam dut.CW.SLOW=4; always #1 CLK=~CLK;
  initial begin
    #100;
    if(LEDS!==5'b00100)$fatal(1,"assembly-program ALU writeback mismatch");
    $display("FemtoRV step 7 assembly ALU sequence passed");$finish;
  end
endmodule
