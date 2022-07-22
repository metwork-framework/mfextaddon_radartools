include ../../../adm/root.mk
include $(MFEXT_HOME)/share/package_python3.mk

export NAME=python-demeter
export VERSION=2022.0.2
export EXPLICIT_NAME=$(NAME)-v$(VERSION)
export EXTENSION=tar.bz2
export CHECKTYPE=MD5
export CHECKSUM=9fcfbc42ed72ce9261be016d3c8be921
DESCRIPTION=\
	Demeter : DEcodeur METEo Rapide (en particulier pour le bufr)
WEBSITE=http://www.meteo.fr
LICENSE=meteo france

export WGETRC=$(shell pwd)/wgetrc

all:: $(PREFIX)/lib/python$(PYTHON3_SHORT_VERSION)/site-packages/python_demeter-2022.0.2-py3.10-linux-x86_64.egg
$(PREFIX)/lib/python$(PYTHON3_SHORT_VERSION)/site-packages/python_demeter-2022.0.2-py3.10-linux-x86_64.egg:
	$(MAKE) --file=$(MFEXT_HOME)/share/Makefile.standard EXPLICIT_NAME="$(EXPLICIT_NAME)" download uncompress python3build python3install
	cd $(PREFIX)/lib/python$(PYTHON3_SHORT_VERSION)/site-packages/python_demeter-2022.0.2-py3.10-linux-x86_64.egg && cp -R demeter .. && cp -R EGG-INFO ../python_demeter-2022.0.2-py3.10-linux-x86_64.egg-info
