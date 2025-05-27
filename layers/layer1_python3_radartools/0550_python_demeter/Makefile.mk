include ../../../adm/root.mk
include $(MFEXT_HOME)/share/package_python3.mk

export NAME=python-demeter
export VERSION=2023.0.0
export EXPLICIT_NAME=$(NAME)-v$(VERSION)
export EXTENSION=tar.bz2
export CHECKTYPE=MD5
export CHECKSUM=19eb593f434df05e3f50255132ecb72d
DESCRIPTION=\
	Demeter : DEcodeur METEo Rapide (en particulier pour le bufr)
WEBSITE=http://www.meteo.fr
LICENSE=meteo france

export WGETRC=$(shell pwd)/wgetrc

all:: $(PREFIX)/lib/python$(PYTHON3_SHORT_VERSION)/site-packages/python_demeter-$(VERSION).dist-info
$(PREFIX)/lib/python$(PYTHON3_SHORT_VERSION)/site-packages/python_demeter-$(VERSION).dist-info:
	mkdir -p $(PREFIX)/lib/python$(PYTHON3_SHORT_VERSION)/site-packages
	$(MAKE) --file=$(MFEXT_HOME)/share/Makefile.standard EXPLICIT_NAME="$(EXPLICIT_NAME)" download uncompress
	cp pyproject.toml build/$(EXPLICIT_NAME)
	$(MAKE) --file=$(MFEXT_HOME)/share/Makefile.standard EXPLICIT_NAME="$(EXPLICIT_NAME)" python3install_pip
