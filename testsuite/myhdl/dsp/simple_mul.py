from myhdl import *

MAC_IDLE, MAC_ADD, MAC_SUB, MAC_ASSIGN = range(4)

WIDTH = 18

def FValue(init):
	return intbv(init, min=-(2**(WIDTH-1)), max=(2**(WIDTH-1)))


@block
def multiplier(clk, ce, a, b, res):
	rm = Signal(intbv(0, min=-(2**(2*WIDTH-1)), max=(2**(2*WIDTH-1))-1))
	acc = Signal(intbv(0, min=-(2**(2*WIDTH+4)), max=(2**(2*WIDTH+4))-1))
	n = len(acc) - len(res)

	ce_d = Signal(bool())

	@always(clk.posedge)
	def stage_mul():
		if ce:
			rm.next = a * b

		if ce_d:
			acc.next = acc + rm

		ce_d.next = ce

	@always_comb
	def assign():
		res.next = acc[:n]

	return instances()

@block
def mac(clk, ce, mode, a, b, res):
	"""Multiply-Accumulate unit"""

	acc = Signal(intbv(0, min=-(2**(2*WIDTH+4)), max=(2**(2*WIDTH+4))-1))
	rm = Signal(intbv(0, min=-(2**(2*WIDTH-1)), max=(2**(2*WIDTH-1))-1))
	n = len(acc) - len(res)

	mode_d = Signal(intbv()[3:])

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

def convert():
	a, b = [ Signal(FValue(0)) for i in range(2) ]
	res = Signal(intbv(0, min=-(2**(2*WIDTH-1)), max=(2**(2*WIDTH-1))-1))
	clk = Signal(bool())
	ce = Signal(bool())
	mode = Signal(intbv(MAC_ADD)[3:])

	# m = multiplier(clk, ce, a, b, res)
	m = mac(clk, ce, mode, a, b, res)

	m.convert("VHDL")
	m.convert("Verilog")


convert()
