import xml.etree.ElementTree as ElementTree

faction_name_mapping = {'Fraktion der Christlich Demokratischen Union/Christlich - Sozialen Union': 'CDU/CSU',
                        'Fraktion der Sozialdemokratischen Partei Deutschlands': 'SPD',
                        'Alternative für Deutschland': 'AFD',
                        'Fraktion Bündnis 90/Die Grünen': 'BÜNDNIS 90/DIE GRÜNEN',
                        'Fraktion DIE LINKE.': 'DIE LINKE.',
                        'Fraktionslos': 'Fraktionslos',
                        'Fraktion der Freien Demokratischen Partei': 'FDP'}


class MdbProcessing:
    def __init__(self):
        self.xml = self.__download_xml()
        self.mdbs = self.__process_xml()
        self.titles = self.__get_titles()

        # Important for filtering out titles. E.g. 'Dr. h. c.' will leave 'h. c.' if 'Dr.' appears first in list
        self.titles.sort(reverse=True)

    def get_mdb_by_name(self, name):
        for title in self.titles:
            name = name.replace(title, '').strip()

        for mdb in self.mdbs:
            mdb_id, mdb_aliases, mdb_periods = mdb
            for mdb_alias in mdb_aliases:
                if f'{mdb_alias[0]} {mdb_alias[1]}' == name:
                    return mdb

        print('Could not resolve name: ' + name)

    def get_mdb_by_id(self, id_):
        for mdb in self.mdbs:
            mdb_id, _, _ = mdb
            if mdb_id == id_:
                return mdb

        print('Could not resolve id: ' + id_)

    @staticmethod
    def __download_xml():
        with open('samples/MDB_STAMMDATEN.XML', 'r', encoding='utf-8') as f:
            return ''.join(f.read())

    def __process_xml(self):
        root = ElementTree.fromstring(self.xml)

        mdbs = []
        for mdb_xml in root.iter('MDB'):
            mdb_id = mdb_xml.find('ID').text

            mdb_aliases = []
            for name in mdb_xml.find('NAMEN').iter('NAME'):
                first_name = name.find('VORNAME').text
                last_name = name.find('NACHNAME').text
                if name.find('PRAEFIX').text:
                    last_name = name.find('PRAEFIX').text + ' ' + last_name
                if name.find('ADEL').text:
                    last_name = name.find('ADEL').text + ' ' + last_name
                mdb_aliases.append((first_name, last_name, name.find('HISTORIE_BIS').text))

            if not mdb_aliases:
                raise NotImplementedError(mdb_id)

            mdb_periods = []
            for period in mdb_xml.iter('WAHLPERIODE'):
                period_id = period.find('WP').text

                for faction in period.iter('INSTITUTION'):
                    if faction.find('INSART_LANG').text != 'Fraktion/Gruppe':
                        continue

                    faction_name = faction.find('INS_LANG').text
                    if faction_name in faction_name_mapping:
                        faction_name = faction_name_mapping[faction_name]

                    part_of_faction_from = faction.find('MDBINS_VON').text
                    part_of_faction_to = faction.find('MDBINS_BIS').text

                    if not part_of_faction_from:
                        continue

                    mdb_periods.append((period_id, faction_name, part_of_faction_from, part_of_faction_to))

            if not mdb_periods:
                continue

            mdbs.append((mdb_id, mdb_aliases, mdb_periods))

        return mdbs

    def __get_titles(self):
        root = ElementTree.fromstring(self.xml)
        titles = []

        for t in root.iter('ANREDE_TITEL'):
            if t.text:
                title = t.text.strip()
                if title not in titles:
                    titles.append(title)

        for t in root.iter('AKAD_TITEL'):
            if t.text:
                title = t.text.strip()
                if title not in titles:
                    titles.append(title)

        return titles
