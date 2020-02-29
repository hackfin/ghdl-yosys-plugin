from myhdl import *

from lfsr8 import lfsr8

class DPport:
	def __init__(self, awidth, dwidth):
		self.clk = Signal(bool(0))
		self.we = Signal(bool(0))
		self.ce = Signal(bool(0))
		self.addr = Signal(modbv()[awidth:])
		self.write = Signal(modbv()[dwidth:])
		self.read = Signal(modbv()[dwidth:])


@block
def dual_raw_v1(HEXFILE, a, b):
	"Working with dual clock mode"
	mem = [Signal(modbv(0)[len(a.read):]) for i in range(2 ** len(a.addr))]

	if HEXFILE:
		init_inst = meminit(mem, HEXFILE)

	@always(a.clk.posedge)
	def port_a_proc():
		if a.we == 1:
			if __debug__:
				print "Write %2x to %2x" % (a.write, a.addr)
			mem[a.addr].next = a.write
		a.read.next = mem[a.addr];

	@always(b.clk.posedge)
	def port_b_proc():
		b.read.next = mem[b.addr];

	return instances()


@block
def top(rxd_uart, txd_uart, oled, seg, segdp, dip_sw, reset_n, clk_in):
	t_state = enum('S_RESET', 'S_IDLE', 'S_IN', 'S_WR', 'S_RD', 'S_CMP',
	'S_ADVANCE', 'S_ERR')

	reset = ResetSignal(0, 1, isasync=False)

	pa, pb = [ DPport(8, 8) for i in range(2) ]
	state = Signal(t_state.S_RESET)

	iptr, optr = [ Signal(modbv()[8:]) for i in range(2) ]
	act = Signal(bool())
	err = Signal(bool())

	counter = Signal(modbv()[32:])

	data_out, data_in = [ Signal(modbv()[8:]) for i in range(2) ]
	data_gen, data_cmp = [ Signal(modbv()[8:]) for i in range(2) ]
	enable_gen, enable_cmp = [ Signal(bool()) for i in range(2) ]

	lfsr_gen = lfsr8(clk_in, reset, 34, enable_gen, data_gen)
	lfsr_cmp = lfsr8(clk_in, reset, 34, enable_cmp, data_cmp)

	ram_inst = dual_raw_v1(None, pa, pb)

	@always(clk_in.posedge)
	def worker():
		if reset == 1:
			state.next = t_state.S_RESET
			iptr.next = 0
			optr.next = 0
			counter.next = 0
		else:
			if state == t_state.S_RESET:
				state.next = t_state.S_IDLE;
			elif state == t_state.S_IDLE:
				state.next = t_state.S_WR;
			elif state == t_state.S_WR:
				state.next = t_state.S_IN;
			elif state == t_state.S_IN:
				state.next = t_state.S_RD;
			elif state == t_state.S_RD:
				state.next = t_state.S_CMP;
			elif state == t_state.S_ADVANCE:
				state.next = t_state.S_IDLE;
			elif state == t_state.S_CMP:
				if data_cmp == data_out:
					state.next = t_state.S_ADVANCE
				else:
					state.next = t_state.S_ERR
			elif state == t_state.S_ERR:
				pass
			else:
				pass

			if pa.we == 1:
				iptr.next = iptr + 1
			if state == t_state.S_RD:
				optr.next = optr + 1

			counter.next = counter + 1
			act.next = counter[24]
	@always_comb
	def assign():
		reset.next = not reset_n
		data_out.next = pb.read
		pa.clk.next = clk_in
		pb.clk.next = clk_in
		pa.write.next = data_gen
		pa.addr.next = iptr
		pb.addr.next = optr
		if state == t_state.S_IN:
			enable_gen.next = 1
			enable_cmp.next = 0
		elif state == t_state.S_ADVANCE:
			enable_gen.next = 0
			enable_cmp.next = 1
		elif state == t_state.S_RD:
			enable_gen.next = 0
			enable_cmp.next = 0
		else:
			enable_gen.next = 0
			enable_cmp.next = 0

		e = state == t_state.S_ERR
		err.next = e

		pa.we.next = state == t_state.S_WR


	@always_comb
	def led():
		oled.next = concat(~err, intbv(0x7f)[6:], act)
		seg.next = 0xff
		segdp.next = 1
		
	return instances()

@block
def test_top():

	rxd_uart = Signal(bool())
	txd_uart = Signal(bool())
	oled = Signal(modbv()[8:])
	seg = Signal(modbv()[13:])
	segdp = Signal(bool())
	dip_sw = Signal(modbv()[8:])
	reset_n = Signal(bool())
	clk_in = Signal(bool(0))

	top_inst = top(rxd_uart, txd_uart, oled, seg, segdp, dip_sw, reset_n, clk_in)

	top_inst.convert("VHDL")
	top_inst.convert("Verilog")

	@instance
	def start():
		yield delay(10)
		reset_n.next = 0
		yield delay(100)
		reset_n.next = 1
		yield delay(10)
	

#	@always(delay(10))
#	def clkgen():
#		clk_in.next = not clk_in
	
	return instances()

def simulate(tb):
	tb.config_sim(backend = 'myhdl', trace=True)
	tb.run_sim(100000)


def generate():
	pa, pb = [ DPport(12, 8) for i in range(2) ]
	ram_inst = dual_raw_v1(None, pa, pb)
	ram_inst.convert("VHDL")

tb = test_top()
# tb.convert("VHDL")

#convert()
generate()
# simulate(tb)
