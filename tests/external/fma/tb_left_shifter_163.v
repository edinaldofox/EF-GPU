module tb_left_shifter_163;
  reg [162:0] data_to_be_shifted_left;
  reg [7:0] left_shift_amount;
  wire [162:0] left_shifted_data;
  left_shifter_163 dut(.*);
  initial begin
    data_to_be_shifted_left = 163'd1; left_shift_amount = 127; #1;
    assert(left_shifted_data == (163'd1 << 127));
    data_to_be_shifted_left = 163'h3; left_shift_amount = 160; #1;
    assert(left_shifted_data == (163'h3 << 160));
    $display("FMA left shifter 163 passed"); $finish;
  end
endmodule
