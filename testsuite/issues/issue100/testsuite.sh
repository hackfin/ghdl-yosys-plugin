#!/bin/sh

topdir=../..
. $topdir/testenv.sh

run_yosys -q -p "ghdl top.vhdl ../../../library/libram.vhdl -e top;
	read_verilog ../../../library/verilog/dpram16_init.v;
	hierarchy -check; ls"

clean
echo OK
