module tb_dpram_r2w1_hl;

reg [8:0] a_addr;
reg [1:0] a_sel;
reg a_we;
wire [15:0] a_read;
reg a_ce;
reg [15:0] a_write;
reg a_clk;
reg [8:0] b_addr;
reg [1:0] b_sel;
reg b_we;
wire [15:0] b_read;
reg b_ce;
reg [15:0] b_write;
reg b_clk;

initial begin
    $from_myhdl(
        a_addr,
        a_sel,
        a_we,
        a_ce,
        a_write,
        a_clk,
        b_addr,
        b_sel,
        b_we,
        b_ce,
        b_write,
        b_clk
    );
    $to_myhdl(
        a_read,
        b_read
    );
end

dpram_r2w1_hl dut(
    a_addr,
    a_sel,
    a_we,
    a_read,
    a_ce,
    a_write,
    a_clk,
    b_addr,
    b_sel,
    b_we,
    b_read,
    b_ce,
    b_write,
    b_clk
);

endmodule
