module tb_femtorv_step8;
  reg CLK=0,RESET=0,RXD=0; wire [4:0] LEDS; wire TXD;
  SOC dut(.*); defparam dut.CW.SLOW=4; always #1 CLK=~CLK;
  initial begin
    #110;
    if(LEDS!==5'b00100)$fatal(1,"jump-loop ALU writeback mismatch");
    if(dut.PC!==32'd4)$fatal(1,"JAL must return to labelled instruction");
    $display("FemtoRV step 8 jump loop passed");$finish;
  end
endmodule
