#!/bin/env python
# -*- coding: utf-8 -*-

from osgeo import ogr
import radar_tools.common.mtomath as mtomath
import radar_tools.common.georeferencing as georeferencing

from demeter import Descriptor
from datetime import datetime, timedelta
import logging

log = logging.getLogger()

DATE_DESCRIPTORS = (
    Descriptor(0, 4, 1),  # Année
    Descriptor(0, 4, 2),  # Mois
    Descriptor(0, 4, 3),  # Jour
    Descriptor(0, 4, 4),  # Heure
    Descriptor(0, 4, 5),  # Minute
    Descriptor(0, 4, 6),   # Seconde
)
DATE_DESCRIPTORS_2 = (
    Descriptor(0, 4, 1),  # Année
    Descriptor(0, 4, 2),  # Mois
    Descriptor(0, 4, 3),  # Jour
    Descriptor(0, 4, 4),  # Heure
    Descriptor(0, 4, 5),  # Minute
)


def getDate(data_bufr):
    def check_year(an):
        if an < 1900 and an >= 80:
            an += 1900
        elif an < 1900 and an < 80:
            an += 2000
        return an

    rule_value = data_bufr.getValueByGroupDescr(DATE_DESCRIPTORS)
    if rule_value:
        (an, mois, jour, heure, minute, seconde) = rule_value
        an = check_year(an)
        return datetime(int(an), int(mois), int(jour),
                        int(heure), int(minute), int(seconde))
    rule_value = data_bufr.getValueByGroupDescr(DATE_DESCRIPTORS_2)
    if rule_value:
        (an, mois, jour, heure, minute) = rule_value
        an = check_year(an)

        return datetime(int(an), int(mois), int(jour), int(heure), int(minute))


COMPOSITE_DESCRIPTOR = Descriptor(0, 1, 192)

INDICATIFOMM_DESCRIPTORS = (
    Descriptor(0, 1, 1),  # Bloc
    Descriptor(0, 1, 2),  # Station
)


def getIndicatifOMM(data_bufr):
    value = data_bufr.getValueByGroupDescr(INDICATIFOMM_DESCRIPTORS)
    if value is not None:
        (block, station) = value
        return int(block) * 1000 + int(station)


def getIndicator(data_bufr):
    u"""L'indicateur de la donnée.

    Il s'agit de l'indicateur de composite et a défaut de l'indicatif OMM
    """
    indicateur_composite = data_bufr.getValueByDescr(COMPOSITE_DESCRIPTOR)

    if indicateur_composite is None:
        return getIndicatifOMM(data_bufr)
    else:
        return indicateur_composite


def getMosaicIndicator(data_bufr):
    return data_bufr.getValueByDescr(COMPOSITE_DESCRIPTOR)


PICTURE_TYPE_DESCRIPTOR = Descriptor(0, 30, 31)


def getPictureType(data_bufr):
    return data_bufr.getValueByDescr(PICTURE_TYPE_DESCRIPTOR)


UNIQUE_PRODUCT_IDENTIFIER_DESCRIPTOR = Descriptor(0, 1, 99)


def getUniqueProductIdentifier(data_bufr):
    return data_bufr.getValueByDescr(UNIQUE_PRODUCT_IDENTIFIER_DESCRIPTOR)


# 4 coins en haute précision
FOUR_CORNERS_1_DESCRIPTORS = (
    Descriptor(0, 5, 1),  # Latitude
    Descriptor(0, 6, 1),  # Longitude
    Descriptor(0, 5, 1),  # Latitude
    Descriptor(0, 6, 1),  # Longitude
    Descriptor(0, 5, 1),  # Latitude
    Descriptor(0, 6, 1),  # Longitude
    Descriptor(0, 5, 1),  # Latitude
    Descriptor(0, 6, 1),  # Longitude
)


# 4 coins en petite précision
FOUR_CORNERS_2_DESCRIPTORS = (
    Descriptor(0, 5, 2),  # Latitude
    Descriptor(0, 6, 2),  # Longitude
    Descriptor(0, 5, 2),  # Latitude
    Descriptor(0, 6, 2),  # Longitude
    Descriptor(0, 5, 2),  # Latitude
    Descriptor(0, 6, 2),  # Longitude
    Descriptor(0, 5, 2),  # Latitude
    Descriptor(0, 6, 2),  # Longitude
)


def getFourCorners(data_bufr):
    u"""Retourne les 4 coins de l'image.

    Retourne les 4 coins de l'image sous la forme d'un tupple dans l'ordre
    suivant:
    latitudeNO, longitudeNO, latitudeNE, longitudeNE,
    latitudeSE, longitudeSE,latitudeSO, longitudeSO
    @param donnée bufr issu du decodage
    @return tupple
    """
    rule_value = data_bufr.getValueByGroupDescr(FOUR_CORNERS_1_DESCRIPTORS)

    if rule_value is None:
        rule_value = data_bufr.getValueByGroupDescr(FOUR_CORNERS_2_DESCRIPTORS)
    return rule_value


TYPE_PROJECTION_1_DESCRIPTOR = Descriptor(0, 29, 1)


TYPE_PROJECTION_2_DESCRIPTOR = Descriptor(0, 29, 201)


# Taille du pixel en x et en y
PIXEL_SIZE_DESCRIPTORS = (Descriptor(0, 5, 33), Descriptor(0, 6, 33),)

# Nombre de lignes et nombre de colonnes
DATA_SIZE_DESCRIPTORS = (Descriptor(0, 30, 21), Descriptor(0, 30, 22),)

# Coordonnées coin NO  Haute precision, Basse précision, BUFR INTERNATIONA
POINT_LAT_LON_1_DESCRIPTORS = (Descriptor(0, 5, 1), Descriptor(0, 6, 1),)
POINT_LAT_LON_2_DESCRIPTORS = (Descriptor(0, 5, 2), Descriptor(0, 6, 2),)
POINT_LAT_LON_3_DESCRIPTORS = (Descriptor(0, 29, 194), Descriptor(0, 29, 193),)

POINT_DISTANCE_NO_DESCRIPTORS = (Descriptor(0, 5, 192),
                                 Descriptor(0, 6, 192),)


def getResolution(data_bufr):
    u"""Résolution.

    Retourne la résolution. On teste si la valeur enx et en y est la même et
    on la retourne sinon on retourne None
    Cette valeur est destiné à reconnaitre le processus
    """
    (reso_x, reso_y) = data_bufr.getValueByGroupDescr(PIXEL_SIZE_DESCRIPTORS)
    if reso_x == reso_y:
        return int(reso_x)
    else:
        return None


