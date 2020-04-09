#!/bin/sh

topdir=../..
. $topdir/testenv.sh

# Test case: make sure to use -defer option for passed INIT_HEX
# option, and that no mem.hex is around (reference to it should
# be replaced by INIT_HEX parameter
# This case only tests that hierarchy resolves
[ -e mem.hex ] && rm mem.hex
run_yosys -p "ghdl top.vhdl ../../../library/libram.vhdl -e top;
	read_verilog -defer ../../../library/verilog/dpram16_init.v;
	hierarchy -check; ls"

# FAILURE case: Re-definition of module `\DPRAM16_init_hex_ce
run_yosys -q -p "ghdl -gDUAL_INST=true top.vhdl ../../../library/libram.vhdl -e top;
	read_verilog -defer ../../../library/verilog/dpram16_init.v;
	hierarchy -check; ls"

clean
echo OK
