# Common makefile for GHDL synthesis

# Specify:
#
# For a platform 'foo' this rule file expects variable definitions such as:
#
#
# foo_GHDL_GENERICS = .. optional parameters
# foo_PARAMETER = .. optional parameters
#
# LPF: I/O constraints file

PLATFORM ?= ecp5

ifneq ($(VERILOG_FILES),)
MAYBE_READ_VERILOG = read_verilog $(VERILOG_FILES);
endif

ifneq ($(SHOW_ENTITY),)
MAYBE_SHOW = show $(SHOW_ENTITY);
endif

# We add this to resolve more complexities below:
.SECONDEXPANSION:

%.json: $$($$*_VHDL_SYN_FILES)
	echo $^
	$(YOSYS) -m $(GHDLSYNTH) -p \
		"ghdl $(GHDL_FLAGS) $($*_GHDL_GENERICS) $^ -e $*; \
		$(MAYBE_SHOW) \
		$(MAYBE_READ_VERILOG) \
		$(EXTRA_COMMANDS) \
		synth_$(PLATFORM) \
		-top $*$($*_PARAMETER) -json $@; \
	" 2>&1 | tee $*-report.txt


%.il: $$($$*_VHDL_SYN_FILES)
	$(YOSYS) -m $(GHDLSYNTH) -p \
		"ghdl $(GHDL_FLAGS) $($*_GHDL_GENERICS) $^ -e $*; \
		$(MAYBE_READ_VERILOG) \
		$(EXTRA_COMMANDS) \
		synth_$(PLATFORM) \
		-top $*$($*_PARAMETER) ; \
		write_ilang $@ \
		"

%.config: %.json
	$(NEXTPNR) --json $< --lpf $(LPF) \
		--textcfg $@ $(NEXTPNR_FLAGS) --package $(PACKAGE)

%.svf: %.config
	$(ECPPACK) --svf $*.svf $< $@


.PRECIOUS: %.json %.config
	
