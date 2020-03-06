-- File: top.vhd
-- Generated by MyHDL 0.11
-- Date: Thu Feb 27 16:44:09 2020


library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;
use std.textio.all;

use work.pck_myhdl_011.all;

entity top is
    port (
        rxd_uart: in std_logic;
        txd_uart: in std_logic;
        oled: out unsigned(7 downto 0);
        seg: out unsigned(12 downto 0);
        segdp: out std_logic;
        dip_sw: in unsigned(7 downto 0);
        reset_n: in std_logic;
        clk_in: in std_logic
    );
end entity top;


architecture MyHDL of top is




type t_enum_t_state_1 is (
	S_RESET,
	S_IDLE,
	S_IN,
	S_WR,
	S_RD,
	S_CMP,
	S_ADVANCE,
	S_ERR
	);

signal iptr: unsigned(7 downto 0);
signal pb_read: unsigned(7 downto 0);
signal pa_addr: unsigned(7 downto 0);
signal pb_addr: unsigned(7 downto 0);
signal data_out: unsigned(7 downto 0);
signal pa_clk: std_logic;
signal data_gen: unsigned(7 downto 0);
signal state: t_enum_t_state_1;
signal enable_gen: std_logic;
signal enable_cmp: std_logic;
signal pa_we: std_logic;
signal reset: std_logic;
signal pb_clk: std_logic;
signal data_cmp: unsigned(7 downto 0);
signal err: std_logic;
signal pa_write: unsigned(7 downto 0);
signal counter: unsigned(31 downto 0);
signal act: std_logic;
signal optr: unsigned(7 downto 0);
signal dual_raw_v10_a_read: unsigned(7 downto 0);
signal lfsr81_fb: std_logic;
signal lfsr81_v: unsigned(7 downto 0);
signal lfsr80_fb: std_logic;
signal lfsr80_v: unsigned(7 downto 0);
type t_array_dual_raw_v10_mem is array(0 to 256-1) of unsigned(7 downto 0);
signal dual_raw_v10_mem: t_array_dual_raw_v10_mem;

begin




TOP_DUAL_RAW_V10_PORT_B_PROC: process (pb_clk) is
begin
    if rising_edge(pb_clk) then
        pb_read <= dual_raw_v10_mem(to_integer(pb_addr));
    end if;
end process TOP_DUAL_RAW_V10_PORT_B_PROC;

TOP_DUAL_RAW_V10_PORT_A_PROC: process (pa_clk) is
begin
    if rising_edge(pa_clk) then
        if (pa_we = '1') then
            
            dual_raw_v10_mem(to_integer(pa_addr)) <= pa_write;
        end if;
        dual_raw_v10_a_read <= dual_raw_v10_mem(to_integer(pa_addr));
    end if;
end process TOP_DUAL_RAW_V10_PORT_A_PROC;


oled <= unsigned'((not err) & to_unsigned(63, 6) & act);
seg <= to_unsigned(255, 13);
segdp <= '1';

TOP_LFSR81_WORKER: process (clk_in) is
begin
    if rising_edge(clk_in) then
        if (reset = '1') then
            lfsr81_v <= to_unsigned(34, 8);
        else
            if (enable_cmp = '1') then
                lfsr81_v <= unsigned'(lfsr81_v(6) & lfsr81_v(5) & lfsr81_v(4) & (lfsr81_v(3) xor lfsr81_fb) & (lfsr81_v(2) xor lfsr81_fb) & (lfsr81_v(1) xor lfsr81_fb) & lfsr81_v(0) & lfsr81_fb);
            end if;
        end if;
    end if;
end process TOP_LFSR81_WORKER;

TOP_LFSR81_ASSIGN: process (lfsr81_v) is
    variable e: std_logic;
begin
    e := stdl(lfsr81_v(7-1 downto 0) = 0);
    lfsr81_fb <= (lfsr81_v(7) xor e);
    data_cmp <= lfsr81_v;
end process TOP_LFSR81_ASSIGN;

TOP_LFSR80_WORKER: process (clk_in) is
begin
    if rising_edge(clk_in) then
        if (reset = '1') then
            lfsr80_v <= to_unsigned(34, 8);
        else
            if (enable_gen = '1') then
                lfsr80_v <= unsigned'(lfsr80_v(6) & lfsr80_v(5) & lfsr80_v(4) & (lfsr80_v(3) xor lfsr80_fb) & (lfsr80_v(2) xor lfsr80_fb) & (lfsr80_v(1) xor lfsr80_fb) & lfsr80_v(0) & lfsr80_fb);
            end if;
        end if;
    end if;
end process TOP_LFSR80_WORKER;

TOP_LFSR80_ASSIGN: process (lfsr80_v) is
    variable e: std_logic;
begin
    e := stdl(lfsr80_v(7-1 downto 0) = 0);
    lfsr80_fb <= (lfsr80_v(7) xor e);
    data_gen <= lfsr80_v;
end process TOP_LFSR80_ASSIGN;

TOP_WORKER: process (clk_in) is
begin
    if rising_edge(clk_in) then
        if (reset = '1') then
            state <= S_RESET;
            iptr <= to_unsigned(0, 8);
            optr <= to_unsigned(0, 8);
            counter <= to_unsigned(0, 32);
        else
            case state is
                when S_RESET =>
                    state <= S_IDLE;
                when S_IDLE =>
                    state <= S_WR;
                when S_WR =>
                    state <= S_IN;
                when S_IN =>
                    state <= S_RD;
                when S_RD =>
                    state <= S_CMP;
                when S_ADVANCE =>
                    state <= S_IDLE;
                when S_CMP =>
                    if (data_cmp = data_out) then
                        state <= S_ADVANCE;
                    else
                        state <= S_ERR;
                    end if;
                when S_ERR =>
                    null;
                when others =>
                    null;
            end case;
            if (pa_we = '1') then
                iptr <= (iptr + 1);
            end if;
            if (state = S_RD) then
                optr <= (optr + 1);
            end if;
            counter <= (counter + 1);
            act <= counter(24);
        end if;
    end if;
end process TOP_WORKER;

TOP_ASSIGN: process (iptr, state, data_gen, pb_read, clk_in, reset_n, optr) is
    variable e: std_logic;
begin
    reset <= stdl((not bool(reset_n)));
    data_out <= pb_read;
    pa_clk <= clk_in;
    pb_clk <= clk_in;
    pa_write <= data_gen;
    pa_addr <= iptr;
    pb_addr <= optr;
    case state is
        when S_IN =>
            enable_gen <= '1';
            enable_cmp <= '0';
        when S_ADVANCE =>
            enable_gen <= '0';
            enable_cmp <= '1';
        when S_RD =>
            enable_gen <= '0';
            enable_cmp <= '0';
        when others =>
            enable_gen <= '0';
            enable_cmp <= '0';
    end case;
    e := stdl(state = S_ERR);
    err <= e;
    pa_we <= stdl(state = S_WR);
end process TOP_ASSIGN;

end architecture MyHDL;