	// Port A
	input	wire				clk,
	input	wire				a_we,
	input	wire	[ADDR-1:0]	a_addr,
	input	wire	[DATA-1:0]	a_write,
	output	reg		[DATA-1:0]	a_read,

	// Port B
	input	wire				b_we,
	input	wire	[ADDR-1:0]	b_addr,
	input	wire	[DATA-1:0]	b_write,
	output	reg		[DATA-1:0]	b_read
);

// Shared memory
reg [DATA-1:0] mem [(2**ADDR)-1:0];

reg [ADDR-1:0] addr_b;
reg [ADDR-1:0] addr_a;


// assign a_read = mem[addr_a];
assign b_read = mem[addr_b];

always @(posedge clk) begin: proc_a_write
    addr_a <= a_addr;
    if (a_we) begin
        mem[a_addr] <= a_write;
    end
end

always @(posedge clk) begin: proc_b_read
    addr_b <= b_addr;
end


