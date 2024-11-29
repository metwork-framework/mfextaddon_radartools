include ../../../adm/root.mk
include $(MFEXT_HOME)/share/package.mk

export NAME=demeter
export VERSION=2023.0.0
export EXPLICIT_NAME=$(NAME)-v$(VERSION)
export EXTENSION=tar.bz2
export CHECKTYPE=MD5
export CHECKSUM=8e8a7191cd93f33de890180440ac6872
DESCRIPTION=\
	Demeter : DEcodeur METEo Rapide (en particulier pour le bufr)
WEBSITE=http://www.meteo.fr
LICENSE=meteo france


export WGETRC=$(shell pwd)/wgetrc

all:: $(PREFIX)/lib/libcodes.so $(PREFIX)/share/tables $(PREFIX)/share/templates_pixmap
$(PREFIX)/lib/libcodes.so:
	$(MAKE) --file=$(MFEXT_HOME)/share/Makefile.standard EXPLICIT_NAME="$(EXPLICIT_NAME)" download uncompress autoreconf configure build install
	cd $(PREFIX)/bin && ln -s fcopy fcopyt && ln -s gcopy gcopyt

$(PREFIX)/share/tables:
	mkdir -p $@
	cp -Rf tables/* $@/

$(PREFIX)/share/templates_pixmap:
	mkdir -p $@
	cp -Rf templates_pixmap/* $@/
