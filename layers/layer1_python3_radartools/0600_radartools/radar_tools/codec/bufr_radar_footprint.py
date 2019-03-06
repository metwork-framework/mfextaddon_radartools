import logging


log = logging.getLogger()


class BufrRadarFootPrint:
    u"""Classe manipulant les empreintes des fichiers passe en parametre."""

    def read_section1_edition2(self, bytes_bufr):
        u"""Lecture section1 Edition2.

        Lecture de la section 1 d'un fichier bufr en edition 2
        @param bytes_bufr les premiers octets du fichier (100)
        @return tupple contenant l'edition du bufr, la version de la table omm,
        le centre de production, la version de la table locale le type de
        donnee et le sous type de donnees
        """
        version_table_omm = int(bytes_bufr[18])
        centre_production = int(bytes_bufr[13])
        version_table_locale = int(bytes_bufr[19])
        type_donnees = int(bytes_bufr[16])
        sous_type_donnees = int(bytes_bufr[17])
        return (2,
                version_table_omm,
                centre_production,
                version_table_locale,
                type_donnees,
                sous_type_donnees)

    def read_section1_edition3(self, bytes_bufr):
        u"""Lecture section 1 edition 3.

        Lecture de la section 1 d'un fichier bufr en edition 3
        @param bytes_bufr les premiers octets du fichier (100)
        @return tupple contenant l'edition du bufr, la version de la table omm,
        le centre de production, la version de la table locale le type de
        donnee et le sous type de donnees
        """
        version_table_omm = int(bytes_bufr[18])
        centre_production = int(bytes_bufr[13])
        version_table_locale = int(bytes_bufr[19])
        type_donnees = int(bytes_bufr[16])
        sous_type_donnees = int(bytes_bufr[17])
        return (3,
                version_table_omm,
                centre_production,
                version_table_locale,
                type_donnees,
                sous_type_donnees)

    def read_section1_edition4(self, bytes_bufr):
        u"""Lecture section 1 edition4.

        Lecture de la section 1 d'un fichier bufr en edition 3
        @param bytes_bufr les premiers octets du fichier (100)
        @return tupple contenant l'edition du bufr, la version de la table omm,
        le centre de production, la version de la table locale le type de
        donnee et le sous type de donnees
        """
        version_table_omm = int(bytes_bufr[21])
        centre_production = int(bytes_bufr[12]) * 256 + int(bytes_bufr[13])
        version_table_locale = int(bytes_bufr[22])
        type_donnees = int(bytes_bufr[18])
        sous_type_donnees = int(bytes_bufr[20])
        return (4,
                version_table_omm,
                centre_production,
                version_table_locale,
                type_donnees,
                sous_type_donnees)

    def footprint(self, path_file):
        u"""Empreinte.

        Fabrique et retourne l'empreinte bufr du fichier passe en parametre.
        @param path_file chemin du fichier a traiter
        @return empreinte dudit fichier
        """
        with open(path_file, 'rb') as f:
            bytes_bufr = bytearray(f.read(100))
        if bytes_bufr[0:4] != b'BUFR':
            return None
        edition_bufr = int(bytes_bufr[7])
        if edition_bufr == 2:
            return self.read_section1_edition2(bytes_bufr)
        if edition_bufr == 3:
            return self.read_section1_edition3(bytes_bufr)
        elif edition_bufr == 4:
            return self.read_section1_edition4(bytes_bufr)
