# Auto generated by Edalize
STD = --std=08
TOPLEVEL = top_module
TOPLEVEL_LIBS = 
ANALYZE_OPTIONS = --ieee=synopsys -P./libx
RUN_OPTIONS = a few run_options

VHDL_SOURCES =  vhdl_file.vhd vhdl_lfile

all: work-obj08.cf

run: $(TOPLEVEL)
	$(EDALIZE_LAUNCHER) ghdl -r $(STD) $(ANALYZE_OPTIONS) $(TOPLEVEL_LIBS) $(TOPLEVEL) $(RUN_OPTIONS) $(EXTRA_OPTIONS)

$(TOPLEVEL): $(VHDL_SOURCES) work-obj08.cf
	$(EDALIZE_LAUNCHER) ghdl -m $(STD) $(ANALYZE_OPTIONS) $(TOPLEVEL_LIBS) $(TOPLEVEL)

$(TOPLEVEL).v: $(VHDL_SOURCES) work-obj08.cf
	$(EDALIZE_LAUNCHER) ghdl --synth --out=verilog $(STD) $(ANALYZE_OPTIONS) $(TOPLEVEL_LIBS) $(TOPLEVEL)

make_libraries_directories:
	@echo "Creating libraries directories"
	mkdir -p libx

work-obj08.cf: make_libraries_directories
	$(EDALIZE_LAUNCHER) ghdl -i $(STD) $(ANALYZE_OPTIONS)  vhdl_file.vhd
	$(EDALIZE_LAUNCHER) ghdl -i $(STD) $(ANALYZE_OPTIONS) --work=libx --workdir=./libx vhdl_lfile

