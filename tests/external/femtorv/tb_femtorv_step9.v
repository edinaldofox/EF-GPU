module tb_femtorv_step9;
  reg CLK=0,RESET=0,RXD=0; wire [4:0] LEDS; wire TXD;
  SOC dut(.*); defparam dut.CW.SLOW=4; always #1 CLK=~CLK;
  initial begin #120;if(LEDS!==5'b00100)$fatal(1,"branch-loop writeback mismatch");if(dut.PC!==32'd8)$fatal(1,"BNE must return to loop label");$display("FemtoRV step 9 branch loop passed");$finish;end
endmodule
