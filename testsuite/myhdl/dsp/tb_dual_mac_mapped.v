`timescale 1ns/10ps

module tb_dual_mac_mapped #(
	parameter WIDTH = 18
);

reg clk;
reg ce;
reg [WIDTH-1:0] a;
reg [WIDTH-1:0] b;
wire [WIDTH-1:0] resa;
wire [WIDTH-1:0] resb;

initial begin
	$dumpfile("dual_mac.vcd");
    $dumpvars(0,tb_dual_mac_mapped);

    $from_myhdl(
        clk,
        ce,
        a,
        b
    );
    $to_myhdl(
        resa,
        resb
    );
end

dual_mac dut(
    clk,
    ce,
    a,
    b,
    resa,
    resb
);

endmodule
