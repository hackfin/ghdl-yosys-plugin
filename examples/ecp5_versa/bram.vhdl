library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity bram_2psync is
	generic (
		ADDR_W      : natural := 6;
		DATA_W      : natural := 16;
		SYN_RAMTYPE : string := "block_ram"
	);
	port (
		-- Port A
		a_we    : in  std_logic;
		a_addr  : in  unsigned(ADDR_W-1 downto 0);
		a_write : in  unsigned(DATA_W-1 downto 0);
		a_read  : out unsigned(DATA_W-1 downto 0);
		-- Port B
		b_we    : in  std_logic;
		b_addr  : in  unsigned(ADDR_W-1 downto 0);
		b_write : in  unsigned(DATA_W-1 downto 0);
		b_read  : out unsigned(DATA_W-1 downto 0);
		clk     : in  std_logic
	);
end entity bram_2psync;

architecture beh of bram_2psync is

type ram_t is array(0 to 2**ADDR_W-1) of unsigned(DATA_W-1 downto 0);
signal mem: ram_t;

begin

porta_proc: process (clk) is
begin
    if rising_edge(clk) then
        a_read <= mem(to_integer(a_addr));
    end if;
end process porta_proc;

portb_proc: process (clk) is
begin
    if rising_edge(clk) then
        if b_we = '1' then
            mem(to_integer(b_addr)) <= b_write;
        end if;
        b_read <= mem(to_integer(a_addr));
    end if;
end process portb_proc;


end architecture beh;
