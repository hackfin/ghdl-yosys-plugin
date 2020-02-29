module tb_test_dpram_r2w1_wt;

reg a_we;
reg [11:0] a_addr;
reg a_clk;
wire [15:0] a_read;
reg a_ce;
reg [15:0] a_write;
reg b_we;
reg [11:0] b_addr;
reg b_clk;
wire [15:0] b_read;
reg b_ce;
reg [15:0] b_write;

initial begin
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

test_dpram_r2w1_wt dut(
    a_we,
    a_addr,
    a_clk,
    a_read,
    a_ce,
    a_write,
    b_we,
    b_addr,
    b_clk,
    b_read,
    b_ce,
    b_write
);

endmodule