def getVue(data_bufr, meta_definition_projection=None):
    u"""Vue.

    Récupération de la vue dans le bufr
    Eventuellement on fournit la definition de la projecton
    """
    def getLatitudeLongitude(data_bufr):
        lat_lon = data_bufr.getValueByGroupDescr(POINT_LAT_LON_1_DESCRIPTORS)
        if lat_lon is None:
            lat_lon = data_bufr.getValueByGroupDescr(
                POINT_LAT_LON_2_DESCRIPTORS)
        if lat_lon is None:
            lat_lon = data_bufr.getValueByGroupDescr(
                POINT_LAT_LON_3_DESCRIPTORS)
        log.debug("lat_lon:%s" % str(lat_lon))
        return lat_lon

    # Cas ou on met la definition de la projection dans le BUFR probleme lié
    # aux antilles
    if meta_definition_projection is not None:
        log.debug("PROJECTION issu des metadata")
        domaine_corners = data_bufr.getValueByGroupDescr(
            FOUR_CORNERS_1_DESCRIPTORS)
        if domaine_corners is not None:
            (latNO, lonNO, latNE, lonNE, latSE, lonSE, latSO, lonSO) =\
                domaine_corners
        else:
            domaine_corners = data_bufr.getValueByGroupDescr(
                FOUR_CORNERS_2_DESCRIPTORS)
        if domaine_corners is not None:
            (latNO, lonNO, latNE, lonNE, latSE, lonSE, latSO, lonSO) =\
                domaine_corners
        else:
            (latNO, lonNO) = data_bufr.getValueByGroupDescr(
                POINT_LAT_LON_1_DESCRIPTORS)

        (pixel_size_x, pixel_size_y) = data_bufr.getValueByGroupDescr(
            PIXEL_SIZE_DESCRIPTORS)
        log.debug("pixel_size_x:%d, pixel_size_y:%d" % (int(pixel_size_x),
                                                        int(pixel_size_y)))
        (pixels_per_row, pixels_per_column) = data_bufr.getValueByGroupDescr(
            DATA_SIZE_DESCRIPTORS)
        log.debug("pixels_per_row:%d,pixel_per_column:%d" % (
            int(pixels_per_row), int(pixels_per_column)))
        domaine = georeferencing.Domaine(lonNO, latNO,
                                         pixel_size_x, pixel_size_y,
                                         pixels_per_row, pixels_per_column)
        log.debug("projection : %s" %
                  meta_definition_projection.getSpatialReference())
        log.debug("domaine : %s" %
                  domaine)
        vue = georeferencing.Vue(meta_definition_projection, domaine)
        log.debug('NO:%s' %
                  meta_definition_projection.getPointLatLon(vue.
                                                            getPointNOXY()))
        log.debug('SE:%s' %
                  meta_definition_projection.getPointLatLon(vue.
                                                            getPointSEXY()))
        return vue

    # Premier cas : On verifie le descripteur 0 29 205 decrivant la projection
    chaineproj4 = data_bufr.getValueByDescr(Descriptor(0, 29, 205))
    if chaineproj4 is not None:
        log.debug("Traitement chaine proj4 : %s" % (chaineproj4))

        try:
            projection = georeferencing.Projection(None)
            georeferencing.Projection.makeSpatialReference(projection,
                                                           chaineproj4)
            four_corners = getFourCorners(data_bufr)
            (pixel_size_x, pixel_size_y) = data_bufr.getValueByGroupDescr(
                PIXEL_SIZE_DESCRIPTORS)
            log.debug("pixel_size_x:%d, pixel_size_y:%d" % (int(pixel_size_x),
                                                            int(pixel_size_y)))
            (pixels_per_row, pixels_per_column) =\
                data_bufr.getValueByGroupDescr(DATA_SIZE_DESCRIPTORS)
            log.debug("pixels_per_row:%d,pixel_per_column:%d" %
                      (int(pixels_per_row), int(pixels_per_column)))
            if four_corners is None:
                # On recherche si presence coin NO du radar
                distance_coin_NO = data_bufr.getValueByGroupDescr(
                    POINT_DISTANCE_NO_DESCRIPTORS)
                if distance_coin_NO is not None:
                    (distance_ouest_est, distance_nord_sud) = distance_coin_NO
                    (lat_rad, lon_rad) = data_bufr.getValueByGroupDescr(
                        POINT_LAT_LON_1_DESCRIPTORS) \
                        if data_bufr.getValueByGroupDescr(
                            POINT_LAT_LON_1_DESCRIPTORS) \
                        else data_bufr.getValueByGroupDescr(
                            POINT_LAT_LON_2_DESCRIPTORS)
                    point_radar = ogr.Geometry(ogr.wkbPoint)
                    point_radar.AddPoint(lon_rad, lat_rad)
                    point_radar = projection.getPointXY(point_radar)
                    xRad = point_radar.GetX()
                    yRad = point_radar.GetY()
                    xNO = xRad - distance_ouest_est
                    yNO = yRad + distance_nord_sud
                    pointNO = ogr.Geometry(ogr.wkbPoint)
                    pointNO.AddPoint(xNO, yNO)
                    pointNO = projection.getPointLatLon(pointNO)
                    lonNO = pointNO.GetX()
                    latNO = pointNO.GetY()
                else:

                    (latNO, lonNO) = data_bufr.getValueByGroupDescr(
                        POINT_LAT_LON_1_DESCRIPTORS) \
                        if data_bufr.getValueByGroupDescr(
                            POINT_LAT_LON_1_DESCRIPTORS) \
                        else data_bufr.getValueByGroupDescr(
                            POINT_LAT_LON_2_DESCRIPTORS)
            else:
                latNO, lonNO, latNE, lonNE, latSE, lonSE, latSO, lonSO =\
                    four_corners
            domaine = georeferencing.Domaine(lonNO, latNO,
                                             pixel_size_x, pixel_size_y,
                                             pixels_per_row, pixels_per_column)
            log.debug("projection : %s" % projection.getSpatialReference())
            log.debug("domaine : %s" % domaine)
            return georeferencing.Vue(projection, domaine)
        except Exception as e:
            log.warning("Definition vue pour projection"
                        "type proj4 (%s) impossible %s " % (
                            chaineproj4, str(e)))

    type_projection = data_bufr.getValueByDescr(TYPE_PROJECTION_1_DESCRIPTOR)
    if type_projection is None:
        type_projection = data_bufr.getValueByDescr(
            TYPE_PROJECTION_2_DESCRIPTOR)
    if type_projection == 0:   # Projection gnomonique
        # Recherche definition de la projection à partir de la structure
        PROJ_GNOMONIC_DESCRIPTORS = (Descriptor(0, 29, 193),
                                     Descriptor(0, 29, 194),
                                     Descriptor(0, 29, 195),
                                     Descriptor(0, 29, 196))
        def_proj = data_bufr.getValueByGroupDescr(PROJ_GNOMONIC_DESCRIPTORS)
        if def_proj is not None:
            lon_0, lat_0, x_offset, y_offset = def_proj

        chaineProj4 = "+proj=gnom +lat_0=%f +lon_0=%f " % (lat_0, lon_0)
        projection = georeferencing.Projection(None)
        georeferencing.Projection.makeSpatialReference(projection, chaineProj4)

        four_corners = getFourCorners(data_bufr)
        if four_corners is None:
            (latNO, lonNO) = data_bufr.getValueByGroupDescr(
                POINT_LAT_LON_1_DESCRIPTORS) \
                if data_bufr.getValueByGroupDescr(
                    POINT_LAT_LON_1_DESCRIPTORS) \
                else data_bufr.getValueByGroupDescr(
                    POINT_LAT_LON_2_DESCRIPTORS)
        else:
            latNO, lonNO, latNE, lonNE, latSE, lonSE, latSO, lonSO =\
                four_corners
        (pixel_size_x, pixel_size_y) = data_bufr.getValueByGroupDescr(
            PIXEL_SIZE_DESCRIPTORS)
        log.debug("pixel_size_x:%d, pixel_size_y:%d" % (int(pixel_size_x),
                                                        int(pixel_size_y)))
        (pixels_per_row, pixels_per_column) = data_bufr.getValueByGroupDescr(
            DATA_SIZE_DESCRIPTORS)
        log.debug("pixels_per_row:%d,pixel_per_column:%d" % (
            int(pixels_per_row), int(pixels_per_column)))
        domaine = georeferencing.Domaine(lonNO, latNO,
                                         pixel_size_x, pixel_size_y,
                                         pixels_per_row, pixels_per_column)
        log.debug("projection : %s" % projection.getSpatialReference())
        log.debug("domaine : %s" % domaine)
        return georeferencing.Vue(projection, domaine)
    if type_projection == 1:   # Projection stereoPolaire
        try:
            four_corners = getFourCorners(data_bufr)
            log.debug("four_corners:%s", str(four_corners))
            if four_corners is None:
                (latNO, lonNO) = data_bufr.getValueByGroupDescr(
                    POINT_LAT_LON_1_DESCRIPTORS) \
                    if data_bufr.getValueByGroupDescr(
                        POINT_LAT_LON_1_DESCRIPTORS) \
                    else data_bufr.getValueByGroupDescr(
                        POINT_LAT_LON_2_DESCRIPTORS)
            else:
                latNO, lonNO, latNE, lonNE, latSE, lonSE, latSO, lonSO =\
                    four_corners
            lon_0 = (lambda x: x if x else 0)(data_bufr.getValueByDescr(
                (0, 6, 198)))
            lat_ts = (lambda x: x if x else 60)(data_bufr.getValueByDescr(
                (0, 5, 195)))
            projection = georeferencing.ProjectionStereoPolaire(lat_ts, lon_0)
            log.debug("projection:%s", str(projection))
            (pixel_size_x, pixel_size_y) = data_bufr.getValueByGroupDescr(
                PIXEL_SIZE_DESCRIPTORS)
            log.debug("pixel_size_x:%d, pixel_size_y:%d" % (int(pixel_size_x),
                                                            int(pixel_size_y)))
            (pixels_per_row, pixels_per_column) =\
                data_bufr.getValueByGroupDescr(DATA_SIZE_DESCRIPTORS)
            log.debug("pixels_per_row:%d,pixel_per_column:%d" % (
                int(pixels_per_row), int(pixels_per_column)))
            (latitude, longitude) = getLatitudeLongitude(data_bufr)
            # Cas particulier Composite origine france seul les images ayant
            # servi à élaborer la composite sont décrite avec leurs 4 coins
            # if four_corners is not None and (latitude > latNO and
            # longitude <lonNO):
            # latNO=latitude
            # lonNO=longitude
            domaine = georeferencing.Domaine(lonNO, latNO,
                                             pixel_size_x, pixel_size_y,
                                             pixels_per_row, pixels_per_column)
            log.debug("projection : %s" % projection.getSpatialReference())
            log.debug("domaine : %s" % domaine)
            return georeferencing.Vue(projection, domaine)
        except Exception as e:
            log.warning(
                "Definition vue pour projection stéréopolaire impossible %s " %
                str(e))

    elif type_projection == 2:  # Lambert conforme
        try:
            four_corners = getFourCorners(data_bufr)
            if four_corners is None:
                (latNO, lonNO) = data_bufr.getValueByGroupDescr(
                    POINT_LAT_LON_1_DESCRIPTORS) \
                    if data_bufr.getValueByGroupDescr(
                        POINT_LAT_LON_1_DESCRIPTORS) \
                    else data_bufr.getValueByGroupDescr(
                        POINT_LAT_LON_2_DESCRIPTORS)
            else:
                latNO, lonNO, latNE, lonNE, latSE, lonSE, latSO, lonSO =\
                    four_corners
            # Recherche definition de la projection à partir de la structure
            PROJ_LAMBERT_CONFORME_DESCRIPTORS = (Descriptor(0, 29, 193),
                                                 Descriptor(0, 29, 194),
                                                 Descriptor(0, 29, 197),
                                                 Descriptor(0, 29, 198))
            def_proj = data_bufr.getValueByGroupDescr(
                PROJ_LAMBERT_CONFORME_DESCRIPTORS)
            if def_proj is not None:
                lon_org, lat_org, lat1, lat2 = def_proj
                log.debug(
                    'lat_org:%.2f - lon_org:%.2f - lat1:%.2f - lat2:%.2f' %
                    (lat_org, lon_org, lat1, lat2))
                chaineProj4 = "+proj=lcc   +lat_1=%.2f +lat_2=%.2f"\
                    " +lat_0=%.2f +lon_0=%.2f +x_0=0 +y_0=0" % (
                        lat1, lat2, lat_org, lon_org)

                projection = georeferencing.ProjectionLambertConforme(
                    lat_org, lon_org, lat1, lat2)
                georeferencing.Projection.makeSpatialReference(
                    projection, chaineProj4)
            else:
                lat_org = latNO
                lon_org = lonNO
                # On definit les paramettres autrement
                lat1 = data_bufr.getValueByDescr(Descriptor(0, 5, 2), 4)
                lat2 = data_bufr.getValueByDescr(Descriptor(0, 5, 2), 5)
                if lat1 is None or lat2 is None:
                    # Deuxieme strategie
                    lat1 = data_bufr.getValueByDescr(Descriptor(0, 29, 197))
                    lat2 = data_bufr.getValueByDescr(Descriptor(0, 29, 198))
                log.debug(
                    'lat_org:%.2f - lon_org:%.2f - lat1:%.2f - lat2:%.2f' %
                    (lat_org, lon_org, lat1, lat2))
                projection = georeferencing.ProjectionLambertConforme(
                    lat_org, lon_org, lat1, lat2)
            (pixel_size_x, pixel_size_y) = data_bufr.getValueByGroupDescr(
                PIXEL_SIZE_DESCRIPTORS)
            (pixels_per_row, pixels_per_column) =\
                data_bufr.getValueByGroupDescr(DATA_SIZE_DESCRIPTORS)
            domaine = georeferencing.Domaine(lonNO, latNO,
                                             pixel_size_x, pixel_size_y,
                                             pixels_per_row, pixels_per_column)
            log.debug("projection : %s" % projection.getSpatialReference())
            log.debug("domaine : %s" % domaine)
            return georeferencing.Vue(projection, domaine)
        except Exception as e:
            log.warning("Definition vue pour projection "
                        "lambert conforme impossible %s " % str(e))

    elif type_projection == 3:  # Si projection type mercator
        try:
            projection = None
            domaine_corners = data_bufr.getValueByGroupDescr(
                FOUR_CORNERS_1_DESCRIPTORS)
            if domaine_corners is not None:
                (latNO, lonNO, latNE, lonNE, latSE, lonSE, latSO, lonSO) =\
                    domaine_corners
            else:
                domaine_corners = data_bufr.getValueByGroupDescr(
                    FOUR_CORNERS_2_DESCRIPTORS)
            if domaine_corners is not None:
                (latNO, lonNO, latNE, lonNE, latSE, lonSE, latSO, lonSO) =\
                    domaine_corners
            else:
                (latNO, lonNO) = data_bufr.getValueByGroupDescr(
                    POINT_LAT_LON_1_DESCRIPTORS)

            # Recherche definition de la projection à partir de la structure
            PROJ_MERCATOR_DESCRIPTORS = (Descriptor(0, 29, 201),
                                         Descriptor(0, 29, 202),
                                         Descriptor(0, 29, 193),
                                         Descriptor(0, 29, 194),
                                         Descriptor(0, 29, 195),
                                         Descriptor(0, 29, 196))
            def_proj = data_bufr.getValueByGroupDescr(
                PROJ_MERCATOR_DESCRIPTORS)
            if def_proj is not None:
                type_proj, lat_ts, lon_org, lat_org, x_offset, y_offset =\
                    def_proj
                chaineProj4 = "+proj=omerc +lat_0=%f +lonc=%f +alpha=%f " % (
                    lat_org, lon_org, lat_ts)
                projection = georeferencing.Projection(None)
                georeferencing.Projection.makeSpatialReference(projection,
                                                               chaineProj4)
            else:
                # La composite suisse a les descripteurs en 2 parties
                PROJ_MERCATOR_DESCRIPTORS_SWISS_1 = (Descriptor(0, 29, 201),
                                                     Descriptor(0, 29, 202))
                def_proj1 = data_bufr.getValueByGroupDescr(
                    PROJ_MERCATOR_DESCRIPTORS_SWISS_1)

                PROJ_MERCATOR_DESCRIPTORS_SWISS_2 = (Descriptor(0, 29, 193),
                                                     Descriptor(0, 29, 194),
                                                     Descriptor(0, 29, 195),
                                                     Descriptor(0, 29, 196))
                def_proj2 = data_bufr.getValueByGroupDescr(
                    PROJ_MERCATOR_DESCRIPTORS_SWISS_2)
                if def_proj1 is not None and def_proj2 is not None:
                    type_proj, lat_ts = def_proj1
                    lon_org, lat_org, x_offset, y_offset = def_proj2
                    chaineProj4 = "+proj=omerc +lat_0=%f +lonc=%f +alpha=%f "\
                        % (lat_org, lon_org, lat_ts)
                    projection = georeferencing.Projection(None)
                    georeferencing.Projection.makeSpatialReference(
                        projection, chaineProj4)

            if projection is None:
                lon_0 = data_bufr.getValueByDescr(Descriptor(0, 6, 198))
                lat_ts = data_bufr.getValueByDescr(Descriptor(0, 5, 195))
                if lon_0 is not None and lat_ts is not None:  # Mercator 2SP
                    lat_0 = 0
                    projection = georeferencing.Projection(None)
                    log.debug("chaineproj4: +proj=merc +lat_0=%f +lon_0=%f "
                              "+lat_ts=%f +ellps=WGS84" % (
                                  lat_0, lon_0, lat_ts))
                    projection.makeSpatialReference(
                        "+proj=merc +lat_0=%f +lon_0=%f "
                        "+lat_ts=%f +ellps=WGS84" % (lat_0, lon_0, lat_ts))
                # TODO à reprendre traitement particulier BUFR international
                # elif self.__ttaaii == 'PAHM22TFFF' or
                # self.__ttaaii == 'PAMR21TFFF': # Cas particulier composite
                #                                # caraibes bufrinternational
                #                                # on met informations en dur
                # projection = Projection(None)
                # projection.makeSpatialReference('+proj=merc +lat_0=%f '
                #          '+lon_0=%f +lat_ts=%f +ellps=WGS84' %
                #           (0, -61.18, 15.501))
                else:  # Mercator 1SP
                    projection = georeferencing.ProjectionMercatorStandard()

            (pixel_size_x, pixel_size_y) = data_bufr.getValueByGroupDescr(
                PIXEL_SIZE_DESCRIPTORS)
            (pixels_per_row, pixels_per_column) =\
                data_bufr.getValueByGroupDescr(DATA_SIZE_DESCRIPTORS)
            log.debug("pixel_size_x%d pixel_size_y:%d "
                      "pixels_per_row:%d pixels_per_column:%d" % (
                          pixel_size_x, pixel_size_y,
                          pixels_per_row, pixels_per_column))
            domaine = georeferencing.Domaine(lonNO, latNO,
                                             pixel_size_x, pixel_size_y,
                                             pixels_per_row, pixels_per_column)
            log.debug("projection : %s" % projection.getSpatialReference())
            log.debug("domaine : %s" % domaine)
            vue = georeferencing.Vue(projection, domaine)
            log.debug('NO:%s' % projection.getPointLatLon(vue.getPointNOXY()))
            log.debug('SE:%s' % projection.getPointLatLon(vue.getPointSEXY()))
            return vue
        except Exception as e:
            log.warning(
                "Definition vue pour projection mercator impossible %s " %
                str(e))

    elif type_projection == 4:

        # Si projection type radar local
        try:
            # Recherche Si 5 informations points lat, lon en 005001 et 006001
            all_point_lat_lon = data_bufr.getAllByGroupDescr(
                POINT_LAT_LON_1_DESCRIPTORS)
            log.debug('all_point:%s' % str(all_point_lat_lon))
            if len(all_point_lat_lon) == 5:
                point_lat_lon_rad = all_point_lat_lon[4].values()
            else:
                point_lat_lon_rad = data_bufr.getValueByGroupDescr(
                    POINT_LAT_LON_3_DESCRIPTORS)\
                    if data_bufr.getValueByGroupDescr(
                        POINT_LAT_LON_3_DESCRIPTORS) is not None \
                    else data_bufr.getValueByGroupDescr(
                        POINT_LAT_LON_2_DESCRIPTORS, 4)  \
                    if data_bufr.getValueByGroupDescr(
                        POINT_LAT_LON_2_DESCRIPTORS, 4) is not None \
                    else data_bufr.getValueByGroupDescr(
                        POINT_LAT_LON_1_DESCRIPTORS) \
                    if data_bufr.getValueByGroupDescr(
                        POINT_LAT_LON_1_DESCRIPTORS) is not None  \
                    else data_bufr.getValueByGroupDescr(
                        POINT_LAT_LON_2_DESCRIPTORS)
            # et encore un cas particulier (Wideumont lat lon sont  inverses
            if point_lat_lon_rad is None:
                lat_rad = data_bufr.getValueByDescr(Descriptor(0, 29, 194))
                lon_rad = data_bufr.getValueByDescr(Descriptor(0, 29, 193))
                if lat_rad is not None and lon_rad is not None:
                    point_lat_lon_rad = (lat_rad, lon_rad)

            (pixel_size_x, pixel_size_y) = data_bufr.getValueByGroupDescr(
                PIXEL_SIZE_DESCRIPTORS)
            (pixels_per_row, pixels_per_column) =\
                data_bufr.getValueByGroupDescr(DATA_SIZE_DESCRIPTORS)
            if point_lat_lon_rad is not None:
                # On recherche si presence coin NO du radar
                (lat_rad, lon_rad) = point_lat_lon_rad
                projection = georeferencing.ProjectionRadarLocal(lon_rad,
                                                                 lat_rad)
                point_radar = ogr.Geometry(ogr.wkbPoint)
                point_radar.AddPoint(lon_rad, lat_rad)
                point_radar = projection.getPointXY(point_radar)

                distance_coin_NO = data_bufr.getValueByGroupDescr(
                    POINT_DISTANCE_NO_DESCRIPTORS)
                if distance_coin_NO is not None:
                    (distance_ouest_est, distance_nord_sud) = distance_coin_NO
                    xRad = point_radar.GetX()
                    yRad = point_radar.GetY()
                    xNO = xRad - distance_ouest_est
                    yNO = yRad + distance_nord_sud
                    pointNO = ogr.Geometry(ogr.wkbPoint)
                    pointNO.AddPoint(xNO, yNO)
                    pointNO = projection.getPointLatLon(pointNO)
                    lonNO = pointNO.GetX()
                    latNO = pointNO.GetY()
                else:
                    xRad = point_radar.GetX()
                    yRad = point_radar.GetY()
                    xNO = xRad - (pixels_per_row * pixel_size_x) / 2
                    yNO = yRad + (pixels_per_column * pixel_size_y) / 2
                    pointNO = ogr.Geometry(ogr.wkbPoint)
                    pointNO.AddPoint(xNO, yNO)
                    pointNO = projection.getPointLatLon(pointNO)
                    lonNO = pointNO.GetX()
                    latNO = pointNO.GetY()
            else:
                (latNO, lonNO) = data_bufr.getValueByGroupDescr(
                    POINT_LAT_LON_2_DESCRIPTORS)

            domaine = georeferencing.Domaine(lonNO, latNO,
                                             pixel_size_x, pixel_size_y,
                                             pixels_per_row, pixels_per_column)
            log.debug("projection : %s" % projection.getSpatialReference())
            log.debug("domaine : %s" % domaine)
            return georeferencing.Vue(projection, domaine)
        except Exception as e:
            log.warning("Definition vue pour projection "
                        "radar local impossible %s " % str(e))

    else:
        log.warning("Projection pas encore traitée %s " % type_projection)


