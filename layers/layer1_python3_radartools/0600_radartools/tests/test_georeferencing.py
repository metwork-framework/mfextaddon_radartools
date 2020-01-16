#!/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
import radar_tools.common.georeferencing as georeferencing
from osgeo import ogr


class TestGeoreferencing(TestCase):
    """Classe de test du module georeferencing."""

    def test01_ProjectionStereoPolaire(self):
        u"""Teste la projection stéréo polaire."""
        proj = georeferencing.ProjectionStereoPolaire(45, 0)
        cr = proj.makeSpatialReference()
        self.assertEqual(cr, True)
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(3, 45)
        proj.getPointXY(point)
        print("POINTCALC:%s\n" % str(point))
        self.assertEqual(round(point.GetX(), 2), 236432.44)
        self.assertEqual(round(point.GetY(), 2), -4511399.79)
