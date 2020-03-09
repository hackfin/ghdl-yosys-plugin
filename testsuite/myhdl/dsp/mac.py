
from myhdl import *
import sys
sys.path.append("..")

from ivl_cosim import *

from pyosys import libyosys as ys
from config import *

MAC_IDLE, MAC_ADD, MAC_SUB, MAC_ASSIGN = range(4)

LIBS = YOSYS_TECHLIBS

WIDTH = 18

def FValue(init):
	return intbv(init, min=-(2**(WIDTH-1)), max=(2**(WIDTH-1)))
	# return intbv(init, min=0, max=(2**(WIDTH-1)))


PLUGIN = XHDL_PLUGIN

@block
def mac(clk, ce, mode, a, b, depth, offset, res):
	"""Multiply-Accumulate unit"""

	rm = Signal(intbv(0, min=-(2**(2*WIDTH-1)), max=(2**(2*WIDTH-1))-1))
	acc = Signal(intbv(0, min=-(2**(2*WIDTH+depth)), max=(2**(2*WIDTH+depth))-1))
	n = len(acc) - len(res)

	mode_d = Signal(mode[2:])

	mvalid = Signal(bool(0))
	
	@always(clk.posedge)
	def mul():
		"MAC Stage 1: (Maybe) multiply a with b, result in rm"
		mode_d.next = mode[2:]
		if ce == 1:
			rm.next = a * b
		# elif mode & MAC_FLAG_NOMUL: # No multiplication if set
			# rm.next = a
		else:
			mode_d.next = MAC_IDLE

	@always(clk.posedge)
	def add():
		"MAC Stage 2: (Maybe) accumulate rm in acc"
		if mode_d == MAC_ADD:
			acc.next = acc + rm
		elif mode_d == MAC_SUB:
			acc.next = acc - rm
	#	elif mode_d == MAC_ASSIGN:
	#		acc.next = rm
		elif mode_d == MAC_IDLE:
			acc.next = 0

	@always_comb
	def assign():
		res.next = acc[:n]

	return instances()

@block
def dual_mac(clk, ce, a, b, resa, resb):
	"Arbitrary dummy transform which should optimize to one multiplier"
	# opcode = Signal(FLiXOpcode())
	res = [ Signal(intbv(0, min=-0x80000000, max=0x7fffffff)) \
		for i in range(2) ]
	mac_mode  = [ Signal(intbv(0, min=0, max=8)) for i in range (2)]
	cut = len(res[0]) - len(resa)

	macs = [ mac(clk, ce, mac_mode[i], a, b, 4, 0, res[i]) \
		for i in range(2) ]

	@always(clk.posedge)
	def static_mac_mode():
		mac_mode[0].next = MAC_ADD
		mac_mode[1].next = MAC_SUB

	@always_comb
	def assign():
		resa.next = res[0][:cut]
		resb.next = res[1][:cut]

	return instances()


@block
def single_mac(clk, ce, a, b, resa, resb):
	"Arbitrary dummy transform"


	# opcode = Signal(FLiXOpcode())
	acc = Signal(intbv(0, min=-0x80000000, max=0x7fffffff)) 
	mac_mode  = Signal(intbv(0, min=0, max=8))

	n = len(acc) - len(resa)

	macs = mac(clk, ce, mac_mode, a, b, 0, 0, acc) 

	@always(clk.posedge)
	def static_mac_mode():
		mac_mode.next = MAC_ADD

	@always_comb
	def assign():
		resa.next = acc[:n]
		resb.next = 0

	return instances()


def yosys_mac_mapper(plugin, cmd, files, top, mapped):
	design = ys.Design()
	TECHMAP = 1

	print("Running YOSYS custom mapper")
	if plugin:
		ys.load_plugin(plugin, [])

	ys.run_pass(cmd, design)

	ys.run_pass("read_verilog -lib %s/ecp5/cells_sim.v %s/ecp5/cells_bb.v" % (LIBS, LIBS), design)

	# ys.run_pass("hierarchy -check -top %s" % (top), design)
	ys.run_pass("proc", design)	
	ys.run_pass("flatten", design)	
	ys.run_pass("tribuf -logic", design)	
	ys.run_pass("deminout", design)	
	ys.run_pass("opt_expr", design)	
	ys.run_pass("opt_clean", design)	
	ys.run_pass("check", design)	
	ys.run_pass("opt", design)	
	ys.run_pass("wreduce", design)	
	ys.run_pass("peepopt", design)	
	ys.run_pass("opt_clean", design)	
	ys.run_pass("share", design)	
	ys.run_pass("techmap -map %s/cmp2lut.v -D LUT_WIDTH=4" % YOSYS_TECHLIBS)
	ys.run_pass("opt_expr", design)	
	ys.run_pass("opt_clean", design)	

	# ys.run_pass("show -prefix pre_dsp_%s" % mapped, design)	
