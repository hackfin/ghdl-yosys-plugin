(* blackbox *)

module \$__ECP5_DP16KD (CLK2, CLK3,
    A1ADDR, A1READ, A1WRITE, A1CE, A1WE,
	B1ADDR, B1READ, B1WRITE, B1CE, B1WE);

	parameter CFG_ABITS = 10;
	parameter CFG_DBITS = 18;
	parameter CFG_ENABLE_A = 2;
	parameter CFG_ENABLE_B = 2;

	parameter CLKPOL2 = 1;
	parameter CLKPOL3 = 1;
	parameter [18431:0] INIT = 18432'bx;
	parameter TRANSP2 = 0;

	input CLK2;
	input CLK3;

	input [CFG_ABITS-1:0] A1ADDR;
	input [CFG_DBITS-1:0] A1WRITE;
	input A1CE;
	input A1WE;
	// input [CFG_ENABLE_A-1:0] A1EN;
	output [CFG_DBITS-1:0] A1READ;

	input [CFG_ABITS-1:0] B1ADDR;
	input [CFG_DBITS-1:0] B1WRITE;
	// input [CFG_ENABLE_B-1:0] B1EN;
	input B1CE;
	input B1WE;
	output [CFG_DBITS-1:0] B1READ;

endmodule
