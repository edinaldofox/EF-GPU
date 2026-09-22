module tb_right_shifter_26_with_outside_bits;
  reg [25:0] data_to_be_shifted_right;
  reg [4:0] right_shift_amount;
  wire [25:0] right_shifted_data;
  wire [9:0] outside_data;
  right_shifter_26_with_outside_bits dut(.*);
  initial begin
    data_to_be_shifted_right = 26'h200001; right_shift_amount = 9; #1;
    assert({right_shifted_data, outside_data} == ({data_to_be_shifted_right, 10'b0} >> right_shift_amount));
    data_to_be_shifted_right = 26'h3ffffff; right_shift_amount = 25; #1;
    assert({right_shifted_data, outside_data} == ({data_to_be_shifted_right, 10'b0} >> right_shift_amount));
    $display("FMA right shifter 26 passed"); $finish;
  end
endmodule
