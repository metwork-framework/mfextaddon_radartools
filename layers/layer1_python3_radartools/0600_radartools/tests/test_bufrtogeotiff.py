#!/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
import os
import radar_tools.scripts.bufrtogeotiff as bufrtogeotiff
import gdal


def get_data_folder():
    path = os.path.join(os.path.dirname(__file__), 'data')
    return path


def get_tmp_folder():
    path = os.path.join(os.path.dirname(__file__), 'tmp')
    if not os.path.exists(path):
        os.makedirs(path)
    return path


class TestBufrtogeotiff(TestCase):
    """Classe de test du module bufrtogeotiff."""

    def transcodage(self, name):
        mfext_home = os.environ['MFEXT_HOME']
        python_mode = os.environ['METWORK_PYTHON_MODE']
        os.environ['DEMETER_TABLE'] = \
            "%s/opt/python%s_radartools/share/tables" % (mfext_home,
                                                         python_mode)
        os.environ['DEMETER_IMAGE'] = \
            "%s/opt/python%s_radartools/share/templates_pixmap" % (mfext_home,
                                                                   python_mode)
        os.environ['PROJ_LIB'] = "%s/opt/scientific_core/share/proj" \
                                 % mfext_home
        location_org = "%s/%s.bufr" % (get_data_folder(), name)
        location_dest = "%s/%s.geotiff" % (get_tmp_folder(), name)
        location_target = "%s/%s.geotiff" % (get_data_folder(), name)
        cr = bufrtogeotiff.bufrtogeotiff(location_org, location_dest)
        self.assertTrue(cr)
        dataset_target = gdal.Open(location_target)
        dataset_dest = gdal.Open(location_dest)
        self.assertEqual(
            [round(a, 4) for a in dataset_target.GetGeoTransform()],
            [round(a, 4) for a in dataset_dest.GetGeoTransform()])
        self.assertEqual(dataset_target.RasterXSize,
                         dataset_dest.RasterXSize)
        self.assertEqual(dataset_target.RasterYSize,
                         dataset_dest.RasterYSize)

    def test01_script(self):
        u"""Teste bufrtogeotiff."""
        self.transcodage("IMFR27LFPW_20170113124000")

    def test02_script(self):
        u"""Teste bufrtogeotiff."""
        self.transcodage("07578_20170228151000_ZBAS")

    def test03_script(self):
        u"""Teste bufrtogeotiff."""
        self.transcodage("Image_Bouchee_Serval_201709141200")

    def test04_script(self):
        u"""Teste bufrtogeotiff."""
        self.transcodage("IMFR21LFPW150000")
