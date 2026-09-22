module tb_right_shifter_74_with_outside_bits;
  reg [73:0] data_to_be_shifted_right;
  reg [6:0] right_shift_amount;
  wire [73:0] right_shifted_data;
  wire [25:0] outside_data;
  right_shifter_74_with_outside_bits dut(.*);
  initial begin
    data_to_be_shifted_right = 74'h200001; right_shift_amount = 37; #1;
    assert({right_shifted_data, outside_data} == ({data_to_be_shifted_right, 26'b0} >> right_shift_amount));
    data_to_be_shifted_right = {74{1'b1}}; right_shift_amount = 64; #1;
    assert({right_shifted_data, outside_data} == ({data_to_be_shifted_right, 26'b0} >> right_shift_amount));
    $display("FMA right shifter 74 passed"); $finish;
  end
endmodule