UNITY_OF_MEASURE_DESCRIPTOR = Descriptor(0, 49, 209)


def getUnityOfMeasure(data_bufr, descriptor_image):
    u"""Unité de mesure.

    L'unité de la mesure dépend du sous type du descripteur de l'image
    et de l'unité de la mesure dans le bufr
    0   En centiemes de mm
    1   En dixiemes de mm
    2   En mm
    3   Valeur manquante
    """
    uom = None
    if descriptor_image == Descriptor(0, 3, 4) or\
       descriptor_image == Descriptor(0, 30, 2) or\
       descriptor_image == Descriptor(0, 30, 1):
        sous_type = data_bufr.sub_category
        val_uom = data_bufr.getValueByDescr(UNITY_OF_MEASURE_DESCRIPTOR)
        if val_uom == 0:
            uom = '1/100 mm'
        elif val_uom == 1:
            uom = '1/10 mm'
        elif val_uom == 2:
            uom = '1 mm'
        elif sous_type in [0, 1, 20, 21, 30, 31, 32, 33]:
            uom = 'dbZ'
        elif sous_type in [2, 3, 22, 23]:
            uom = '1/10 mm'
        if uom is None:
            log.debug("Unknown unity of measure : %s" % (val_uom))
        else:
            log.debug("Unity of measure : %s(%s)" % (uom, val_uom))
    return uom


