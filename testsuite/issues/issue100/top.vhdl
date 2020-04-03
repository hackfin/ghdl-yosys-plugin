-- Test:
-- * HEX file parameter resolving to verilog module
-- * Multiple unit inference with different hex files

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.ram.all;

entity top is
	generic (DATA_W : natural := 16; DUAL_INST : boolean := false);
	port (clk    : in std_ulogic;
	      wren   : in  std_ulogic;
		  idata  : in unsigned(DATA_W-1 downto 0);
		  odata  : out unsigned(DATA_W*2-1 downto 0);
	      led    : out std_ulogic
	);
end entity;


architecture behaviour of top is
	constant ADDR_W : natural := 8;
	constant INACTIVE_WRITE_PORT :
		unsigned(DATA_W-1 downto 0) := (others => '0');
	constant ZERO_COUNT : unsigned(ADDR_W-1 downto 0) := (others => '0');

	signal rdata : unsigned(DATA_W-1 downto 0);
	signal iptr  : unsigned(ADDR_W-1 downto 0) := ZERO_COUNT;
	signal optr  : unsigned(ADDR_W-1 downto 0) := ZERO_COUNT;

begin

advance:
	process (clk)
	begin
		if rising_edge(clk) then
			iptr <= iptr + 1;
		end if;
		optr <= iptr;
	end process;

init_ram_l:
	DPRAM16_init_hex_ce
	generic map ( ADDR_W => ADDR_W, DATA_W => DATA_W,
		INIT_HEX  => "test_a.hex" )
	port map (
		a_ce    => '1',
		a_we    => '0',
		a_addr  => optr,
		a_write => INACTIVE_WRITE_PORT,
		a_read  => odata(DATA_W-1 downto 0),
		a_clk   => clk,
		b_ce    => '1',
		b_we    => wren,
		b_addr  => iptr,
		b_write => idata,
		b_read  => open,
		b_clk   => clk
	);

maybe_h:
	if DUAL_INST generate
init_ram_h:
	DPRAM16_init_hex_ce
	generic map ( ADDR_W => ADDR_W, DATA_W => DATA_W,
		INIT_HEX  => "test_b.hex" )
	port map (
		a_ce    => '1',
		a_we    => '0',
		a_addr  => optr,
		a_write => INACTIVE_WRITE_PORT,
		a_read  => odata(DATA_W*2-1 downto DATA_W),
		a_clk   => clk,
		b_ce    => '1',
		b_we    => wren,
		b_addr  => iptr,
		b_write => idata,
		b_read  => open,
		b_clk   => clk
	);
end generate;


end architecture;

