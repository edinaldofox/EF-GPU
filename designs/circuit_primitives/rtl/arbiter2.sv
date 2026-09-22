module arbiter2(input logic request0, request1, output logic grant0, grant1);
    assign grant0 = request0;
    assign grant1 = !request0 && request1;
endmodule
