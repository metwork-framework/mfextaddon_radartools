include ../../../adm/root.mk
include $(MFEXT_HOME)/share/package.mk

export NAME=demeter
export VERSION=v2018.1.53.g08d929e
export EXTENSION=tar.gz
export CHECKTYPE=MD5
export CHECKSUM=41d7ba64b53ec514d28d9afa0a75e23b
DESCRIPTION=\
	Demeter : DEcodeur METEo Rapide (en particulier pour le bufr)
WEBSITE=http://www.meteo.fr
LICENSE=meteo france
SHORT_VERSION=1.53

export WGETRC=$(shell pwd)/wgetrc


all:: $(PREFIX)/lib/libcodes.so $(PREFIX)/share/tables $(PREFIX)/share/templates_pixmap
$(PREFIX)/lib/libcodes.so:
	$(MAKE) --file=$(MFEXT_HOME)/share/Makefile.standard OPTIONS="--with-boost=$(PREFIX)/../scientific" download uncompress configure build install python3pyinstall_pip

$(PREFIX)/share/tables:
	mkdir -p $@
	cp -Rf tables/* $@/

$(PREFIX)/share/templates_pixmap:
	mkdir -p $@
	cp -Rf templates_pixmap/* $@/
