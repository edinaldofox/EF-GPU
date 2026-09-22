create_clock -name core_clk -period 10.0 [get_ports clk]
set_clock_uncertainty 0.20 [get_clocks core_clk]
set_input_delay 1.0 -clock core_clk [get_ports {rst_n start a[*] b[*] acc[*]}]
set_output_delay 1.0 -clock core_clk [get_ports {busy done result[*]}]
