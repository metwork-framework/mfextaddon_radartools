include ../../../adm/root.mk
include $(MFEXT_HOME)/share/package.mk

export NAME=demeter-python
export VERSION=1.0.0
export EXTENSION=tar.gz
export CHECKTYPE=MD5
export CHECKSUM=27d96038b6f578c272fbbb6679d40a56
DESCRIPTION=\
	Demeter : DEcodeur METEo Rapide (en particulier pour le bufr)
WEBSITE=http://www.meteo.fr
LICENSE=meteo france
SHORT_VERSION=1.0.0


all:: $(PREFIX)/lib/libcodes.so $(PREFIX)/share/tables $(PREFIX)/share/templates_pixmap
$(PREFIX)/lib/libcodes.so:
	$(MAKE) --file=$(MFEXT_HOME)/share/Makefile.standard download uncompress configure build install python2pyinstall

$(PREFIX)/share/tables:
	mkdir -p $@
	cp -Rf tables/* $@/

$(PREFIX)/share/templates_pixmap:
	mkdir -p $@
	cp -Rf templates_pixmap/* $@/