TEMPORAL_CHARACTERISTIC_DESCRIPTORS = [  # En GENERAL
    (Descriptor(0, 8, 21),
     Descriptor(0, 4, 1),
     Descriptor(0, 4, 2),
     Descriptor(0, 4, 3),
     Descriptor(0, 4, 4),
     Descriptor(0, 4, 5),),
    # En GENERAL
    (Descriptor(0, 8, 21),
     Descriptor(0, 4, 23),
     Descriptor(0, 4, 24),
     Descriptor(0, 4, 25),
     Descriptor(0, 4, 26),),
    # Pour 2PIR
    (Descriptor(0, 8, 21),
     Descriptor(0, 4, 25),),
    # Pour Aiga Cumul
    (Descriptor(0, 8, 21),
     Descriptor(0, 4, 24),
     Descriptor(0, 4, 25),),
    # Pour Aiga Facteur de Risque (Le troisième descripteur
    # est la pour ne pas reprendre la sequence precedente
    (Descriptor(0, 8, 21),
     Descriptor(0, 4, 24),
     Descriptor(0, 29, 1),),
    # Pour Aiga Facteur de Risque ? Est ce bien utile
    (Descriptor(0, 8, 1),
     Descriptor(0, 4, 1),
     Descriptor(0, 4, 2),
     Descriptor(0, 4, 3),
     Descriptor(0, 4, 4),
     Descriptor(0, 4, 5),),
]


