--
-- Versa ECP5(G) top level module
--
--
-- 1/2017  Martin Strubel <hackfin@section5.ch>
--
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

library work;


entity versa_ecp5_top is
    generic(
        CLK_FREQUENCY : positive := 25000000
    );
	port (
		-- clk_out     : out  std_logic;

		-- spi_miso  : in  std_logic;
		-- spi_mosi  : out std_logic;
		-- spi_cs    : out std_logic;

		twi_scl  : inout std_logic;
		twi_sda  : inout std_logic;

		rxd_uart    : in std_logic;	  -- FT2232 -> CPU
		txd_uart    : out std_logic;  -- CPU    -> FT2232

		oled         : out  std_logic_vector(7 downto 0);
		seg          : out  std_logic_vector(13 downto 0);
		segdp        : out  std_logic;
		dip_sw       : in   std_logic_vector(7 downto 0);

		reset_n      : in   std_logic;
		-- clk_serdes   : in   std_logic;
		clk_in       : in   std_ulogic

	);
end entity versa_ecp5_top;


architecture behaviour of versa_ecp5_top is

	signal mclk           : std_logic;
	signal mclk_locked    : std_logic;

	-- Pixel clock:
	signal pclk           : std_logic;

	signal comb_reset     : std_logic;

	-- signal spi_sclk       : std_logic;
	-- signal spi_ts         : std_logic;
	-- signal spi_cs_int     : std_logic;

	-- GPIOs:
	-- Set to defined state for simulation:
	-- signal gpio           : unsigned(31 downto 0);
	-- signal cfg            : std_logic_vector(7 downto 0);

	constant f_half : integer := CLK_FREQUENCY / 2;
	signal reset_delay    : unsigned(3 downto 0);
	signal led            : unsigned(7 downto 0);
    signal counter : integer range 0 to f_half;
    signal toggle_led : std_ulogic := '0';

	-- MAC clocks:

 
begin

	comb_reset <= (not reset_n) or (not mclk_locked);

	-- seg <= not std_logic_vector(gpio(13 downto 0));
	-- segdp <= not gpio(14);
	seg <= (others => '1'); -- low active
	segdp <= '1'; -- low active

	-- gsr_inst: GSR port map (reset_n);

	process(mclk)
    begin
        if rising_edge(mclk) then
            counter <= counter + 1;
            if counter = f_half then
                toggle_led <= not toggle_led;
                counter <= 0;
            end if;
        end if;
    end process;

-- We run a delayed reset for the CPU, as there might be race conditions
-- with the TAP.

delayed_cpu_reset:
	process (comb_reset, mclk)
	begin
		if comb_reset = '1' then
			reset_delay	<= x"f";
			-- delayed_reset <= '1';
		elsif rising_edge(mclk) then
			if reset_delay /= x"0" then
				reset_delay <= reset_delay - 1;
			else
				-- delayed_reset <= '0';
			end if;
		end if;
	end process;


clk_pll1: entity work.pll_mac
    port map (
        CLKI    =>  clk_in,
        CLKOP   =>  open,
        CLKOS   =>  mclk, -- 25 Mhz
        CLKOS2  =>  open,
        CLKOS3  =>  pclk,
        LOCK    =>  mclk_locked
	);

    led(0) <= toggle_led;
    led(1) <= not rxd_uart;
    led(2) <= '1';
	led(3) <= '0';
	led(4) <= '0';
	led(5) <= '0';
	led(6) <= '0';
	led(7) <= '0';

	-- Note LED are low active
	oled <= not std_logic_vector(led);

	twi_sda <= 'H';
	twi_scl <= 'H';


	txd_uart   <= rxd_uart;
	

end behaviour;
