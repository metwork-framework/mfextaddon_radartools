#!/usr/bin/env python3
from radar_tools.codec.bufr_radar_codec import BufrRadarCoDec
from radar_tools.codec.geotiff_radar_codec import GeotiffRadarCoDec
from argparse import ArgumentParser


parser = ArgumentParser(description=__doc__)
parser.add_argument(
    'bufrfile',
    metavar='bufrfile',
    type=str,
    help=u"BUFR files to process")
parser.add_argument(
    'geotifffile',
    metavar='geotifffile',
    type=str,
    help=u"Resulting GEOTIFF files")
group = parser.add_mutually_exclusive_group()
group.add_argument(
    '-dt', '--demeter_table',
    default=None,
    help=u"Location of storage of demeter tables ")
group.add_argument(
    '-di', '--demeter_image',
    default=None,
    help=u"Location of storage of demeter templates of image descriptors ")
group.add_argument(
    '-bn', '--band_number',
    default=None,
    help=u"Number of the band to put in geotiff (first=1). If None all the"
    " bands will be in the geotiff")


def bufrtogeotiff(bufrfile, geotifffile, demeter_data=None,
                  demeter_image=None, band_number=None):
    cr = BufrRadarCoDec.load_env_bufr(demeter_data, demeter_image)
    if not cr:
        print("Impossible de charger les tables bufr")
        return False
    codec_bufr = BufrRadarCoDec()
    data_radar = codec_bufr.decoding(bufrfile)
    if data_radar is None:
        print("Decodage bufr impossible")
    codec_geotiff = GeotiffRadarCoDec()
    cr = codec_geotiff.encoding(data_radar, geotifffile, band_number)
    if not cr:
        print("Codage geotiff impossible")
        return False
    return True


def main():
    args = parser.parse_args()
    bufrtogeotiff(args.bufrfile,
                  args.geotifffile,
                  args.demeter_table,
                  args.demeter_image,
                  args.band_number)
