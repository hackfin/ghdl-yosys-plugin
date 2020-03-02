"""
Dual port RAM test suite

(c) 2020   <hackfin@section5.ch>
        
LICENSE: GPL v2

If the IMPLEMENTED variable is set to 1, this construct is expected
to synthesize using GHDL and is tested against the synthesized result.

"""

# 2: Cosimulation test only
IMPLEMENTED = 1

from ramgen import *


@block
def dpram_r2w1_verify(a, b):
	"Verification TB, read before write"
	@instance
	def stim():
		a.ce.next = 1
		b.ce.next = 1
		for i in range(2 ** len(a.addr)):
			yield a.clk.posedge
			a.addr.next = i
			a.write.next = 0xface
			yield a.clk.negedge
			a.we.next = 1
			yield a.clk.negedge
			a.we.next = 0
	
			# On read-after-write, data can not yet be ready on port A:
			if a.read == 0xface:
				raise ValueError, "Mismatch (transparent) A / 0"

			b.addr.next = i
			# Data is ready on port B:
			yield b.clk.posedge
			yield b.clk.posedge
			if b.read != 0xface:
				raise ValueError, "Mismatch B / 1"

			yield a.clk.posedge
			a.addr.next = i
			a.write.next = 0xdead
			yield a.clk.negedge
			a.we.next = 1
			yield a.clk.negedge
			a.we.next = 0
	
			# On read-after-write, data can not yet be ready on port A:
			if a.read == 0xdead:
				raise ValueError, "Mismatch (transparent) A / 1"

			b.addr.next = i
			# Data is ready on port B:
			yield b.clk.posedge
			yield b.clk.posedge
			if b.read != 0xdead:
				raise ValueError, "Mismatch B / 2"


		print "Simulation Done"

	return instances()

# Make sure to use a minimum of 7 address bits to map to a
# DP16KD primitive. Otherwise, TRELLIS DPR16X are emitted.

run(dpram_r2w1, dpram_r2w1_verify, IMPLEMENTED, 7)
