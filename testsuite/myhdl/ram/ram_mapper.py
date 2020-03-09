# Python based RAM mapper
#
# <hackfin@section5.ch>
#
#

from pyosys import libyosys as ys

from config import *

import sys
import map_bram
import dprams

_ID = ys.IdString

PARAM_TRANSLATE = { 
	"MEMID"           : None,
    "RD_CLK_ENABLE"   : str,
    "RD_CLK_POLARITY" : str,
    "RD_PORTS"        : int,
    "RD_TRANSPARENT"  : str,
    "ABITS"           : int,
    "SIZE"            : int,
    "WIDTH"           : int,
    "WR_CLK_ENABLE"   : str,
    "WR_CLK_POLARITY" : str,
    "WR_PORTS"        : int,
}


def to_levels(v):
	s = ""
	for i in v:
		print(i)

def to_mem_impl_description(c):
	"Translates a memory cell info into a descriptor dictionary"
	d = {}

	conn = c.connections_
	parameters = c.parameters

	for it in parameters.items():
		k, v = it
		k = k.str()[1:]
		try:
			t = PARAM_TRANSLATE[k]
			if t == int:
				d[k] = v.as_int()
			elif t == str:
				d[k] = v.as_string()
			else:
				d[k] = v

		except KeyError:
			d[k] = v.as_string()

	nwp = d['WR_PORTS']
	nrp = d['RD_PORTS']
	width = d['WIDTH']
	abits = d['ABITS']

	for it in conn.items():
		k, v = it
		k = k.str()[1:]
		if k == 'WR_DATA':
			d[k] = [ v.extract(j * width, width) for j in range(nwp) ]
		elif k == 'RD_DATA':
			d[k] = [ v.extract(j * width, width) for j in range(nrp) ]
		elif k == 'WR_ADDR':
			d[k] = [ v.extract(j * abits, abits) for j in range(nwp) ]
		elif k == 'RD_ADDR':
			d[k] = [ v.extract(j * abits, abits) for j in range(nrp) ]
		elif k in [ 'WR_CLK', 'WR_EN' ]:
			d[k] = [ v.extract(j) for j in range(nwp) ]
		elif k in [ 'RD_CLK', 'RD_EN' ]:
			d[k] = [ v.extract(j) for j in range(nrp) ]
		else:
			d[k] = v

	return d

import inspect

def lineno():
	return inspect.currentframe().f_back.f_lineno

def mem_replace_cell(module, i, mem, mem_impl, nl, primitive_id):
	repl_cell = module.addCell(_ID("\\meminst%d" % i), _ID(primitive_id))
	print("Added cell", repl_cell)

	width, abits = mem_impl['WIDTH'], mem_impl['ABITS']
	print("Phys. Data width: %d, Address width: %d" % (width, abits))
	nrp = mem_impl['RD_PORTS']

	param = {
		_ID('\\INIT') :  ys.Const("000000000000000"),
		_ID('\\CFG_DBITS') :  ys.Const(width, 8),
		_ID('\\CFG_ABITS') :  ys.Const(abits, 8)
	}

	repl_cell.parameters = param
	
	for k in nl.items():
		wirename = _ID("\\" + k[0])
		if k[1]:
			s = k[1][0]
			if isinstance(s, ys.SigSpec):
				name = wirename.str()
				wid = _ID("\\" + k[0] + "%d" % i)
				# wid = ys.new_id(__name__, lineno(), k[0])
				w = module.addWire(wid, s.size())
				sw = ys.SigSpec(w)

				if k[1][1] == 'out':
					print("Connect output", wirename.str())
					repl_cell.setPort(wirename, ys.SigSpec(w))
					module.connect(s, sw)
				else:
					print("Connect input", name)
					repl_cell.setPort(wirename, sw)
					module.connect(sw, s)

			elif isinstance(s, str):
				if s in [ '0', '1' ]:
					c = ys.Const.from_string(s)
					repl_cell.setPort(wirename, ys.SigSpec(c))
				else:
					raise ValueError("Unsupported string value")

	module.remove(mem)


def map_tdp_memory(module, i, m, pid):
	"Map true dual port memory"

	mem_impl = to_mem_impl_description(m)
	pmaps = map_bram.analyze_cell(mem_impl, map_bram.ECP5_DPRAM)
	print("Mapping...")
	# print(pmaps)
	nl = map_bram.map_cell(mem_impl, pmaps, map_bram.TARGET_TDP_RAM)
	for n in nl.items():
		# print(n)
		if n[1]:
			if n[1][1] == 'out':
				print(n[0], " => ", dprams.getid(n[1][0]))
			else:
				print(n[0], " <= ", dprams.getid(n[1][0]))
		else:
			print(n[0], " <= (others => 'X')")

	print("#### DONE ####")

	mem_replace_cell(module, i, m, mem_impl, nl, pid)

def dump_entity(c):
	conn = c.connections_
	parameters = c.parameters


	for k in parameters.items():
		i, v = k
		if i != _ID("\INIT"):
			print(k)

	print(40 * "-")

	for k in conn.keys():
		sig = conn[k]
		print(k, sig, sig.size())

def yosys_dpram_mapper(plugin, cmd, files, top, mapped):
	design = ys.Design()
	TECHMAP = 1

	print("Running YOSYS custom mapper")
	if plugin:
		ys.load_plugin(plugin, [])

	ys.run_pass(cmd, design)

	if not TECHMAP: # Without techmap
		ys.run_pass("read_verilog ecp5_dp16kd.v", design)

	ys.run_pass("read_verilog -lib %s/cells_sim.v %s/cells_bb.v" % (YOSYS_ECP5_LIBS, YOSYS_ECP5_LIBS), design)

	ys.run_pass("hierarchy -check -top %s" % (top), design)

	modules = design.selected_whole_modules_warn()
	for module in modules:
		# print(dir(module))
		memories = []
		for cell in module.selected_cells():
			if cell.type == "$mem":
				print(20 * "-")
				print("Found memory")
				dump_entity(cell)
				memories.append(cell)


	module = modules[0]
	for i, m in enumerate(memories):
		pid = "$__ECP5_DP16KD"
		# When not using techmap, bind to local blackbox definition:
		if not TECHMAP:
			pid = "\\" + pid

		map_tdp_memory(module, i, m, pid)

	if TECHMAP:
		ys.run_pass("techmap -map /data/src/yosys/techlibs/ecp5/brams_map.v", design)
		ys.run_pass("techmap -map /data/src/yosys/techlibs/ecp5/cells_map.v", design)


	ys.run_pass("hierarchy -check", design)	
	ys.run_pass("clean", design)	
	ys.run_pass("show -prefix %s" % mapped, design)	
	ys.run_pass("write_verilog -norename %s.v" % (mapped), design)
