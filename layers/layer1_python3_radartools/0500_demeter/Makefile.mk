include ../../../adm/root.mk
include $(MFEXT_HOME)/share/package.mk

export NAME=demeter
export VERSION=2022.0.1
export EXPLICIT_NAME=$(NAME)-v$(VERSION)
export EXTENSION=tar.bz2
export CHECKTYPE=MD5
export CHECKSUM=f09b3de7a365af553f31e582415b6dd4
DESCRIPTION=\
	Demeter : DEcodeur METEo Rapide (en particulier pour le bufr)
WEBSITE=http://www.meteo.fr
LICENSE=meteo france


export WGETRC=$(shell pwd)/wgetrc

all:: $(PREFIX)/lib/libcodes.so $(PREFIX)/share/tables $(PREFIX)/share/templates_pixmap
$(PREFIX)/lib/libcodes.so:
	$(MAKE) --file=$(MFEXT_HOME)/share/Makefile.standard EXPLICIT_NAME="$(EXPLICIT_NAME)" download uncompress autoreconf configure build install

$(PREFIX)/share/tables:
	mkdir -p $@
	cp -Rf tables/* $@/

$(PREFIX)/share/templates_pixmap:
	mkdir -p $@
	cp -Rf templates_pixmap/* $@/
