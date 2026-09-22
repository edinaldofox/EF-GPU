module tb_femtorv_step10;
  reg CLK=0,RESET=1,RXD=0; wire [4:0] LEDS; wire TXD;
  SOC dut(.*); defparam dut.CW.SLOW=4; always #1 CLK=~CLK;
  initial begin #2;RESET=0;#500;if(LEDS!==5'b11111)$fatal(1,"LUI/ORI writeback mismatch");if(dut.PC!==32'd8)$fatal(1,"upper-immediate program counter mismatch");$display("FemtoRV step 10 upper-immediate sequence passed");$finish;end
endmodule