def getTemporalCharacteristics(data_bufr, dat):

    def readPeriod(descriptor_value):
        duree_period = 0
        for dv in descriptor_value:
            if dv['descriptor'] == Descriptor(0, 4, 23):
                duree_period += int(dv['value']) * 86400
            elif dv['descriptor'] == Descriptor(0, 4, 24):
                duree_period += int(dv['value']) * 3600
            elif dv['descriptor'] == Descriptor(0, 4, 25):
                duree_period += int(dv['value']) * 60
            elif dv['descriptor'] == Descriptor(0, 4, 26):
                duree_period += int(dv['value'])
        return duree_period

    def readEffectivePeriodOfAccumulation(data_bufr):
        u"""Periode de cumul effective.

        Lis la période effective de cumul en seconde.
        La valeur est négative car elle s'applique à la période précédent
        la date on la met en positif
        return la valeur de la période de cumul en secondes
        """
        accumulationPeriod = None
        minutes = data_bufr.getValueByDescr(Descriptor(0, 4, 204))
        if minutes is not None:
            accumulationPeriod = -int(minutes) * 60
        return accumulationPeriod

    def readCaracTempoDate(descriptor_value):
        time_image = None
        try:
            for dv in descriptor_value:
                if dv['descriptor'] == '004001':
                    annee = int(dv['value'])
                    if annee < 1900 and annee >= 80:
                        annee += 1900
                    elif annee < 1900 and annee < 80:
                        annee += 2000
                elif dv['descriptor'] == '004002':
                    mois = int(dv['value'])
                elif dv['descriptor'] == '004003':
                    jour = int(dv['value'])
                elif dv['descriptor'] == '004004':
                    heure = int(dv['value'])
                elif dv['descriptor'] == '004005':
                    minute = int(dv['value'])
            date_image = '%04d:%02d:%02d %02d:%02d:%02d' % (
                annee, mois, jour, heure, minute, 0)
            time_image = datetime.strptime(date_image, "%Y:%m:%d %H:%M:%S")
        except KeyError:
            time_image = None

        return time_image

    def getValueOfDescriptor(descriptor_value, descriptor):
        for desc, value in descriptor_value.items():
            if desc == descriptor:
                return value
        return None

    dat_analysis = dat
    dat_cumul_analyse = None
    return_temporal_characteristics = {}
    return_temporal_characteristics['dat_analysis'] = dat_analysis

    for caracTempo in TEMPORAL_CHARACTERISTIC_DESCRIPTORS:
        temporal_characteristics_list = data_bufr.getAllByGroupDescr(
            caracTempo)
        for temporal_characteristics in temporal_characteristics_list:
            if temporal_characteristics is not None:
                descriptor_value = [{'descriptor': descriptor, 'value': value}
                                    for descriptor, value in
                                    temporal_characteristics.items()]
                duree_period = 0
                carac_period = getValueOfDescriptor(temporal_characteristics,
                                                    Descriptor(0, 8, 21))

                if carac_period in [3, 7]:  # il s'agit de données cumul

                    duree_period = readPeriod(descriptor_value)
                    return_temporal_characteristics['accumulation_period'] =\
                        duree_period
                    effective_accumulation_period =\
                        readEffectivePeriodOfAccumulation(data_bufr)
                    if effective_accumulation_period is not None:
                        return_temporal_characteristics[
                            'effective_accumulation_period'] =\
                            effective_accumulation_period
                elif carac_period in [4]:  # Echeance de Prevision
                    duree_period = readPeriod(descriptor_value)

                    echeance = duree_period
                    log.debug('echeance:%s' % echeance)
                    if echeance is None:
                        echeance = 0
                    if dat_cumul_analyse:
                        dat = dat_cumul_analyse + timedelta(seconds=echeance)
                        dat_analysis = dat_cumul_analyse
                    else:
                        dat = dat_analysis + timedelta(seconds=echeance)
                    log.debug('dat_analysis:%s' % dat_analysis)
                elif carac_period in [16]:  # Cumul analysé
                    dat_cumul_analyse = readCaracTempoDate(caracTempo)
                    log.debug('dat_cumul_analysis:%s' % dat_cumul_analyse)
    return_temporal_characteristics['date'] = dat
    log.debug('*************** %s' % str(return_temporal_characteristics))
    return return_temporal_characteristics


