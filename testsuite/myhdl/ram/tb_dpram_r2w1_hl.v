module tb_dpram_r2w1_hl;

reg b_ce;
reg [15:0] b_write;
wire [15:0] b_read;
reg [1:0] b_sel;
reg b_clk;
reg [8:0] b_addr;
reg b_we;
reg a_ce;
reg [15:0] a_write;
wire [15:0] a_read;
reg [1:0] a_sel;
reg a_clk;
reg [8:0] a_addr;
reg a_we;

initial begin
    $from_myhdl(
        b_ce,
        b_write,
        b_sel,
        b_clk,
        b_addr,
        b_we,
        a_ce,
        a_write,
        a_sel,
        a_clk,
        a_addr,
        a_we
    );
    $to_myhdl(
        b_read,
        a_read
    );
end

dpram_r2w1_hl dut(
    b_ce,
    b_write,
    b_read,
    b_sel,
    b_clk,
    b_addr,
    b_we,
    a_ce,
    a_write,
    a_read,
    a_sel,
    a_clk,
    a_addr,
    a_we
);

endmodule
