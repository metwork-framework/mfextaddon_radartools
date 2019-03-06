# -*- coding: utf-8 -*-

import numpy as np
import logging

log = logging.getLogger()


class Data():
    """Classe de base."""

    pass


class DataBufr(Data):
    u"""Classe permettant de manipuler une donnee bufr avec des pixmaps."""

    images = []

    def __init__(self, bufrdatas):
        u"""Initialisation.

        @param data Données BUFR sous forme d'une liste de bufrdata
        """
        self.data = []
        self.sub_category = bufrdatas.data_sub_category
        for bufrdata in bufrdatas:
            if bufrdata.type != 'IMAGE':
                self.data.append({'type': bufrdata.type,
                                  'value': bufrdata.value,
                                  'descriptor': bufrdata.descriptor})
            else:
                image = np.fromfile(bufrdata.value[3], bufrdata.value[2])
                image.resize(bufrdata.value[0], bufrdata.value[1])
                self.data.append({'type': bufrdata.type,
                                  'value': image,
                                  'descriptor': bufrdata.descriptor})
        # Mise sous forme de dictionnaire pour accélérer l'accès aux données
        self.datadict = {}
        if bufrdatas:
            for data_elem in self.data:
                if data_elem['descriptor'] in self.datadict:
                    self.datadict[data_elem['descriptor']].append(data_elem)
                else:
                    self.datadict[data_elem['descriptor']] = [data_elem]

    def getByDescr(self, descr, index=0):
        u"""Retourne le i.eme item (descripteur,valeur).

        Retourne l'item (descripteur, valeur) associe au descripteur passe en
        argument
        @param descr descripteur bufr recherche
        @param index dans le cas ou le descripteur est multiple on peut
        preciser l'indice recherche
        @return (descripteur,valeur) recherchee
        """
        if descr not in self.datadict:
            return

        if len(self.datadict[descr]) > index:
            return self.datadict[descr][index]

    def getValueByDescr(self, descr, index=0):
        u"""Valeur associee au descripteur.

        Retourne la valeur associee au descripteur passe en argument
        @param descr descripteur bufr recherche
        @param index dans le cas ou le descripteur est multiple on peut
        preciser l'indice recherche
        @return valeur recherchee
        """
        dataitem = self.getByDescr(descr, index)
        if dataitem:
            return dataitem['value']

    def getByListDescr(self, liste):
        u"""Donnée associée à une liste de descripteur.

        Retourne la premiere data disponible associé à un descripteur parmi la
        liste de descripteur passée en paramètres
        @list liste de descripteur
        @return retourne la data si un descripteur correspond None sinon
        """
        for descriptor in liste:
            data = self.getByDescr(descriptor)
            if data is not None:
                return data

    def getValueByListDescr(self, liste):
        u"""Première valeur associe à une liste de descripteurs.

        Retourne la premiere valeur disponible associé à un descripteur parmi
        la liste de descripteur passée en paramètres
        @list liste de descripteur
        @return retourne la valeur associe à la data si un descripteur
        correspond None sinon
        """
        data_item = self.getByListDescr(liste)
        if data_item:
            return data_item['value']

    def getByGroupDescr(self, group, index=0):
        descrs = [data_elem['descriptor'] for data_elem in self.data]
        if not type(group) is list:
            group = list(group)
        indice = 0
        for i in range(len(descrs) - len(group)):
            if descrs[i:i + len(group)] == group:
                if indice == index:
                    data_group = self.data[i:i + len(group)]
                    return data_group
                else:
                    indice += 1

    def getAllByGroupDescr(self, group):
        u"""Lis toutes les valeurs associées à un groupe de descripteurs.

        Lis toutes les valeurs correspondant au groupe de descripteur passé en
        argument
        ATTENTION ! Ne pas avoir 2 fois le meme descripteur dans le groupe
        @param group groupe de descripteurs
        @return une liste contenant les réponses sous la forme d'un
        dictionnaire associant la clé du dictionnaire (descriptor bufr) à sa
        data
        """
        datas = []
        descrs = [data_elem['descriptor'] for data_elem in self.data]
        if not type(group) is list:
            group = list(group)
        for i in range(len(descrs) - len(group)):
            if descrs[i:i + len(group)] == group:
                datas.append({data_elem['descriptor']: data_elem['value']
                              for data_elem in self.data[i:i + len(group)]})
        return datas

    def getValueByGroupDescr(self, group, index=0):
        data_group = self.getByGroupDescr(group, index)
        if data_group:
            return [data_item['value'] for data_item in data_group]

    def getValueFromRule(self, rule):
        u"""Valeur associée à une règle.

        Retourne la valeur correspondant à la règle passé en parametre
        Une regle est un dictionaire contenant 2 clé
           * descriptor: designe le descripteur
           * rule : fonction à appliquer à la valeur du descripteur
        @param descriptor le descripteur recherché
        @param rule la règle à appliquer
        """
        data = self.getByDescr(rule['descriptor'])
        if data is not None:
            return eval(rule['rule'], {'value': data['value']})

    def getDataGroup(self, group, value):
        u"""Recherche la valeur associée au groupe de descripteurs.

        @param group Liste ordonnées de descripteurs consécutifs à l'intérieure
            de laquelle est cherché le descripteur 'descr'
        @param value Valeur associée au premier descripteur du groupe cherché

        """
        descrs = [descr for descr, _ in self.data]
        for i in range(len(descrs) - len(group)):
            if descrs[i:i + len(group)] == group:
                if self.data[i][1] != value:
                    continue
                data_group = self.data[i:i + len(group)]
                return data_group

    def getDataImages(self):
        u"""Retourne les images.

        @return retourne une liste de tupple associant un descripteur bufr et
        une matrice de données caractéristique de l'image
        """
        return [data_elem for data_elem in self.data
                if data_elem['type'] == 'IMAGE']
