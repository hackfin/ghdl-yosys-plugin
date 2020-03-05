#!/usr/bin/env python3.5
#
# Yosys interfacing
#
# <hackfin@section5.ch>
#

from pyosys import libyosys as ys

def show_conn(mem):
	conn = mem.connections_
	parameters = mem.parameters

	for k in parameters.keys():
		print(k)


	for k in conn.keys():
		sig = conn[k]
		print(k, sig, sig.size())
		if k == "\WR_CLK":
			pass

_ID = ys.IdString

bram_conn = {
	"porta_clk" : [ "CLK2", 1],
	"portb_clk" : [ "CLK3", 1],
	"porta_ce" : [ "A1CE", 1],
	"portb_ce" : [ "B1CE", 1],
	"porta_we" : [ "A1WE", 1],
	"porta_read" : [ "A1READ", 16],
	"portb_read" : [ "B1READ", 16],
	"porta_write" : [ "A1WRITE", 18],
	"portb_write" : [ "B1WRITE", 18],
	"portb_we" : [ "B1WE", 1],
	"porta_addr" : [ "A1ADDR", 7],
	"portb_addr" : [ "B1ADDR", 7],
}

IN, OUT = 0, 1

bram_wire = {
	( "RD_CLK",   0, IN )  : "porta_clk",
	( "RD_CLK",   1, IN )  : "portb_clk",
	( "RD_EN",    0, IN )  : "porta_ce",
	( "RD_EN",    1, IN )  : "portb_ce",
	( "WR_EN",    0, IN )  : "porta_we",
	( "WR_EN",    0, IN )  : "porta_we",
	( "RD_EN",    1, IN )  : "portb_we",
	( "RD_DATA", (16, 0), OUT )  : "porta_read",
	( "RD_DATA", (16, 1), OUT )  : "portb_read",
	( "WR_DATA", (16, 0), IN )  : "porta_write",
	# ( "WR_DATA", (16, 1), IN )  : "portb_write",
	( "RD_ADDR", (7, 0), IN )  : "porta_addr",
	( "WR_ADDR", (7, 0), IN )  : "portb_addr",
}

import inspect

def lineno():
	return inspect.currentframe().f_back.f_lineno

def mem_replace_cell(module, mem, use_techmap = 1):
	name = "$__ECP5_DP16KD"
	if not use_techmap:
		name = "\\" + name

	repl_cell = module.addCell(_ID("$meminst0"), _ID(name))
	param = {
		_ID('\\CFG_DBITS') :  ys.Const(18, 8),
		_ID('\\CFG_ABITS') :  ys.Const(10, 8)
	}

	repl_cell.parameters = param
	
	wires = {}


	for k in bram_conn.items():
		NEW_ID = ys.new_id(__file__, lineno(), k[0])
		w = module.addWire(_ID("\\" + k[0]), k[1][1])
		wires[k[0]] = w
		s = ys.SigSpec(w)
		repl_cell.setPort(_ID("\\" + k[1][0]), s)

	conn = mem.connections_

	for k in bram_wire.items():
		name = _ID("\\" + k[0][0])
		print("Connecting %s" % name.str())
		sig = conn[name]
		w = wires[k[1]]
		is_out = k[0][2] == OUT
		if k[0][1] != None:
			t = k[0][1]
			if isinstance(t, tuple):
				sub = sig.extract(t[0] * t[1], t[0])
			else:
				sub = sig.extract(k[0][1])
		else:
			sub = sig
		sw = ys.SigSpec(w)
		print("Sizes:", sub.size(), sw.size())
		if sw.size() > sub.size():
			sub.extend_u0(sw.size())

		if is_out:
			module.connect(sub, sw)
			# sub.replace(0, sw)
		else:
			module.connect(sw, sub)

	print(conn)
	read = conn[_ID('\\RD_DATA')]

	# print("## RD_DATA:", read.port_output)

	print(80 * '#')

	module.remove(mem)


design = ys.Design()

TECHMAP = 1

ys.load_plugin("/home/strubi/src/vhdl/ghdlsynth-beta/ghdl.so", [])
ys.run_pass("ghdl dpram_r2w1.vhd pck_myhdl_011.vhd -e dpram_r2w1", design)
if not TECHMAP:
	ys.run_pass("read_verilog ecp5_dp16kd.v", design)
ys.run_pass("hierarchy -check -top dpram_r2w1", design)

modules = design.selected_whole_modules_warn()
for module in modules:
	# print(dir(module))
	memories = []
	for cell in module.selected_cells():
		if cell.type == "$mem":
			print(20 * "-")
			print("Found memory")
			show_conn(cell)
			memories.append(cell)

module = modules[0]
for m in memories:
	mem_replace_cell(module, m, TECHMAP)

if TECHMAP:
	ys.run_pass("debug techmap -map /data/src/yosys/techlibs/ecp5/brams_map.v", design)
# ys.run_pass("techmap -map /data/src/yosys/techlibs/ecp5/cells_map.v", design)
# ys.run_pass("clean", design)
ys.run_pass("show", design)
ys.run_pass("write_ilang test.ilang", design)
ys.run_pass("write_verilog test.v", design)
