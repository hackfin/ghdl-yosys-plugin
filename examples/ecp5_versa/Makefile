LIB = ../../library

GHDL ?= ghdl

GHDL_FLAGS = -Plib

CLK_FREQ = 25000000

# Enable to use VHDL for BRAM. Currently broken.
# USE_BRAM_VHDL = y

TOPLEVEL ?= versa_ecp5_top

LPF = versa_ecp5.lpf
PACKAGE = CABGA381
NEXTPNR_FLAGS = --um5g-45k --freq 100
NEXTPNR_FLAGS += --lpf-allow-unconstrained
OPENOCD_JTAG_CONFIG = ../../openocd/ecp5-versa.cfg
OPENOCD_DEVICE_CONFIG = ../../openocd/LFE5UM5G-45F.cfg


WORKDIR = work
# Files to synthesize:

# 'top' MyHDL example:
top_VHDL_SYN_FILES = pck_myhdl_011.vhd top.vhd

# 'versa_ecp5_top' setup:
versa_ecp5_top_GHDL_GENERICS =-gCLK_FREQUENCY=$(CLK_FREQ)
versa_ecp5_top_PARAMETER = _$(CLK_FREQ)

TOP = versa_ecp5_top
$(TOP)_VHDL_SYN_FILES = $(TOP).vhdl pll_mac.vhd
$(TOP)_VHDL_SYN_FILES += soc_iomap_pkg.vhdl
ifdef USE_BRAM_VHDL
$(TOP)_VHDL_SYN_FILES += bram.vhdl
endif
$(TOP)_VHDL_SYN_FILES += uart.vhdl uart_tx.vhdl uart_rx.vhdl fifobuf.vhdl


# Common files

VERILOG_FILES = $(LIB)/wrapper/primitives.v
VERILOG_FILES += $(LIB)/wrapper/wrapper.v
ifndef USE_BRAM_VHDL
VERILOG_FILES += $(LIB)/wrapper/bram.v
endif

# Board supply packages:
BSPS = top versa_ecp5_top

SVFFILE = $(TOPLEVEL).svf
DEPENDENCIES = lib/ecp5um-std93.cf

all: $(BSPS:%=%.svf)

include ../docker.mk
include ../ghdlsynth.mk

which:
	@echo Run 'make prog TOPLEVEL=X' where X is one of:
	@for i in $(BSPS); do echo -- $$i; done

lib:
	mkdir $@

lib/ecp5um-std93.cf: $(LIB)/ecp5u/components.vhdl | lib
	$(GHDL) -i --workdir=$(dir $@) --work=ecp5um \
		$< 

pll_mac.vhd: $(DEPENDENCIES) 

prog: $(SVFFILE)
	$(OPENOCD) -f $(OPENOCD_JTAG_CONFIG) -f $(OPENOCD_DEVICE_CONFIG) \
		-c "transport select jtag; init; svf $<; exit"

clean:
	rm -fr lib work *.json *.svf *.config *-report.txt
