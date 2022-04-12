include ../../../adm/root.mk
include $(MFEXT_HOME)/share/simple_layer.mk

LIB_LIST = $(shell cat libraries.txt)
$(shell mkdir $(PREFIX)/lib)

all:: $(PREFIX)/lib/libboost_filesystem.so.1.66.0
$(PREFIX)/lib/libboost_filesystem.so.1.66.0:
	for lib in $(LIB_LIST); do cp -r $$lib $(PREFIX)/lib; done
