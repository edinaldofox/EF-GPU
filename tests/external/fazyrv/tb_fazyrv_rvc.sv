module tb_fazyrv_rvc;
  logic clk_i = 0;
  logic ack_i;
  logic [31:0] instr_c_i;
  logic [31:0] instr_o;
  logic is_rvc_o;
  fazyrv_rvc dut(.*);
  always #1 clk_i = ~clk_i;
  initial begin
    ack_i = 1; instr_c_i = 32'h00000013; #2;
    assert(instr_o == 32'h00000013 && !is_rvc_o);
    instr_c_i = 32'h00000001; #2;
    assert(instr_o == 32'h00000013 && is_rvc_o);
    $display("FazyRV RVC decoder passed"); $finish;
  end
endmodule
