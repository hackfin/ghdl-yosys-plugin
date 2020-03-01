"""
Dual port RAM test suite

Test case RAM generators module

(c) 2020   <hackfin@section5.ch>
        
LICENSE: GPL v2

"""

from myhdl import *
import subprocess

import sys
sys.path.append("..")

from ivl_cosim import *


class DPport:
	def __init__(self, awidth, dwidth):
		self.clk = Signal(bool(0))
		self.we = Signal(bool(0))
		self.ce = Signal(bool(0))
		self.addr = Signal(modbv()[awidth:])
		self.write = Signal(modbv()[dwidth:])
		self.read = Signal(modbv()[dwidth:])


@block
def dummy(a, b):
	def worker():
		pass

	return instances()


@block
def meminit(mem, hexfile):
	size = len(mem)
	init_values = tuple([int(ss.val) for ss in mem])
	wsize = len(mem[0])

	@instance
	def initialize():
		for i in range(size):
			mem[i].next = init_values[i]
		yield delay(10)

	return instances()


meminit.verilog_code = """
initial begin
	$$readmemh(\"$hexfile\", $mem, $size);
end
"""

# Disabled memory init code for now

if 0:
	meminit.vhdl_code = """
		type ram_t is array(0 to $size-1) of unsigned($wsize-1 downto 0);

		impure function init_ram() return ram_t is
			file hexfile : text open read_mode is "$hexfile";
			variable l : line;
			variable hw : unsigned($wsize-1 downto 0);
			variable initmem : ram_t := (others => (others => '0'));
		begin
			for i in 0 to $size-1 loop
				exit when endfile(hexfile);
				readline(hexfile, l);
				report "read: " & l.all;
				hread(l, hw);
				initmem(i) := hw;
			end loop;

			return initmem;
		end function;
	"""


@block
def dpram_test(a, b, ent, CLKMODE, HEXFILE = False, verify = False):

	"Entities that are 'required' to work"

	# This is grown into duplicates, due to different clk domains
	# Would not be necessary for the ECP5.
	# ram_raw1 = dual_raw_v0(a, b)

	# This one has a common clock and translates fine
	# ram_raw2 = dual_raw_v0(pa, pb)

	# Both port clocks the same:
	if CLKMODE:
		b.clk.next = a.clk

	ram_tdp = ent(a, b, HEXFILE)

	return instances()

@block
def ram_v(name, a, b, HEXFILE):
	params = { }
	return setupCosimulationIcarus(params, name=name, a_clk=a.clk, a_ce=a.ce, a_we=a.we,  a_addr=a.addr, a_read=a.read, a_write=a.write, b_clk=b.clk, b_ce=b.ce, b_we=b.we, b_addr=b.addr, b_read=b.read, b_write=b.write)


@block
def ram_mapped_vhdl(name, a, b, HEXFILE = False):
	mapped = name + "_mapped"

 	map_cmd = ['yosys', '-m', 'ghdl',
 	'-p',
 	"""ghdl pck_myhdl_011.vhd %s.vhd -e %s;
		show -prefix %s;
		synth_ecp5;
		show -prefix %s;
		write_verilog %s.v
 	""" % (name, name, name, mapped, mapped)]
 	subprocess.call(map_cmd)
	params = { 'ADDR_W' : len(a.addr) }

	return setupCosimulationIcarus(params, name=mapped, libfiles=LIBFILES, a_clk=a.clk, a_ce=a.ce, a_we=a.we,  a_addr=a.addr, a_read=a.read, a_write=a.write, b_clk=b.clk, b_ce=b.ce, b_we=b.we, b_addr=b.addr, b_read=b.read, b_write=b.write)
	
@block
def clkgen(clka, clkb, DELAY_A, DELAY_B):

	@instance
	def clkgen_a():
		while True:
			clka.next = not clka
			yield delay(DELAY_A)

	if DELAY_A == DELAY_B:
		@always_comb
		def assign():
			clkb.next = clka

	else:

		@instance
		def clkgen_b():
			while True:
				clkb.next = not clkb
				yield delay(DELAY_B)


	return instances()

############################################################################
# LIBRARY
#

@block
def dpram_r1w1(a, b, HEXFILE = None, USE_CE = False):
	"Synthesizing one read one write port DPRAM, synchronous read b4 write"
	mem = [Signal(modbv(0)[len(a.read):]) for i in range(2 ** len(a.addr))]

	if HEXFILE:
		init_inst = meminit(mem, HEXFILE)

	if USE_CE:
		@always(a.clk.posedge)
		def porta_proc():
			if a.ce:
				if a.we:
					if __debug__:
						print "Writing to ", a.addr
					mem[a.addr].next = a.write

		@always(b.clk.posedge)
		def portb_proc():
			if b.ce:
				b.read.next = mem[b.addr]
	else:
		@always(a.clk.posedge)
		def porta_proc():
			if a.we:
				if __debug__:
					print "Writing to ", a.addr
				mem[a.addr].next = a.write

		@always(b.clk.posedge)
		def portb_proc():
			b.read.next = mem[b.addr]


	return instances()



