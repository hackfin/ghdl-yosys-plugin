import os
from myhdl import Cosimulation
import subprocess

HOME = os.environ['HOME']
# Local MyHDL checkout:
MYHDL_COSIMULATION = HOME + "/src/myhdl/cosimulation/icarus"

# The icarus verilog prefix:
IVL_PREFIX = "/usr"
# Where ECP cell simulation libs are found:
ECP5_LIB = "/usr/local/share/yosys/ecp5"

try:
	from config import *
except ImportError:
	pass

IVL_MODULE_PATH_ARGS = [ '-M', IVL_PREFIX + '/lib/ivl' ]
LIBFILES = [ ECP5_LIB + "/cells_sim.v", "-I", ECP5_LIB]

# If we simulate vendor libs, we might need this one:
try:
	LIBFILES += [ ECP5_LIB + "/gsr_pur_assign.v"]
except:
	pass

def setupCosimulationIcarus(options, parameters, kwargs):
	try:
		libfiles = options['libfiles']
	except KeyError:
		libfiles = ""

	name = options['name']

	objfile = "%s.o" % name
	if os.path.exists(objfile):
	    os.remove(objfile)

	analyze_cmd = ['iverilog' ]
	analyze_cmd += ['-s', "tb_" + name]
	analyze_cmd += ['-D', "mixed_hdl"]
	
	for p in parameters.keys():
		analyze_cmd += [ '-P', 'tb_%s.%s=%s' % (name, p, parameters[p]) ]

	analyze_cmd += ['-o', objfile, '%s.v' %name, 'tb_%s.v' % name]
	analyze_cmd += libfiles
	print(analyze_cmd)
	subprocess.call(analyze_cmd)
	simulate_cmd = ['vvp', '-m', MYHDL_COSIMULATION + '/myhdl.vpi']
	simulate_cmd += IVL_MODULE_PATH_ARGS
	simulate_cmd += [objfile]
	c = Cosimulation(simulate_cmd, **kwargs)
	c.name = name
	return c


