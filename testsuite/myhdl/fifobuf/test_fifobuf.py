
import sys
import subprocess
sys.path.append("..")

from myhdl import *

from ivl_cosim import *

@block
def fifobuf_mapped(wren, idata, iready, odata, oready, rden, err, reset, clk):

	name = "fifobuffer"
	mapped = name + "_mapped"

 	map_cmd = ['yosys', '-m', 'ghdl',
 	'-p',
 	"""ghdl -gADDR_W=12 -gDATA_W=8 %s.vhdl -e %s;
		show -prefix %s;
		read_verilog ../../../library/wrapper/bram.v;
		synth_ecp5;
		write_verilog %s.v
 	""" % (name, name, name, mapped)]
 	subprocess.call(map_cmd)
	return setupCosimulationIcarus({}, name=mapped, libfiles=LIBFILES, wren=wren,
		idata=idata, iready=iready, odata=odata, oready=oready, rden=rden, err=err,
		reset=reset, clk=clk)

@block
def clkgen(clk, DELAY):
	@always(delay(DELAY))
	def clkgen():
		clk.next = not clk

	return instances()

@block
def fifobuffer(wren, idata, iready, odata, oready, rden, err, reset, clk):
	"Dummy to create TB skeleton"
	@always(clk.posedge)
	def worker():
		if reset:
			odata.next = 0

	return instances()

@block
def fifobuf_tb():
	err = Signal(bool(0))
	clk = Signal(0)
	reset = Signal(bool(0))
	idata, odata = [ Signal(intbv()[8:]) for i in range(2) ]
	iready, oready = [ Signal(bool()) for i in range(2) ]
	rden, wren = [ Signal(bool()) for i in range(2) ]

	# inst_fifobuf = fifobuffer(wren, idata, iready, odata, oready, rden, err, reset, clk)
	inst_fifobuf = fifobuf_mapped(wren, idata, iready, odata, oready, rden, err, reset, clk)

	inst_clkgen = clkgen(clk, 20)

	count = Signal(intbv()[8:])


	@instance
	def testbench_fill():
		rden.next = 0
		wren.next = 0
		reset.next = 1
		yield delay(20)
		reset.next = 0

		yield delay(20)

		for d in [ 0xde, 0xad, 0xbe, 0xef, 0xff, 0x20 ]:
			idata.next = d
			yield clk.negedge
			wren.next = 1
			yield clk.negedge
			wren.next = 0
			yield clk.posedge
			if iready == 0:
				raise ValueError, "not ready"

		yield delay(100)
		if count != 6:
			raise ValueError, "Didn't get data"

	@instance
	def testbench_drain():
		yield oready.posedge


		while 1:
			while oready == 1:
				yield clk.negedge
				rden.next = 1
				yield clk.negedge
				rden.next = 0
				yield clk.posedge
				print "Data", odata
				count.next = count + 1
			yield delay(10)


	return instances()

def test_fifobuf():
	tb = fifobuf_tb()
	tb.config_sim(backend = 'myhdl')
	tb.run_sim(20000)



test_fifobuf()
