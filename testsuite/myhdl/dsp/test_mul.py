from pyosys.libyosys import *

# FIXME: python module can't tell where the shared folder is.
LIBS = "/media/sandbox/usr/share/yosys"
import os

GHDL = 0

HOME = os.environ['HOME']

XHDL_PLUGIN = HOME + "/src/vhdl/ghdlsynth-beta/ghdl.so"
plugin = XHDL_PLUGIN

name = "dual_mac"

d = Design()
if GHDL:
	load_plugin(plugin, [])
	run_pass("ghdl %s.vhd pck_myhdl_011.vhd -e %s" % (name, name), d)
else:
	run_pass("read_verilog %s.v" % name, d)

run_pass("proc", d)
run_pass("techmap -map %s/mul2dsp.v -map %s/ecp5/dsp_map.v -D DSP_A_MAXWIDTH=18 -D DSP_B_MAXWIDTH=18  -D DSP_A_MINWIDTH=2 -D DSP_B_MINWIDTH=2  -D DSP_NAME=\$__MUL18X18" % (LIBS, LIBS), d)
run_pass("stat", d)
# run_pass("show", d)

