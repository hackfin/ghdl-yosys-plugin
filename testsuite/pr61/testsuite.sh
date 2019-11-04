#!/bin/sh

topdir=..
. $topdir/testenv.sh

run_yosys -p "ghdl vector.vhdl -e vector; dump -o vector.il"

grep -q 0000000000000000000000000000000011111111111111111111111111111010 vector.il || exit 1
grep -q 0000000011111111111111111111111111111111111111111111111100000000 vector.il || exit 1
grep -q 1111111111111111111111111111111111111111111111111111111111111111 vector.il || exit 1
grep -q 0000111111111111111111111111111111111111111111111111111111110000 vector.il || exit 1

clean
