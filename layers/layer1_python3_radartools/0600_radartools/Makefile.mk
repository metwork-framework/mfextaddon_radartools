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

all:: $(PREFIX)/lib/python$(PYTHON3_SHORT_VERSION)/site-packages/radar_tools-0.0.1.dist-info

$(PREFIX)/lib/python$(PYTHON3_SHORT_VERSION)/site-packages/radar_tools-0.0.1.dist-info:
	$(MAKE) clean
	layer_wrapper --layers=$(LAYER_NAME)@mfext -- unsafe_pip install --prefix=$(PREFIX) --src=$(PYTHON3_SITE_PACKAGES) . && rm -f $(PYTHON3_SITE_PACKAGES)/$(NAME)-$(VERSION).dist-info/direct_url.json

test:
	@echo "***** PYTHON TESTS *****"
	flake8.sh --exclude=build .
	find . -name "*.py" ! -path './build/*' -print0 |xargs -0 pylint.sh --errors-only
	cd tests && layer_wrapper --layers=python3_devtools@mfext,python3_radartools@mfext -- nosetests .
