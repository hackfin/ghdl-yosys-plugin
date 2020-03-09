module tb_dpram_r2w1_hl;

reg [8:0] b_addr;
reg [1:0] b_sel;
reg [15:0] b_write;
reg b_clk;
wire [15:0] b_read;
reg b_we;
reg b_ce;
reg [8:0] a_addr;
reg [1:0] a_sel;
reg [15:0] a_write;
reg a_clk;
wire [15:0] a_read;
reg a_we;
reg a_ce;

initial begin
    $from_myhdl(
        b_addr,
        b_sel,
        b_write,
        b_clk,
        b_we,
        b_ce,
        a_addr,
        a_sel,
        a_write,
        a_clk,
        a_we,
        a_ce
    );
    $to_myhdl(
        b_read,
        a_read
    );
end

dpram_r2w1_hl dut(
    b_addr,
    b_sel,
    b_write,
    b_clk,
    b_read,
    b_we,
    b_ce,
    a_addr,
    a_sel,
    a_write,
    a_clk,
    a_read,
    a_we,
    a_ce
);

endmodule
