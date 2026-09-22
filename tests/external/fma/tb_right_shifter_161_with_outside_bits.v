module tb_right_shifter_161_with_outside_bits;
  reg [160:0] data_to_be_shifted_right;
  reg [7:0] right_shift_amount;
  wire [160:0] right_shifted_data;
  wire [54:0] outside_data;
  right_shifter_161_with_outside_bits dut(.*);
  initial begin
    data_to_be_shifted_right = 161'h200001; right_shift_amount = 91; #1;
    assert({right_shifted_data, outside_data} == ({data_to_be_shifted_right, 55'b0} >> right_shift_amount));
    data_to_be_shifted_right = {161{1'b1}}; right_shift_amount = 128; #1;
    assert({right_shifted_data, outside_data} == ({data_to_be_shifted_right, 55'b0} >> right_shift_amount));
    $display("FMA right shifter 161 passed"); $finish;
  end
endmodule
