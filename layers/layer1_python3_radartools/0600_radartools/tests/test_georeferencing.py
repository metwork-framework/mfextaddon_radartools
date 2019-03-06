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
        print("POINTTARGET:%s\n" % str(proj.getPointXY(point)))
        point_calc = proj.getPointXY(point)
        print("POINTCALC:%s\n" % str(point_calc))
        self.assertEqual(point_calc.GetX(), 4126.5246130275855)
        self.assertEqual(point_calc.GetY(), -78738.7801864541)
