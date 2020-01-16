# -*- coding: utf-8 -*-
from osgeo import ogr, osr
#  from osgeo.gdalconst import *

import logging
log = logging.getLogger(__name__)


class Projection:
    """Classe de base des projections."""

    __type = None
    __spatialReference = None

    def __init__(self, type):
        """Constructeur."""
        self.__type = type

    def getPointXY(self, pointLatLon):
        u"""Point dans le plan de projection.

        Calcule les coordonnées du point dans le systeme de projection et le
        retourne à partir des coordonnées en lat lon
        @param pointLatLon Point en lat lon
        @return coordonnée du point dans le plan de projection
        """
        sourceProjection = osr.SpatialReference()
        # Pour assurer compatibilité GDAL 2 <-> GDAL 3
        if 'SetAxisMappingStrategy' in dir(sourceProjection):
            sourceProjection.SetAxisMappingStrategy(
                osr.OAMS_TRADITIONAL_GIS_ORDER)  # pylint: disable=E1101
        sourceProjection.ImportFromEPSG(4326)
        if self.__spatialReference is None:
            log.debug("pas de spatial")
        coordTrans = osr.CoordinateTransformation(sourceProjection,
                                                  self.__spatialReference)
        pointLatLon.Transform(coordTrans)
        return pointLatLon

    def getPointLatLon(self, point):
        u"""Point dans lat lon (EPSG4326).

        Calcule les coordonnées du point en lat lon à partir des coordonnées
        dans le systeme de projection
        @param pointLatLon Point dans le plan de projection
        @return coordonnée du point en lat lon
        """
        targetProjection = osr.SpatialReference()
        # Pour assurer compatibilité GDAL 2 <-> GDAL 3
        if 'SetAxisMappingStrategy' in dir(targetProjection):
            targetProjection.SetAxisMappingStrategy(
                osr.OAMS_TRADITIONAL_GIS_ORDER)  # pylint: disable=E1101
        targetProjection.ImportFromEPSG(4326)
        coordTrans = osr.CoordinateTransformation(
            self.__spatialReference, targetProjection)
        point.Transform(coordTrans)
        return point

    def getType(self):
        u"""Type de projection.

        @return type de projection
        """
        return self.__type

    def getSpatialReference(self):
        u"""Spatial référence de la projection.

        Retourne la référence spatiale de la projection
        @return Référence spatiale de la projection
        """
        return self.__spatialReference

    def makeSpatialReference(self, chaineProj4):
        u"""Fabrique la projection.

        Fabrique la projection à partir de la chaine proj4
        @param chaineProj4 chaine proj4 décrivant la projection
        @return satial référence de la projection
        """
        self.__spatialReference = osr.SpatialReference()
        self.__spatialReference.ImportFromProj4(chaineProj4)

    def getProj4String(self):
        return self.__spatialReference.ExportToProj4()


class ProjectionStereoPolaire(Projection):
    u"""Classe Projection stéréo polaire."""

    def __init__(self, lat_ts, lon_0, lat_0=90, req=6378137.0, rpo=6356752.0):
        u"""Constructeur.

        Constructeur de la classe stéréopolaire
        """
        Projection.__init__(self, "StereoPolaire")
        self.__lat_ts = req
        self.__req = req
        self.__rpo = rpo
        self.__lon_0 = lon_0
        self.__lat_0 = lat_0
        self.__lat_ts = lat_ts
        self.makeSpatialReference()

    ##
    # Fabrication de la projection
    #
    # @return True si la fabrication de la projection est OK
    def makeSpatialReference(self):
        u"""Fabrique.

        Fabrique la projection
        @return True si OK
        """
        if (self.__lon_0 is None):
            log.warning("lon_0 unknown")
            return False
        if (self.__lat_ts is None):
            log.warning("lat_ts unknown")
            return False
        chaineProj4 = "+proj=stere +a=%.2f +b=%.2f +lon_0=%.2f "\
            "+lat_0=%d +lat_ts=%d" % (
                self.__req, self.__rpo, self.__lon_0, self.__lat_0,
                self.__lat_ts)
        Projection.makeSpatialReference(self, chaineProj4)
        return True


