#Auto generated by Edalize
include config.mk

all: $(TOPLEVEL).bit

$(TOPLEVEL).bit:  $(NAME)_run.tcl $(NAME).xise
	$(EDALIZE_LAUNCHER) xtclsh $^

$(NAME).xise: $(NAME).tcl
	$(EDALIZE_LAUNCHER) xtclsh $<
