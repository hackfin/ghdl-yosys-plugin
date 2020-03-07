"""
Dual port RAM test suite

(c) 2020   <hackfin@section5.ch>
        
LICENSE: GPL v2

See ramgen for configuration of 'IMPLEMENTED' variable

"""

from ramgen import *

IMPLEMENTED = IMPLEMENTATION_VHDL_CUSTOM_MAPPED

@block
def dpram_r1w1_verify(a, b):
	"Verification TB, read before write"
	@instance
	def stim():
		a.ce.next = 1
		b.ce.next = 1

		for i in range(4):
			yield a.clk.posedge

		for i in range(2 ** len(a.addr)):
			yield a.clk.posedge
			a.addr.next = i
			a.write.next = 0xface
			yield a.clk.negedge
			a.we.next = 1
			yield a.clk.negedge
			a.we.next = 0
	

			b.addr.next = i
			# Data is ready on port B:
			yield b.clk.posedge
			yield b.clk.posedge
			if b.read != 0xface:
				raise ValueError("Mismatch B / 1")

			yield a.clk.posedge
			a.addr.next = i
			a.write.next = 0xdead
			yield a.clk.negedge
			a.we.next = 1
			yield a.clk.negedge
			a.we.next = 0
	
			b.addr.next = i
			# Data is ready on port B:
			yield b.clk.posedge
			yield b.clk.posedge
			if b.read != 0xdead:
				raise ValueError("Mismatch B / 2")


		print("Simulation Done")

	return instances()

# Make sure to use a minimum of 7 address bits to map to a
# DP16KD primitive
run(dpram_r1w1, dpram_r1w1_verify, IMPLEMENTED, 8)
