#Auto generated by Edalize

all: post_build

pre_build: 

test_vpr_vpr_0.blif: edalize_yosys_template.tcl | pre_build
	$(EDALIZE_LAUNCHER) yosys -l yosys.log -p 'tcl edalize_yosys_template.tcl'

test_vpr_vpr_0.net: test_vpr_vpr_0.blif
	$(EDALIZE_LAUNCHER) vpr /tmp/k6_N10_mem32K_40nm.xml test_vpr_vpr_0.blif --pack

test_vpr_vpr_0.place: test_vpr_vpr_0.net
	$(EDALIZE_LAUNCHER) vpr /tmp/k6_N10_mem32K_40nm.xml test_vpr_vpr_0.blif --place

test_vpr_vpr_0.route: test_vpr_vpr_0.place
	$(EDALIZE_LAUNCHER) vpr /tmp/k6_N10_mem32K_40nm.xml test_vpr_vpr_0.blif --route

test_vpr_vpr_0.analysis: test_vpr_vpr_0.route
	$(EDALIZE_LAUNCHER) vpr /tmp/k6_N10_mem32K_40nm.xml test_vpr_vpr_0.blif --analysis

post_build: test_vpr_vpr_0.analysis

pre_run: 

run: pre_run

post_run: run
