#Auto generated by Edalize

all: test_symbiflow_nextpnr_xilinx_0.bit

test_symbiflow_nextpnr_xilinx_0.json: edalize_yosys_template.tcl
	$(EDALIZE_LAUNCHER) yosys -l yosys.log -p 'tcl edalize_yosys_template.tcl'

test_symbiflow_nextpnr_xilinx_0.fasm: test_symbiflow_nextpnr_xilinx_0.json
	$(EDALIZE_LAUNCHER) nextpnr-xilinx --chipdb chipdb.bin --xdc top.xdc --json test_symbiflow_nextpnr_xilinx_0.json --write test_symbiflow_nextpnr_xilinx_0.routed.json --fasm test_symbiflow_nextpnr_xilinx_0.fasm --log nextpnr.log --fake_option 1000

test_symbiflow_nextpnr_xilinx_0.bit: test_symbiflow_nextpnr_xilinx_0.fasm
	$(EDALIZE_LAUNCHER) symbiflow_write_bitstream -d artix7 -f test_symbiflow_nextpnr_xilinx_0.fasm -p xc7a35tcsg324-1csg324-1 -b test_symbiflow_nextpnr_xilinx_0.bit
