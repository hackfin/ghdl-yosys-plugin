# Temporary Makefile for synthesis tests with ghdl --synth
#
#

PYTHON ?= python3

WORKDIR ?= work

test_%.vhd: %.py
	$(PYTHON) $< -c

syn-%.vhd: %.vhd pck_myhdl_011.vhd
	ghdl --synth --std=08 $^ -e $* >$@

DUTIES = syn-test_dpram_r2w1.vhd

# Entities to include in the test:
TEST_ENTITIES = dpram_r1w1 dpram_r2w1 dpram_r2w1_wt dpram_r2w1_raw

GHDL ?= ghdl

all: $(DUTIES)

GHDL_FLAGS += --warn-no-binding --warn-no-error
GHDL_FLAGS += --warn-no-delayed-checks

GHDL_LIBFLAGS = -P$(LIBGHDL)/lattice/$(FPGA_ARCH)
GHDL_LIBFLAGS += -P$(WORKDIR)

GHDL_ARGS = \
	ghdl --std=08 $(GHDL_GENERICS) \
	$(GHDL_LIBFLAGS) $(GHDL_FLAGS) $^ -e test_$*; \

SYN_ARGS = $(GHDL_ARGS) synth_ecp5 -top test_$* -json $@;

FILES = pck_myhdl_011.vhd 

# Use this for experimental builds
# YOSYS     = export LD_LIBRARY_PATH=/media/scratch/build/ghdl-synth; yosys

YOSYS ?= yosys

%.json: $(FILES) test_%.vhd
	$(YOSYS) -m ghdl -p "$(SYN_ARGS)" 2>&1 | tee $*-report.txt

show-%: $(FILES) test_%.vhd
	$(YOSYS) -m ghdl -p "$(GHDL_ARGS); \
		show -prefix map_$* ;"


ENTITIES += dpram_r1w1 dpram_r2w1 dpram_r2w1_wt dpram_r2w1_raw

check:  $(ENTITIES:%=%.json)
	@for i in $(ENTITIES:%=%-report.txt); do \
		if (tail -15 $$i | grep -q DP16KD); then \
			echo -e "$$i: \e[42mECP5 DP16KD\e[0m"; \
		elif (tail -15 $$i | grep -q TRELLIS_DPR16X4); then \
			echo -e "$$i: \e[36mTRELLIS_DPR16X4\e[0m"; \
		else \
			echo -e "$$i: \e[41mFAIL\e[0m"; \
		fi; \
	done

test:
	@for i in $(TEST_ENTITIES); do \
		echo Running test for $$i; \
		$(PYTHON) $$i.py; \
	done

.PHONY: test

clean:
	rm -f $(DUTIES) $(ENTITIES:%=%.json) *.vhd *.vcd
	rm -f dpram*.v *.o *.txt *.dot *.pid *.pyc