LATITUDE_DESCRIPTORS = [Descriptor(0, 5, 1),
                        Descriptor(0, 5, 2)]


LONGITUDE_DESCRIPTORS = [Descriptor(0, 6, 1),
                         Descriptor(0, 6, 2)]


TYPE_RADAR_RULE = {
    'descriptor': Descriptor(0, 2, 205),
    'rule': '"NON DISPONIBLE" if value is None \
    else "THOMSON-RODIN" if value==0 \
    else "OMERA-MELODI" if value==1 \
    else "PLESSEY 46C" if value==2 \
    else "OMERA-RAVEL" if value==3 \
    else "GEMATRONIK METEOR300AC" if value==4 \
    else "THOMSON-MTO2000" if value==5  else \
    "METEOR 510C" if value==6 \
    else "INCONNU (code:%d)" % value'}


TYPE_CALCULATOR_RULE = {
    'descriptor': Descriptor(0, 2, 193),
    'rule': '"NON DISPONIBLE" if value is None \
    else "Thomson MT750" if value==0 \
    else "Meteo-France SAPHYR" if value==1 \
    else "Meteo-France CASTOR" if value==2 \
    else "Meteo-France CASTOR2" if value==3  \
    else "INCONNU (code:%d)" % value'}


TYPE_ANTENNA_RULE = {
    'descriptor': Descriptor(0, 2, 101),
    'rule': '"NON DISPONIBLE" if value is None \
    else "Paraboloide a alimentation frontale centre" if value==0 \
    else "Paraboloide a alimentation frontale excentre" if value==1 \
    else "Paraboloide Cassegrain centre" if value==2 \
    else "Paraboloide Cassegrain excentre" if value==3 \
    else "Reseau d’elements plan" if value==4  \
    else "Reseau coaxial-collineaire" if value==5  \
    else "Reseau d elements Yagi" if value==6 \
    else "Microligne a ruban" if value==7  \
    else  "Autre" if value==14 \
    else "INCONNU (code:%d)" % value'}


PRESENCE_RADOME_RULE = {
    'descriptor': Descriptor(0, 2, 103),
    'rule': '"NON DISPONIBLE" if value is None  \
    else "Antenne radar est protegee par un radome" if value==1  \
    else "INCONNU (code:%d)" % value'}

POLARIZATION_ANTENNA_RULE = {
    'descriptor': Descriptor(0, 2, 104),
    'rule': '"NON DISPONIBLE" if value is None \
    else "Polarisation horizontale" if value==0 \
    else "Polarisation verticale" if value==1 \
    else "Polarisation circulaire droite" if value==2 \
    else "Polarisation circulaire gauche" if value==3 \
    else "Polarisation horizontale et verticale" if value==4 \
    else "Polarisation circulaire droite et gauche" if value==5 \
    else  "Polarisation quasi horizontale" if value==6 \
    else "Polarisation quasi verticale" if value==7 \
    else  "Autre" if value==14 \
    else "INCONNU (code:%d)" % value'}

MULTI_ELEVATION_DESCRIPTORS = (Descriptor(0, 2, 135),
                               Descriptor(0, 6, 194),
                               Descriptor(0, 6, 195),)
LOCALISATION_RADAR_DESCRIPTORS_RULE_1 = (Descriptor(0, 5, 1),
                                         Descriptor(0, 6, 1))
LOCALISATION_RADAR_DESCRIPTORS_RULE_2 = (Descriptor(0, 5, 2),
                                         Descriptor(0, 6, 2))


def getLocalisationRadar(data_bufr):
    u"""Localisation radar.

    Stratégie
        005001 et 006001 seul c'est la position du radar
        005001 et 006001 à 5 reprises c'est le 5 emequi represente le radar
        005002 et 006002 c'est la position du radar
    """
    localisations = data_bufr.getAllByGroupDescr(
        LOCALISATION_RADAR_DESCRIPTORS_RULE_1)
    if len(localisations) == 1:
        localisation = localisations[0]
        return {'latitude': localisation[Descriptor(0, 5, 1)],
                'longitude': localisation[Descriptor(0, 6, 1)]}
    if len(localisations) == 5:
        localisation = localisations[4]
        return {'latitude': localisation[Descriptor(0, 5, 1)],
                'longitude': localisation[Descriptor(0, 6, 1)]}
    localisations = data_bufr.getAllByGroupDescr(
        LOCALISATION_RADAR_DESCRIPTORS_RULE_2)
    if len(localisations) == 1:
        localisation = localisations[0]
        return {'latitude': localisation[Descriptor(0, 5, 2)],
                'longitude': localisation[Descriptor(0, 6, 2)]}


def getMultiElevations(data_bufr):
    elevations = []
    list_elevations = data_bufr.getAllByGroupDescr(MULTI_ELEVATION_DESCRIPTORS)
    for elevation in list_elevations:
        elevations.append({'elevation': elevation[Descriptor(0, 2, 135)],
                           'borneinf': elevation[Descriptor(0, 6, 194)],
                           'bornesup': elevation[Descriptor(0, 6, 195)]})
    return elevations


MULTI_ELEVATION_DESCRIPTORS_3D_2 = (Descriptor(0, 7, 2),
                                    Descriptor(0, 31, 192),
                                    Descriptor(0, 31, 192),)

MULTI_ELEVATION_DESCRIPTORS_3D_1 = (Descriptor(0, 7, 2),
                                    Descriptor(0, 31, 192))


def getListElevation(data_bufr):
    """Lecture de la liste des elevation dans une image 3d.

    """
    elevations = []
    list_elevations = data_bufr.getAllByGroupDescr(
        MULTI_ELEVATION_DESCRIPTORS_3D_2)
    pixmap_per_elevation = 2
    if len(list_elevations) == 0:
        list_elevations = data_bufr.getAllByGroupDescr(
            MULTI_ELEVATION_DESCRIPTORS_3D_1)
        pixmap_per_elevation = 1

    for elevation in list_elevations:
        elevations.append(int(elevation[Descriptor(0, 7, 2)]))
    return elevations, pixmap_per_elevation


ELEMENTARY_LOCAL_RADAR_DESCRIPTORS_1 = (Descriptor(0, 1, 1),
                                        Descriptor(0, 1, 2),
                                        Descriptor(0, 4, 1),
                                        Descriptor(0, 4, 2),
                                        Descriptor(0, 4, 3),
                                        Descriptor(0, 4, 4),
                                        Descriptor(0, 4, 5),
                                        Descriptor(0, 4, 6),
                                        Descriptor(0, 5, 1),
                                        Descriptor(0, 6, 1),
                                        Descriptor(0, 6, 196),
                                        Descriptor(0, 25, 210))

