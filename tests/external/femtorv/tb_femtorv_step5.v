module tb_femtorv_step5;
reg CLK=0,RESET=0,RXD=0; wire [4:0] LEDS; wire TXD; SOC dut(.*); always #1 CLK=~CLK;
initial begin #262146 if(LEDS!=5'b00010)$fatal(1,"fetch-register state");#524288 if(LEDS!=5'b00100)$fatal(1,"execute state");#524288 if(LEDS!=5'b00001)$fatal(1,"fetch state");$display("FemtoRV step 5 state machine passed");$finish;end
endmodule
