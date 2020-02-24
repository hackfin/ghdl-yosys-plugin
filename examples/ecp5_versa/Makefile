LIB = ../../library

GHDL ?= ghdl

GHDL_FLAGS = -Plib

CLK_FREQ = 25000000

# USE_BRAM_VHDL = y

ifdef MYHDL_MWE
TOPLEVEL = top
else
GHDL_GENERICS=-gCLK_FREQUENCY=$(CLK_FREQ)
TOPLEVEL = versa_ecp5_top
TOPLEVEL_PARAMETER = _$(CLK_FREQ)
endif


LPF = versa_ecp5.lpf
PACKAGE = CABGA381
NEXTPNR_FLAGS = --um5g-45k --freq 100
NEXTPNR_FLAGS += --lpf-allow-unconstrained
OPENOCD_JTAG_CONFIG = ../../openocd/ecp5-versa.cfg
OPENOCD_DEVICE_CONFIG = ../../openocd/LFE5UM5G-45F.cfg

WORKDIR = work
# Files to synthesize:
ifdef MYHDL_MWE
VHDL_SYN_FILES = pck_myhdl_011.vhd top.vhd
SHOW_ENTITY = top

else
VHDL_SYN_FILES = versa_ecp5_top.vhdl pll_mac.vhd
VHDL_SYN_FILES += soc_iomap_pkg.vhdl
ifdef USE_BRAM_VHDL
VHDL_SYN_FILES += bram.vhdl
# EXTRA_COMMANDS = blackbox bram_2psync_12_8_59fe624214af9b8daa183282288d5eb56b321f14;
endif
VHDL_SYN_FILES += uart.vhdl uart_tx.vhdl uart_rx.vhdl fifobuf.vhdl


VERILOG_FILES = $(LIB)/wrapper/primitives.v
VERILOG_FILES += $(LIB)/wrapper/wrapper.v
ifndef USE_BRAM_VHDL
VERILOG_FILES += $(LIB)/wrapper/bram.v
endif

SHOW_ENTITY = fifobuffer_12_8_0_59fe624214af9b8daa183282288d5eb56b321f14

endif

SVFFILE = $(TOPLEVEL).svf
DEPENDENCIES = lib/ecp5um-std93.cf

all: $(SVFFILE)

include ../docker.mk
include ../ghdlsynth.mk

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
