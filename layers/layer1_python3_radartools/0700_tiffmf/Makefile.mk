include ../../../adm/root.mk
include $(MFEXT_HOME)/share/package.mk

export NAME=tiffmf
export VERSION=1.0.2
export EXTENSION=tar.gz
export CHECKTYPE=MD5
export CHECKSUM=66deb5f9201b89842d1c1d5c7972ebaf
DESCRIPTION=\
Bibliotheque Meteo-France d'ecriture et lecture de fichiers au format TIFF-MF. C'est une extension du format TIFF.
WEBSITE=http://www.meteo.fr
LICENSE=meteo france

export WGETRC=$(shell pwd)/wgetrc

all:: $(PREFIX)/lib/libtiffmto.so
$(PREFIX)/lib/libtiffmto.so:
	$(MAKE) --file=$(MFEXT_HOME)/share/Makefile.standard PREFIX=$(PREFIX) download uncompress configure build install
