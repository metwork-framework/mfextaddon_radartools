# -*- coding: utf-8 -*-
import numpy


def RtoZ(val_r, a=200, b=1.6):
    u"""Conversion R vers Z.

    Effectue la conversion de R exprimé en mm/h en dBZ pour les données Radar
    @param val_r  valeur de precipitation exprimée en mm/h
    @param a coefficient a de la relation de Marshall-Palmer (defaut a=200)
    @param b coefficient b de la relation de Marshall-Palmer (defaut b=1.6)
    @return Valeur Z de la mesure exprimé en dBZ
    """
    save_settings = numpy.seterr(divide='ignore')
    try:
        z = 10 * numpy.log10(a * (val_r)**b)
        if z.ndim > 0:
            z[z == -numpy.inf] = 0
        elif z == -numpy.inf:
            z = 0
        return z
    finally:
        numpy.seterr(**save_settings)


def ZtoR(val_z, a=200, b=1.6):
    u"""Coversion Z vers R.

    Effectue la conversion de Z exprimé en dBZ en mm/h pour les données Radar
    @param val_z  valeur de precipitation exprimée en dBZ
    @param a coefficient a de la relation de Marshall-Palmer (defaut a=200)
    @param b coefficient b de la relation de Marshall-Palmer (defaut b=1.6)
    @return Valeur Z de la mesure exprimé en mm/h
    """
    return ((10**(val_z / 10.)) / a) ** (1 / b)