#	ys.run_pass("script map_mac.ys")
	ys.run_pass("""techmap -map %s/mul2dsp.v -map %s/ecp5/dsp_map.v \
		-D DSP_A_MAXWIDTH=18 -D DSP_B_MAXWIDTH=18 -D DSP_A_MINWIDTH=2 \
		-D DSP_B_MINWIDTH=2 -D DSP_NAME=\$__MUL18X18""" % (LIBS, LIBS), design)
	# ys.run_pass("chtype -set $mul t:$soft__mul", design)	
	ys.run_pass("opt", design)	
	ys.run_pass("pmuxtree", design)	
	ys.run_pass("stat", design)	
	ys.run_pass("show -prefix %s" % mapped, design)	
	ys.run_pass("write_verilog -norename %s.v" % (mapped), design)

@block
def mac_mapped_vhdl(name, clk, ce, a, b, resa, resb):
	"""Translated MyHDL -> VHDL cosimulation unit, using synth_ecp5
script for default mapping"""
	portmap = locals()
	del portmap['name']

	mapped = name + "_mapped"

	files = "%s.vhd pck_myhdl_011.vhd" % name
	top =  name
	yosys_mac_mapper(PLUGIN, "ghdl %s -e %s" % (files, top), files, top, mapped)

	params = { 'WIDTH' : len(a) }
	options = { "name" : mapped, "libfiles" : LIBFILES} 
	return setupCosimulationIcarus(options, params, portmap)

@block
def mac_mapped_verilog(name, clk, ce, a, b, resa, resb):
	"""Translated MyHDL -> Verilog cosimulation unit"""
	portmap = locals()
	del portmap['name']

	mapped = name + "_mapped"

	files = "%s.v" % name
	top =  name
	yosys_mac_mapper(None, "read_verilog %s" % (files), files, top, mapped)

	params = { 'WIDTH' : len(a) }
	options = { "name" : mapped, "libfiles" : LIBFILES} 
	return setupCosimulationIcarus(options, params, portmap)

@block
def clkgen(clk, DELAY):

	@instance
	def worker():
		while True:
			clk.next = not clk
			yield delay(DELAY)

	return instances()

@block
def dual_mac_verify(clk, ce, a, b, result_a, result_b):
	DELAY_CYCLES = [ (0, 0), (0, 0) ] # Pipeline bubbles for testing
	VALUES = [ (-0x8000, 0x7fff), ( -0x4000, 0x2fff ) ]
	VALUES += DELAY_CYCLES

	RESULTS = DELAY_CYCLES
	RESULTS += [ (-128, 127), (-152, 151) ]

	@instance
	def stim():
		for i in range(20):
			yield(clk.posedge)
		ce.next = 1

		for i, v in enumerate(VALUES):
			print("Checking value set %d" % i)
			yield(clk.negedge)
			a.next = v[0]
			b.next = v[1]
			yield(clk.posedge)
			if result_a != RESULTS[i][0]:
				raise ValueError("Value mismatch: %04x" % result_a.val)
			if result_b != RESULTS[i][1]:
				raise ValueError("Value mismatch: %04x" % result_b.val)


		yield(clk.negedge)
		ce.next = 0

	return instances()

@block
def tb_mac(entity, impl, verify):
	"Co-Simulation test bench"

	reset = ResetSignal(0, 1, isasync = False)

	a, b = [ Signal(FValue(0)) for i in range(2) ]
	result_a, result_b = [ Signal(FValue(0)) for i in range(2) ]
	ref_result_a, ref_result_b = [ Signal(FValue(0)) for i in range(2) ]

	ce = Signal(bool(0))
	clk = Signal(bool(0))

	inst_clkgen = clkgen(clk, 10000)
	ref_dmac = entity(clk, ce, a, b, ref_result_a, ref_result_b)

	sim_dmac   = impl(entity.__name__, clk, ce, a, b, result_a, result_b)
	inst_verify = verify(clk, ce, a, b, result_a, result_b)
	inst_verify_ref = verify(clk, ce, a, b, ref_result_a, ref_result_b)

	return instances()

def testbench(templ, impl, verify):
	tb = tb_mac(templ, impl, verify)
	tb.config_sim(backend = 'myhdl', timescale="1ps", trace=True)
	tb.run_sim(20000000)

def convert(entity):
	a, b = [ Signal(FValue(0)) for i in range(2) ]
	result_a, result_b = [ Signal(FValue(0)) for i in range(2) ]
	ce = Signal(bool(0))
	clk = Signal(bool(0))

	inst_dmac   = entity(clk, ce, a, b, result_a, result_b)
	inst_dmac.convert("VHDL")
	inst_dmac.convert("Verilog")


if __name__ == "__main__":
	ent, verify = dual_mac, dual_mac_verify
	convert(ent)
	testbench(ent, mac_mapped_vhdl, verify)
