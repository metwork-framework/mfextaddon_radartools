include ../../../adm/root.mk
include $(MFEXT_HOME)/share/package.mk

export NAME=tiffmf
export VERSION=1.0.1
export EXTENSION=tar.gz
export CHECKTYPE=MD5
export CHECKSUM=de5f7e1916b7c6209632f54bcc5d9aa9
DESCRIPTION=\
Bibliotheque Meteo-France d'ecriture et lecture de fichiers au format TIFF-MF. C'est une extension du format TIFF.
WEBSITE=http://www.meteo.fr
LICENSE=meteo france

export WGETRC=$(shell pwd)/wgetrc

all:: $(PREFIX)/lib/libtiffmto.so
$(PREFIX)/lib/libtiffmto.so:
	$(MAKE) --file=$(MFEXT_HOME)/share/Makefile.standard PREFIX=$(PREFIX) download uncompress configure build install
