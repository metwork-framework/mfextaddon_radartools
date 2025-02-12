include ../../../adm/root.mk
include $(MFEXT_HOME)/share/package.mk

export NAME=tiffmfutils
export VERSION=0.2.1
export EXTENSION=tar.gz
export CHECKTYPE=MD5
export CHECKSUM=5bcdc4ece04b0c547ee39e3177afcf36
DESCRIPTION=\
Outils de conversion entre le tiffmf et le geotiff
WEBSITE=http://www.meteo.fr
LICENSE=meteo france

export WGETRC=$(shell pwd)/wgetrc

all:: $(PREFIX)/lib/libtiffmfutils.so
$(PREFIX)/lib/libtiffmfutils.so:
	$(MAKE) --file=$(MFEXT_HOME)/share/Makefile.standard EXTRACFLAGS="-I$(PREFIX)/../core/include" PREFIX=$(PREFIX) OPTIONS="--with-geotiff=$(PREFIX)/../scientific_core" download uncompress configure build install