class ProjectionRadarLocal(Projection):
    u"""Classe Projection type radar local (plan tangeant)"""

    def __init__(self, lon_rad, lat_rad, req=6378137.0, rpo=6356752.0):
        u"""Constructeur.

        Constructeur de la classe projection radar local
        """
        self.__type = "RadarLocal"
        self.__req = req
        self.__rpo = rpo
        self.__lon_rad = lon_rad
        self.__lat_rad = lat_rad
        self.makeSpatialReference()

    def makeSpatialReference(self):
        u"""Fabrique.

        Fabrique la projection
        @return True si OK
        """
        self.__spatialReference = None
        if (self.__lon_rad is None):
            log.warning("lon_rad unknown")
            return False
        if (self.__lat_rad is None):
            log.warning("lar_rad unknown")
            return False
        chaineProj4 = "+proj=gnom +a=%.2f +b=%.2f +lon_0=%.2f +lat_0=%d" % (
            self.__req, self.__rpo, self.__lon_rad, self.__lat_rad)
        Projection.makeSpatialReference(self, chaineProj4)
        return True


class ProjectionMercatorStandard(Projection):
    u"""Classe Projection type mercator standard."""

    def __init__(self):
        u"""Constructeur.

        Constructeur de la classe projection mercator standard
        """
        Projection.__init__(self, "Mercator Standard")
        self.makeSpatialReference()

    def makeSpatialReference(self):
        u"""Fabrique.

        Fabrique la projection
        @return True si OK
        """
        chaineProj4 = "+proj=merc +lon_0=0 +k=1 +x_0=0 +y_0=0 "\
            "+ellps=WGS84 +datum=WGS84 +units=m +no_defs"
        Projection.makeSpatialReference(self, chaineProj4)
        return True


class ProjectionMercator(Projection):
    u"""Classe Projection type mercator oblique."""

    def __init__(self, lat_0, lon_0, lat_1=90., req=6378137.0, rpo=6356752.0):
        u"""Constructeur.

        Constructeur de la classe projection mercator oblique
        """
        Projection.__init__(self, "Mercator Oblique")
        self.__lat_0 = lat_0
        self.__lon_0 = lon_0
        self.__lat_1 = lat_1
        self.__req = req
        self.__rpo = rpo
        self.makeSpatialReference()

    def makeSpatialReference(self):
        u"""Fabrique.

        Fabrique la projection
        @return True si OK
        """
        if (self.__lat_0 is None):
            log.warning("lat_0 unknown")
            return False
        if (self.__lon_0 is None):
            log.warning("lon_0 unknown")
            return False
        if (self.__lat_1 is None):
            log.warning("lat_1 unknown")
            return False
        chaineProj4 = "+proj=omerc +lat_0=%.2f +lon_0=%.2f "\
            "+lat_1=%.4f +a +es=%.4f" % (self.__lat_0, self.__lon_0,
                                         self.__lat_1, self.__req)
#        chaineProj4 = "+proj=omerc +lat_0=%.2f +lon_0=%.2f "\
#            "+lat_1=%.4f +a +es=%.4f" % (self.__lat_0, self.__lon_0,
#                                         self.__lat_1, self.__req, self.__rpo)

        Projection.makeSpatialReference(self, chaineProj4)
        return True


class ProjectionLambertConforme(Projection):
    u"""Classe Projection type lambert conforme."""

    def __init__(self, lat_org, lon_org, lat_1, lat_2):
        u"""Constructeur.

        Constructeur de la classe projection mercator oblique
        """
        Projection.__init__(self, "Lambert Conforme")
        self.__lat_org = lat_org
        self.__lon_org = lon_org
        self.__lat_1 = lat_1
        self.__lat_2 = lat_2
        self.makeSpatialReference()

    def makeSpatialReference(self):
        u"""Fabrique.

        Fabrique la projection
        @return True si OK
        """
        if (self.__lat_org is None):
            log.warning("lat_org unknown")
            return False
        if (self.__lon_org is None):
            log.warning("lon_org unknown")
            return False
        if (self.__lat_1 is None):
            log.warning("lat_1 unknown")
            return False
        if (self.__lat_2 is None):
            log.warning("lat_2 unknown")
            return False

        chaineProj4 = "+proj=lcc   +lat_1=%.2f  "\
            "+lon_0=0 +lat_2=%.2f +ellps=sphere" % (self.__lat_1, self.__lat_2)
        Projection.makeSpatialReference(self, chaineProj4)
        return True


