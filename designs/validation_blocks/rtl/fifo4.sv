module fifo4(input logic clk,rst_n,input logic write_enable,read_enable,input logic[7:0] write_data,output logic[7:0] read_data,output logic empty,full);
 logic[7:0] memory[0:3];logic[1:0] wp,rp;logic[2:0] used;integer i;
 assign empty=used==0;assign full=used==4;assign read_data=memory[rp];
 always_ff @(posedge clk or negedge rst_n) begin if(!rst_n)begin wp<=0;rp<=0;used<=0;for(i=0;i<4;i=i+1)memory[i]<=0;end else begin case({write_enable&&!full,read_enable&&!empty})2'b10:used<=used+1;2'b01:used<=used-1;default:used<=used;endcase if(write_enable&&!full)begin memory[wp]<=write_data;wp<=wp+1;end if(read_enable&&!empty)rp<=rp+1;end end
endmodule
