# -*- coding: utf-8 -*-
from radar_tools.codec.radar_codec import RadarCoDec
import radar_tools.codec.rule_bufr as RuleBufr
from radar_tools.codec.data_radar import DataRadar
from radar_tools.codec.data_bufr import DataBufr
from radar_tools.codec.bufr_radar_footprint import BufrRadarFootPrint
import json
import os
from demeter import BufrDataset, Descriptor, TableB
import logging

log = logging.getLogger()


class BufrRadarCoDec(RadarCoDec):
    """Cette classe represente une image radar bufr
    """

    @classmethod
    def load_env_bufr(cls, env_demeter_table=None, env_demeter_image=None):
        if env_demeter_table is None and 'DEMETER_TABLE'in os.environ:
            env_demeter_table = os.environ['DEMETER_TABLE']
        if os.path.exists(env_demeter_table):
            os.environ['NEPpGbTables'] = env_demeter_table
            cr = True
        else:
            print('ERREUR : Les données associées à DEMETER ne sont pas'
                  ' correctement installées\n')
            if 'DEMETER_TABLE' in os.environ:
                print('DEMETER_TABLE : %s\n' % os.environ['DEMETER_TABLE'])
            else:
                print('DEMETER_TABLE : ABSENT\n')
            if 'NEPpGbTables' in os.environ:
                print('NEPpGbTables : %s\n' % os.environ['NEPpGbTables'])
            else:
                print('NEPpGbTables : ABSENT\n')
            cr = False
        if env_demeter_image is None and 'DEMETER_IMAGE'in os.environ:
            env_demeter_image = os.environ['DEMETER_IMAGE']
        if os.path.exists(env_demeter_image):
            os.environ['DEMETER_IMAGE'] = env_demeter_image
            cr = True
        else:
            print('ERREUR : Les données associées à DEMETER ne sont pas'
                  ' correctement installées\n')
            if 'DEMETER_IMAGE' in os.environ:
                print('DEMETER_IMAGE : %s\n' % os.environ['DEMETER_IMAGE'])
            else:
                print('DEMETER_IMAGE : ABSENT\n')
            if 'NEPDescPixConf' in os.environ:
                print('NEPDescPixConf : %s\n' % os.environ['NEPDescPixConf'])
            else:
                print('NEPDescPixConf : ABSENT\n')
            cr = False
        return cr

    def to_dict_str(self, dico):
        u"""Dictionnaire clé, valeur.

        Fabrique un dictionnaire cle, valeur pour pouvoir traiter les
        dictionaires de dictionaires
        @param dico le dictionnaire a traiter
        @return le nouveau dictionnaire
        """
        new_dico = {}
        for key, value in dico.items():
            new_dico[key] = str(value)
        return new_dico

    def to_list_str(self, liste):
        """Liste de dictionnaire.

        Fabrique une liste de chaines a partir d'une liste de dictionnaires
        @param liste liste de dictionnaires
        @return liste de chaines
        """
        new_liste = []
        for element in liste:
            new_liste.append(self.to_dict_str(element))
        return new_liste

    def bufr_characteristics(self, dataset):
        u"""Caracterisitiques.

        Recupere les caracteristiques du bufr. C'est a dire les couples
        descripteur valeur mais en oubliant le descripteur
        @param dataset il s'agit de la donnee bufr décodé
        @return liste de dictionnaire permettant de connaitre le titre,
        le type de donnee et la valeur
        """
        bufr_characteristics = []

        for i, subset in dataset:
            self.table_b = TableB.fromOmm(subset.center,
                                          subset.master_table_version,
                                          subset.local_table_version)
            for data_bufr in subset:
                descriptor = data_bufr.descriptor
                descriptor_table = self.table_b[descriptor]
                bufr_characteristics.append({
                    'title': descriptor_table.title,
                    'data_type': descriptor_table.data_type,
                    'value': str(data_bufr.value)})
        return bufr_characteristics

    def select_nepdescpixconf(self, path_file):
        u"""Selectionne la variable d'environnement pour les pixmaps.

        Selectionne la variable d'environnement pour désigner le fichier de
        descripteur de pixmap.
        @param path_file path du fichier bufr
        @return un tuple associant l'empreinte du fichier et le template de
        pixmap. Si l'empreinte n'est pas reconnue le template sera null
        """
        bufr_footprint = BufrRadarFootPrint()
        footprint_file = bufr_footprint.footprint(path_file)
        descripteur_pixmap = None
        if footprint_file == (4, 16, 85, 14, 6, 3) or\
                footprint_file == (2, 11, 85, 14, 6, 20) or\
                footprint_file == (4, 16, 85, 14, 6, 30) or\
                footprint_file == (4, 16, 85, 16, 6, 22) or\
                footprint_file == (2, 11, 85, 14, 6, 22) or\
                footprint_file == (4, 16, 85, 14, 6, 27):
            descripteurs_pixmap = 'DESCRIPTEURS_PIXMAP_SERVAL.CONFIG'
        else:
            print("Empreinte inconnu : %s\n" % str(footprint_file))
            return
        os.environ['NEPDescPixConf'] = os.path.join(
            os.environ['DEMETER_IMAGE'], descripteurs_pixmap)
        return (footprint_file, descripteur_pixmap)

    def decoding(self, path_file):
        u"""Décodage du fichier.

        Decodage du fichier dont le nom est apssé en argument
        @param path_file fichier bufr a decoder
        @return Donnee radar decodee ou null si probleme
        """
        if self.select_nepdescpixconf(path_file) is None:
            return None
        dataset = BufrDataset.fromFile(path_file)
        data_radar = DataRadar()
        dataset = list(enumerate(dataset))
        for i, subset in dataset:
            self.table_b = TableB.fromOmm(subset.center,
                                          subset.master_table_version,
                                          subset.local_table_version)
            data_bufr = DataBufr(subset)
            date = RuleBufr.getDate(data_bufr)
            if date is None:
                log.info("Warn : Unknown date")
                return None
            data_radar.vue = RuleBufr.getVue(data_bufr)

            data_images = data_bufr.getDataImages()

            if RuleBufr.getUniqueProductIdentifier(data_bufr) is not None:
                data_radar.common_characteristics[
                    'unique_product_identifier'] =\
                    RuleBufr.getUniqueProductIdentifier(data_bufr)
            if RuleBufr.getPictureType(data_bufr) is not None:
                data_radar.common_characteristics['picture_type'] = str(
                    RuleBufr.getPictureType(data_bufr))
            if RuleBufr.getMosaicIndicator(data_bufr) is not None:
                data_radar.common_characteristics['mosaic_indicator'] = str(
                    RuleBufr.getMosaicIndicator(data_bufr))

            data_radar.common_characteristics.update(
                self.to_dict_str(
                    RuleBufr.getTemporalCharacteristics(data_bufr, date)))

            # Caracteristiques des radar
            if data_bufr.sub_category in range(0, 20):  # Radar local
                feature = self.getCharacteristicsLocalRadar(data_bufr)
                data_radar.common_characteristics['radar_characteristics'] =\
                    str(self.to_dict_str(feature)['feature'])
            else:  # Composite
                feature = RuleBufr.getElementaryLocalRadar(data_bufr)
                data_radar.common_characteristics['radars'] =\
                    str(self.to_list_str(feature))

            for data_image in data_images:
                descriptor_table = self.table_b[data_image['descriptor']]
                characteristics_image = {
                    'title': descriptor_table.title,
                    'data_type': descriptor_table.data_type}

                data_radar.pixmaps.append(data_image['value'])
                data_radar.pixmaps_characteristics.append(
                    self.to_dict_str(characteristics_image))

            # Dans le fourre tout on met l'ensemble des infos du bufr
            data_radar.catch_all = self.bufr_characteristics(dataset)

        return data_radar

    def getCharacteristicsLocalRadar(self, data_bufr):
        u"""Caractéristiques d'un radar local.

        Retourne les caracteristique du radars
        @data_bufr donnee bufr decodee
        @return dictionnaire
        """
        feature = {}
        feature['indicatifomm'] = RuleBufr.getIndicatifOMM(data_bufr)
        feature['latituderadar'] = \
            data_bufr.getValueByListDescr(RuleBufr.LATITUDE_DESCRIPTORS)
        feature['longituderadar'] = \
            data_bufr.getValueByListDescr(RuleBufr.LONGITUDE_DESCRIPTORS)
        feature['typeradar'] = \
            data_bufr.getValueFromRule(RuleBufr.TYPE_RADAR_RULE)
        feature['typecalculateur'] = \
            data_bufr.getValueFromRule(RuleBufr.TYPE_CALCULATOR_RULE)
        feature['typeantenne'] = \
            data_bufr.getValueFromRule(RuleBufr.TYPE_ANTENNA_RULE)
        feature['radome'] =\
            data_bufr.getValueFromRule(RuleBufr.PRESENCE_RADOME_RULE)
        feature['polarisationantenne'] = \
            data_bufr.getValueFromRule(RuleBufr.POLARIZATION_ANTENNA_RULE)
        feature['altitude'] = \
            data_bufr.getValueByDescr(Descriptor(0, 7, 2))
        feature['hauteurantenne'] = \
            data_bufr.getValueByDescr(Descriptor(0, 2, 102))
        feature['frequence'] = data_bufr.getValueByDescr(Descriptor(0, 2, 121))
        feature['multisite'] = RuleBufr.getMultiElevations(data_bufr)
        porteehydrologique = data_bufr.getValueByDescr(Descriptor(0, 6, 199))
        if porteehydrologique is not None:
            feature['porteehydrologique'] = porteehydrologique
        facteurcorrectif = data_bufr.getValueByDescr(Descriptor(0, 25, 210))
        if facteurcorrectif is not None:
            feature['facteurcorrectif'] = facteurcorrectif
        characteristic = {'feature': json.dumps(feature)}
        return characteristic
