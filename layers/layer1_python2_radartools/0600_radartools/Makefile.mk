include ../../../adm/root.mk
include $(MFEXT_HOME)/share/package.mk

export NAME=radartools
export VERSION=0.0.1
DESCRIPTION=\
Une lib python autour des donnees radar meteofrance.
WEBSITE=http://www.meteo.fr
LICENSE=Proprietaire

clean::
	rm -rf build dist *.egg-info                                                
	rm -f `find -name "*.pyc"`                                                  
	rm -rf `find -name "__pycache__"`                                           
	rm -rf tests/.coverage tests/coverage         

all:: $(PREFIX)/lib/python$(PYTHON2_SHORT_VERSION)/site-packages/radar_tools-0.0.1-py$(PYTHON2_SHORT_VERSION).egg

$(PREFIX)/lib/python$(PYTHON2_SHORT_VERSION)/site-packages/radar_tools-0.0.1-py$(PYTHON2_SHORT_VERSION).egg:
	$(MAKE) clean
	layer_wrapper --layers=$(LAYER_NAME)@mfext -- python setup.py install --prefix=$(PREFIX)
