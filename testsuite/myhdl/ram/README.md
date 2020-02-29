Dual port RAM test suite
-------------------------------------------------------------------------

02/2020   <hackfin@section5.ch>

This test suite is based on a recent MyHDL 0.11 package.
It is recommended to use the supplied Dockerfile to build the test
environment.

 Short Introduction
--------------------

See Makefile.test for the various test rules.
In particular, a few examples:

- `make clean test` will run all enabled tests (see `TEST_ENTITIES`)


For each test entity in `TEST_ENTITIES` there is a corresponding python
test bench, like `dpram_r1w1.py`. If it has the variable `IMPLEMENTED`
set, synthesis will be attempted and a post mapping Verilog dump will be run
through MyHDLs Cosimulation feature. This might require to set the path
to the correct simulation libraries. Also, a fairly recent release of
icarus verilog (**iverilog**) is required, to correctly interpret the
verilog dump.

Note: Enabling the VCD trace may produce misleading results, due to some
cosimulation details. However, the cosimulation should produce something
sensible.
