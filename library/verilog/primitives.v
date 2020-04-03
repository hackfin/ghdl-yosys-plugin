`timescale 1 ns / 1 ps

module VHI ( Z );
    output Z ;
  supply1 VSS;
  buf (Z , VSS);
endmodule 

module VLO ( Z );
	output Z;
  supply1 VSS;
  buf (Z , VSS);
endmodule