ELEMENTARY_LOCAL_RADAR_DESCRIPTORS_2 = (Descriptor(0, 1, 1),
                                        Descriptor(0, 1, 2),
                                        Descriptor(0, 4, 1),
                                        Descriptor(0, 4, 2),
                                        Descriptor(0, 4, 3),
                                        Descriptor(0, 4, 4),
                                        Descriptor(0, 4, 5),
                                        Descriptor(0, 4, 6),
                                        Descriptor(0, 5, 1),
                                        Descriptor(0, 6, 1))


def getElementaryLocalRadar(data_bufr):
    list_local_radar = []
    list_elementary_local_radar = data_bufr.getAllByGroupDescr(
        ELEMENTARY_LOCAL_RADAR_DESCRIPTORS_1)
    if len(list_elementary_local_radar) == 0:
        list_elementary_local_radar = data_bufr.getAllByGroupDescr(
            ELEMENTARY_LOCAL_RADAR_DESCRIPTORS_2)
    for elementary_radar in list_elementary_local_radar:
        try:
            indicatifOMM = int(elementary_radar[Descriptor(0, 1, 1)] * 1000) +\
                int(elementary_radar[Descriptor(0, 1, 2)])
        except KeyError:
            indicatifOMM = None
            continue
        try:
            (year, month, day, hour, minute, second) = (
                int(elementary_radar[Descriptor(0, 4, 1)]),
                int(elementary_radar[Descriptor(0, 4, 2)]),
                int(elementary_radar[Descriptor(0, 4, 3)]),
                int(elementary_radar[Descriptor(0, 4, 4)]),
                int(elementary_radar[Descriptor(0, 4, 5)]),
                int(elementary_radar[Descriptor(0, 4, 6)]))
            dat = '%04d-%02d-%02dT%02d:%02d:%02dZ' % (
                year, month, day, hour, minute, second)
        except KeyError:
            dat = None
        try:
            (lat, lon) = (elementary_radar[Descriptor(0, 5, 1)],
                          elementary_radar[Descriptor(0, 6, 1)])
        except KeyError:
            (lat, lon) = (None, None)
        if None not in [indicatifOMM, dat, lat, lon]:
            local_radar = {}
            local_radar['indicatifomm'] = str(indicatifOMM)
            local_radar['dat'] = dat
            local_radar['latitude'] = str(lat)
            local_radar['longitude'] = str(lon)
            try:
                local_radar['distance_oblique'] = elementary_radar[
                    Descriptor(0, 6, 196)]
            except KeyError:
                pass
            try:
                local_radar['facteur_correction'] = elementary_radar[
                    Descriptor(0, 25, 210)]
            except KeyError:
                pass

            list_local_radar.append(local_radar)
    return list_local_radar


def getConversionTable(data_bufr):

    def getListElementaryLevelDescriptor1(data_bufr):
        """ Descripteur 3 21 193.

        """
        ELEMENTARY_LEVEL_DESCRIPTORS = (Descriptor(0, 30, 1),
                                        Descriptor(0, 21, 216),
                                        Descriptor(0, 21, 216))
        group = ELEMENTARY_LEVEL_DESCRIPTORS
        datas = []
        descrs = [data_elem['descriptor'] for data_elem in data_bufr.data]
        if not type(group) is list:
            group = list(group)
        for i in range(len(descrs) - len(group)):
            if descrs[i:i + len(group)] == group:
                min = data_bufr.data[i + 1]['value']
                max = data_bufr.data[i + 2]['value']
                moy = int(mtomath.RtoZ((mtomath.ZtoR(min)
                          + mtomath.ZtoR(max)) / 2))  # noqa: W503

                datas.append({'id_level': int(data_bufr.data[i]['value']),
                              'min': min,
                              'max': max,
                              'moy': moy})  # -1 car nveau max exclu
        return datas

    def getListElementaryLevelDescriptor2(data_bufr):
        """Descripteur 3 21 193.

        """
        ELEMENTARY_LEVEL_DESCRIPTORS = (Descriptor(0, 21, 36),
                                        Descriptor(0, 31, 1),
                                        Descriptor(0, 21, 36))
        group = ELEMENTARY_LEVEL_DESCRIPTORS
        datas = []
        descrs = [data_elem['descriptor'] for data_elem in data_bufr.data]
        if not type(group) is list:
            group = list(group)
        min_r = None
        max_r = None
        for i in range(len(descrs) - len(group)):
            if descrs[i:i + len(group)] == group:
                min_r = data_bufr.data[i]['value']
                min = int(round(mtomath.RtoZ(min_r)))
                min = 0 if min < 0 else min
                max_r = data_bufr.data[i + 2]['value']
                max = int(round(mtomath.RtoZ(max_r)))
                max = 0 if max < 0 else max
                moy = int(round(mtomath.RtoZ((min_r + max_r) / 2)))
                moy = 0 if moy < 0 else moy
                try:
                    nbr_elements = int(data_bufr.data[i + 1]['value'])
                except KeyError:
                    nbr_elements = None
                datas.append({'id_level': 0,
                              'min': min,
                              'max': max,
                              'moy': moy})
                break
        if min_r is not None and max_r is not None:
            # Pour tenir compte du cas ou le nombre d'éléments dans la palette
            # n'est pas correctement positionne
            if nbr_elements is None:
                nbr_elements = 0
                j = i + 2
                while data_bufr.data[j]['descriptor'] == Descriptor(0, 21, 36):
                    j = j + 1
                    nbr_elements += 1

            for j in range(i + 2, i + nbr_elements + 1):
                min_r = data_bufr.data[j]['value']
                min = int(round(mtomath.RtoZ(min_r)))
                min = 0 if min < 0 else min
                max_r = data_bufr.data[j + 1]['value']
                max = int(round(mtomath.RtoZ(max_r)))
                max = 0 if max < 0 else max
                moy = int(round(mtomath.RtoZ((min_r + max_r) / 2)))
                moy = 0 if moy < 0 else moy
                datas.append({'id_level': j - i - 1,
                              'min': min,
                              'max': max,
                              'moy': moy})
        return datas

    def getListElementaryLevelDescriptor3(data_bufr):
        """Sequence 3 13 009 Descripteur 021001 031001 021001.

        """
        log.debug("getListElementaryLevelDescriptor3")
        ELEMENTARY_LEVEL_DESCRIPTORS = (Descriptor(0, 21, 1),
                                        Descriptor(0, 31, 1),
                                        Descriptor(0, 21, 1))
        group = ELEMENTARY_LEVEL_DESCRIPTORS
        datas = []
        descrs = [data_elem['descriptor'] for data_elem in data_bufr.data]
        if not type(group) is list:
            group = list(group)
        min_r = None
        max_r = None
        for i in range(len(descrs) - len(group)):
            if descrs[i:i + len(group)] == group:

                if data_bufr.data[i]['value'] is None:
                    # Pour traiter cas particulier composite allemenade
                    # ou la valeur manquante est null (on ne pourras pas
                    # distiguer les valeurs manquantes
                    min_z = 0
                else:
                    min_z = int(round(data_bufr.data[i]['value']))

                min_r = mtomath.ZtoR(min_z)
                max_z = int(round(data_bufr.data[i + 2]['value']))
                max_r = mtomath.ZtoR(max_z)
                moy_z = int(round(mtomath.RtoZ((min_r + max_r) / 2)))
                nbr_elements = int(data_bufr.data[i + 1]['value'])
                # TODO provisoirement tout ce qui est inferieur à 0 = 0
                datas.append({'id_level': 0,
                              'min': 0 if min_z < 0 else min_z,
                              'max': 0 if max_z < 0 else max_z,
                              'moy': 0 if moy_z < 0 else moy_z})
                break
        if min_r is not None and max_r is not None:
            for j in range(i + 2, i + nbr_elements):
                try:
                    min_z = int(round(data_bufr.data[j]['value']))
                    min_r = mtomath.ZtoR(min_z)
                    max_z = int(round(data_bufr.data[j + 1]['value']))
                    max_r = mtomath.ZtoR(max_z)
                    moy_z = int(round(mtomath.RtoZ((min_r + max_r) / 2)))
                    # TODO provisoirement tout ce qui est inferieur à 0 = 0
                    datas.append({'id_level': j - i - 1,
                                  'min': 0 if min_z < 0 else min_z,
                                  'max': 0 if max_z < 0 else max_z,
                                  'moy': 0 if moy_z < 0 else moy_z})
                except KeyError:
                    pass
        return datas

    def getListElementaryLevelDescriptor4(data_bufr):
        u"""Palette.

        Sequence 4 En fait on n'a pas de table de codage mais des valeurs qui
        sont codé à partir d'un offset et d'un icrément on reconstitue une
        pseudo table de conversion
        """
        log.debug("getListElementaryLevelDescriptor4")
        ELEMENTARY_LEVEL_DESCRIPTORS = (Descriptor(0, 21, 198),
                                        Descriptor(0, 21, 199))
        offset_increment = data_bufr.getValueByGroupDescr(
            ELEMENTARY_LEVEL_DESCRIPTORS)
        datas = []
        if offset_increment is not None:
            offset, increment = offset_increment
            for i in range(255):
                if offset + (increment * i) < 0:
                    val = 0  # On ne traite pas les valeurs négatives
                else:
                    val = offset + (increment * i)
                datas.append({'id_level': i,
                              'min': val,
                              'max': val,
                              'moy': val})
            # On traite a part la valeur manquante
            datas.append({'id_level': 255,
                          'min': 255,
                          'max': 255,
                          'moy': 255})

        return datas

    def getListElementaryLevelDescriptor5(data_bufr):
        """Descripteur 031001 021219."""
        ELEMENTARY_LEVEL_DESCRIPTORS = (Descriptor(0, 31, 1),
                                        Descriptor(0, 21, 219))
        group = ELEMENTARY_LEVEL_DESCRIPTORS
        datas = []
        descrs = [data_elem['descriptor'] for data_elem in data_bufr.data]
        if not type(group) is list:
            group = list(group)
        min_r = None
        max_r = None
        for i in range(len(descrs) - len(group)):
            if descrs[i:i + len(group)] == group:
                min_z = data_bufr.data[i + 1]['value']
                min_r = mtomath.ZtoR(min_z)
                max_z = data_bufr.data[i + 2]['value']
                max_r = mtomath.ZtoR(max_z)
                moy_z = int(round(mtomath.RtoZ((min_r + max_r) / 2.)))
                nbr_elements = int(data_bufr.data[i]['value'])
                datas.append({'id_level': 0,
                              'min': 0 if min_z < 0 else min_z,
                              'max': 0 if max_z < 0 else max_z,
                              'moy': 0 if moy_z < 0 else moy_z})