@block
def dpram_r2w1(a, b, HEXFILE = False, USE_CE = False):
	"Synthesizing two read one write port DPRAM, synchronous read b4 write"
	mem = [Signal(modbv(0)[len(a.read):]) for i in range(2 ** len(a.addr))]

	if HEXFILE:
		init_inst = meminit(mem, HEXFILE)

	if USE_CE:
		@always(a.clk.posedge)
		def porta_proc():
			if a.ce:
				if a.we:
					if __debug__:
						print "Writing to ", a.addr
					mem[a.addr].next = a.write
				else:
					a.read.next = mem[a.addr]

		@always(b.clk.posedge)
		def portb_proc():
			if b.ce:
				b.read.next = mem[b.addr]
	else:
		@always(a.clk.posedge)
		def porta_proc():
			if a.we:
				if __debug__:
					print "Writing to ", a.addr
				mem[a.addr].next = a.write
			else:
				a.read.next = mem[a.addr]

		@always(b.clk.posedge)
		def portb_proc():
			b.read.next = mem[b.addr]

	return instances()

@block
def dpram_r2w1_wt(a, b, HEXFILE = False, USE_CE = False):
	"Two read one write port DPRAM, writethrough"
	mem = [Signal(modbv(0)[len(a.read):]) for i in range(2 ** len(a.addr))]

	if HEXFILE:
		init_inst = meminit(mem, HEXFILE)

	if USE_CE:
		@always(a.clk.posedge)
		def porta_proc():
			if a.ce:
				if a.we:
					mem[a.addr].next = a.write
					a.read.next = a.write
				else:
					a.read.next = mem[a.addr]

		@always(b.clk.posedge)
		def portb_proc():
			if b.ce:
				b.read.next = mem[b.addr]
	else:
		@always(a.clk.posedge)
		def porta_proc():
			if a.we:
				mem[a.addr].next = a.write
				a.read.next = a.write
			else:
				a.read.next = mem[a.addr]

		@always(b.clk.posedge)
		def portb_proc():
			b.read.next = mem[b.addr]

	return instances()
	
############################################################################

@block
def dpram_tb(ent, ent_v, CLKMODE, HEXFILE, verify, addrbits):
	"Test with Co-Simulation"

	a = DPport(addrbits, 16)
	b = DPport(addrbits, 16)

	# Both port clocks the same:

	if ent_v:
		# Note: Trace can be flaky when using the wrong verilog version
		# Use a very recent release with MyHDL VPI support.
		ram_tdp_v = ent_v(ent.__name__, a, b, HEXFILE)
	else:
		ram_tdp = ent(a, b, HEXFILE)

 
	inst_clkgen = clkgen(a.clk, b.clk, 10, 11)
	inst_verify = verify(a, b)

	return instances()

def convert(addrbits):
	# d = dpram16_init(a, b)

	RAM_LIST = [ dpram_r1w1, dpram_r2w1, dpram_r2w1_wt]

	for ent in RAM_LIST:
		a = DPport(addrbits, 16)
		b = DPport(addrbits, 16)

		dp = dpram_test(a, b, ent, False, False)
		s = "test_" + ent.__name__
		dp.convert("VHDL", name=s)
		dp.convert("Verilog", name=s)

		e = ent(a, b)
		e.convert("VHDL", name=ent.__name__)
		e.convert("Verilog", name=ent.__name__)

	# test_init = dpram_r2w1(a, b, "../sw/bootrom_l.hex")
	# test_init.convert("VHDL")
	# test_init.convert("Verilog")

def testbench(which, verify, MODE=0, ADDRBITS=6):
	"Test bench to co-simulate against conversion/synthesis results"
	if MODE == 1:
		# Use VHDL RAM model for mapping, co-simulate synthesized Verilog
		# output
		r = ram_mapped_vhdl
	elif MODE == 2:
		# Use translated Verilog model:
		r = ram_v
	else:
		r = None

	# Unfortunately, we can only run one sim instance. Don't try...

	tb = dpram_tb(which, r, False, False, verify, ADDRBITS)
	# tb.convert("Verilog", name="tb")
	tb.config_sim(backend = 'myhdl', trace=True)
	tb.run_sim(20000)

if __name__ == '__main__':
	convert(7)