class Domaine:
    u"""Classe domaine."""

    __lonNO = None
    __latNO = None
    __pixelSizeX = None
    __pixelSizeY = None
    __numberPixelX = None
    __numberPixelY = None

    def __init__(self, lonNO, latNO,
                 pixelSizeX, pixelSizeY,
                 numberPixelX, numberPixelY):
        """Constructeur."""
        self.__lonNO = lonNO
        self.__latNO = latNO
        self.__pixelSizeX = pixelSizeX
        self.__pixelSizeY = pixelSizeY
        self.__numberPixelX = numberPixelX
        self.__numberPixelY = numberPixelY

    def __str__(self):
        chaine = "Domaine -> "
        chaine += "Corner NO:[lon=" + str(self.__lonNO) + "-lat=" +\
            str(self.__latNO) + "] "
        chaine += "Pixel Size:[lon=" + str(self.__pixelSizeX) + "-lat=" +\
            str(self.__pixelSizeY) + "] "
        chaine += "Number Pixel:[X=" + str(self.__numberPixelX) + "-Y=" +\
            str(self.__numberPixelY) + "] "
        return chaine

    def getCornerNO(self):
        pointNO = ogr.Geometry(ogr.wkbPoint)
        pointNO.AddPoint(self.__lonNO, self.__latNO)
        return pointNO

    def getPixelSizeX(self):
        return self.__pixelSizeX

    def getPixelSizeY(self):
        return self.__pixelSizeY

    def getNumberPixelX(self):
        return self.__numberPixelX

    def getNumberPixelY(self):
        return self.__numberPixelY


class CornersDomain:
    u"""Classe domaine défini par ses 4 coins."""

    lonNO = None
    latNO = None
    lonNE = None
    latNE = None
    lonSE = None
    latSE = None
    lonSO = None
    latSO = None

    def __init__(self, lonNO, latNO, lonNE, latNE, lonSE, latSE, lonSO, latSO):

        self.lonNO = lonNO
        self.latNO = latNO
        self.lonNE = lonNE
        self.latNE = latNE
        self.lonSE = lonSE
        self.latSE = latSE
        self.lonSO = lonSO
        self.latSO = latSO

    def __str__(self):
        chaine = "Domaine Coins-> "
        chaine += "Corner NO:[lon=" + str(self.lonNO) + "-lat=" +\
            str(self.latNO) + "] "
        chaine += "Corner NE:[lon=" + str(self.lonNE) + "-lat=" +\
            str(self.latNE) + "] "
        chaine += "Corner SE:[lon=" + str(self.lonSE) + "-lat=" +\
            str(self.latSE) + "] "
        chaine += "Corner SO:[lon=" + str(self.lonSO) + "-lat=" +\
            str(self.latSO) + "] "
        return chaine


class Vue:
    """Classe vue combinaison d'un domaine et d'uine projection"""

    __projection = None
    __domaine = None

    def __init__(self, projection, domaine):
        self.__projection = projection
        self.__domaine = domaine

    def getPointNOXY(self):
        u"""Point Nord Ouest dans le plan de projection.

        Calcule les coordonnées du point NO dans le systeme de projection et
        le retourne à partir des coordonnées en lat lon
        @return Point Nord Ouest dans le pla de projection
        """
        return self.__projection.getPointXY(self.__domaine.getCornerNO())

    def getPointSEXY(self):
        u"""Point Sud Est dans le plan de projection.

        Il ne s'agit pas d'un point en petite tenu mais du point Sud Est
        dans le plan de projection
        @return Point Sud Est dans le plan de projection
        """
        pointNO = self.getPointNOXY()
        xNO = pointNO.GetX()
        yNO = pointNO.GetY()
        log.debug("xNO : %s" % xNO)
        xSE = xNO + (self.__domaine.getNumberPixelX()
                     * self.__domaine.getPixelSizeX())  # noqa: W503
        log.debug("xSE : %s" % xSE)
        ySE = yNO - (self.__domaine.getNumberPixelY()
                     * self.__domaine.getPixelSizeY())  # noqa: W503
        log.debug("ySE : %s" % ySE)
        pointSE = ogr.Geometry(ogr.wkbPoint)
        pointSE.AddPoint(xSE, ySE)
        return pointSE

    def getResolutions(self):
        u"""Résolution en x et en y."""
        pointNO = self.getPointNOXY()
        log.debug("Point NO recupere")
        pointSE = self.getPointSEXY()
        log.debug("Point SE recupere")
        resX = (pointSE.GetX() - pointNO.GetX()) /\
            self.__domaine.getNumberPixelX()
        log.debug("resX : %s" % resX)
        resY = (pointSE.GetY() - pointNO.GetY()) /\
            self.__domaine.getNumberPixelY()
        log.debug("resY : %s" % resY)
        return resX, resY

    def getProjection(self):
        return self.__projection

    def getDomaine(self):
        return self.__domaine


def test_point(proj, lon, lat):
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lon, lat)
    print(point)
    proj.getPointXY(point)
    print(point)
    proj.getPointLatLon(point)
    print(point)
