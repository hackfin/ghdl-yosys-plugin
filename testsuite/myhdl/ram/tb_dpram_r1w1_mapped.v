`timescale 1ns/10ps

module tb_dpram_r1w1_mapped #(
	parameter ADDR_W = 12
);

reg a_we;
reg [ADDR_W-1:0] a_addr;
reg a_clk;
wire [15:0] a_read;
reg a_ce;
reg [15:0] a_write;
reg b_we;
reg [ADDR_W-1:0] b_addr;
reg b_clk;
wire [15:0] b_read;
reg b_ce;
reg [15:0] b_write;

initial begin
    $dumpfile("dpram.vcd");
    $dumpvars(0,tb_dpram_r1w1_mapped);

    $from_myhdl(
        a_we,
        a_addr,
        a_clk,
        a_ce,
        a_write,
        b_we,
        b_addr,
        b_clk,
        b_ce,
        b_write
    );
    $to_myhdl(
        a_read,
        b_read
    );
end

dpram_r1w1 dut(
    .a_ce       ( a_ce ),
    .a_write    ( a_write ),
    .a_read     ( a_read ),
    .a_clk      ( a_clk ),
    .a_addr     ( a_addr ),
    .a_we       ( a_we ),
    .b_ce       ( b_ce ),
    .b_write    ( b_write ),
    .b_clk      ( b_clk ),
    .b_addr     ( b_addr ),
    .b_we       ( b_we ),
    .b_read     ( b_read )
);

endmodule