#                   datas.append({'id_level':0,
#                          'min':min_z,
#                              'max':max_z,
#                              'moy':moy_z })
                break
        if min_r is not None and max_r is not None:
            for j in range(i + 1, i + nbr_elements):
                min_z = int(data_bufr.data[j]['value'])
                min_r = mtomath.ZtoR(min_z)
                max_z = int(data_bufr.data[j + 1]['value'])
                max_r = mtomath.ZtoR(max_z)
                moy_z = int(round(mtomath.RtoZ((min_r + max_r) / 2.)))
                datas.append({'id_level': j - i - 1,
                              'min': 0 if min_z < 0 else min_z,
                              'max': 0 if max_z < 0 else max_z,
                              'moy': 0 if moy_z < 0 else moy_z})
#                datas.append({'id_level':j-i-1,
#                              'min':min_z,
#                              'max':max_z,
#                              'moy':moy_z })
        return datas

    def getListElementaryLevelDescriptor6(data_bufr):
        u"""Descripteur 031001 021001.

        """
        ELEMENTARY_LEVEL_DESCRIPTORS = (Descriptor(0, 31, 1),
                                        Descriptor(0, 21, 1))
        group = ELEMENTARY_LEVEL_DESCRIPTORS
        datas = []
        descrs = [data_elem['descriptor'] for data_elem in data_bufr.data]
        if not type(group) is list:
            group = list(group)
        min_r = None
        max_r = None
        for i in range(len(descrs) - len(group)):
            if descrs[i:i + len(group)] == group:
                min_z = data_bufr.data[i + 1]['value']
                min_r = mtomath.ZtoR(min_z)
                max_z = data_bufr.data[i + 2]['value']
                max_r = mtomath.ZtoR(max_z)
                moy_z = int(round(mtomath.RtoZ((min_r + max_r) / 2.)))
                nbr_elements = int(data_bufr.data[i]['value'])
                datas.append({'id_level': 0,
                              'min': 0 if min_z < 0 else min_z,
                              'max': 0 if max_z < 0 else max_z,
                              'moy': 0 if moy_z < 0 else moy_z})
#                   datas.append({'id_level':0,
#                          'min':min_z,
#                              'max':max_z,
#                              'moy':moy_z })
                break
        if min_r is not None and max_r is not None:
            for j in range(i + 1, i + nbr_elements):
                min_z = int(data_bufr.data[j]['value'])
                min_r = mtomath.ZtoR(min_z)
                max_z = int(data_bufr.data[j + 1]['value'])
                max_r = mtomath.ZtoR(max_z)
                moy_z = int(round(mtomath.RtoZ((min_r + max_r) / 2.)))
                datas.append({'id_level': j - i - 1,
                              'min': 0 if min_z < 0 else min_z,
                              'max': 0 if max_z < 0 else max_z,
                              'moy': 0 if moy_z < 0 else moy_z})
#                datas.append({'id_level':j-i-1,
#                              'min':min_z,
#                              'max':max_z,
#                              'moy':moy_z })
        return datas

    list_level = getListElementaryLevelDescriptor1(data_bufr)
    if len(list_level) == 0:
        list_level = getListElementaryLevelDescriptor2(data_bufr)
    if len(list_level) == 0:
        list_level = getListElementaryLevelDescriptor3(data_bufr)
    if len(list_level) == 0:
        list_level = getListElementaryLevelDescriptor4(data_bufr)
    if len(list_level) == 0:
        list_level = getListElementaryLevelDescriptor5(data_bufr)
    if len(list_level) == 0:
        list_level = getListElementaryLevelDescriptor6(data_bufr)

    log.debug("Liste de niveaux ()%d:%s" % (len(list_level), list_level))
    return list_level


def getCharacteristicsImages(data_bufr):
    u"""Caractéristiques images.

    On récupère les caractéristiques complémentaires servant à identifier
    l'image
    """
    return data_bufr.getAllByGroupDescr([Descriptor(0, 8, 210)])
