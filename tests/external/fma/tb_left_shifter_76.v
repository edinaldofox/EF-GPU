module tb_left_shifter_76;
  reg [75:0] data_to_be_shifted_left;
  reg [6:0] left_shift_amount;
  wire [75:0] left_shifted_data;
  left_shifter_76 dut(.*);
  initial begin
    data_to_be_shifted_left = 76'd1; left_shift_amount = 63; #1;
    assert(left_shifted_data == (76'd1 << 63));
    data_to_be_shifted_left = 76'h3; left_shift_amount = 70; #1;
    assert(left_shifted_data == (76'h3 << 70));
    $display("FMA left shifter 76 passed"); $finish;
  end
endmodule
