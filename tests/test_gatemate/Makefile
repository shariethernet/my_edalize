#Auto generated by Edalize

all: test_gatemate_0_00.cfg.bit

test_gatemate_0_synth.v: edalize_yosys_template.tcl
	$(EDALIZE_LAUNCHER) yosys -l yosys.log -p 'tcl edalize_yosys_template.tcl'

test_gatemate_0_00.cfg.bit: test_gatemate_0_synth.v
	$(EDALIZE_LAUNCHER) p_r -A 1 -i test_gatemate_0_synth.v -o test_gatemate_0 -lib ccag some p_r_synth_options
