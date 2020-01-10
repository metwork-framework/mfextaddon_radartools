#!/bin/env python
# -*- coding: utf-8 -*-
import gdal
import logging
from radar_tools.codec.radar_codec import RadarCoDec


log = logging.getLogger()


class GeotiffRadarCoDec(RadarCoDec):

    def encoding(self, data_radar, geotiff_name, band_num=None):

        data_type = gdal.GDT_Float64
        if band_num is None:
            count_band = len(data_radar.pixmaps)
        elif int(band_num) <= len(data_radar.pixmaps):
            count_band = 1
        else:
            return False

        # Recupération des éléments nécessaires depuis la vue
        vue = data_radar.vue
        pixels_per_row = int(vue.getDomaine().getNumberPixelX())
        pixels_per_column = int(vue.getDomaine().getNumberPixelY())
        point_north_west = vue.getPointNOXY()
        pixel_size_x, pixel_size_y = vue.getResolutions()
        log.debug("geotiff_name:%s, pixels_per_row:%d,"
                  "pixels_per_column:%d, data_type:%s" %
                  (geotiff_name, pixels_per_row, pixels_per_column, data_type))

        # Create gtif
        driver = gdal.GetDriverByName("GTiff")
        dst_ds = driver.Create(geotiff_name, pixels_per_row, pixels_per_column,
                               count_band, data_type,
                               ['COMPRESS=LZW'])

        # Definition du domaine de l'image
        dst_ds.SetGeoTransform([point_north_west.GetX(), pixel_size_x, 0,
                                point_north_west.GetY(), 0, pixel_size_y])

        dst_ds.SetDescription('Override the description')

        # On met les caracteristiques de la production
        dst_ds.SetMetadata(data_radar.common_characteristics)

        # Projection du dataset
        spatialReference = vue.getProjection().getSpatialReference()
        if spatialReference is None:
            log.warning('spatialReference KO')
            return False
        log.debug('Definition projection:%s' %
                  vue.getProjection().getSpatialReference().ExportToWkt())
        dst_ds.SetProjection(vue.getProjection().
                             getSpatialReference().ExportToWkt())

        num_band = 0
        num_band_write = 0
        for pixmap, pixmap_characteristics in zip(
                data_radar.pixmaps, data_radar.pixmaps_characteristics):
            num_band += 1
            # write the band
            if band_num is None or int(band_num) == num_band:
                num_band_write += 1
                band = dst_ds.GetRasterBand(num_band_write)
                band.WriteArray(pixmap)
                band.SetMetadata(pixmap_characteristics)

        return True
