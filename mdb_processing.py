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

        # Important for filtering out titles. E.g. 'Dr. h. c.' will leave 'h. c.' if 'Dr.' appears first in list.
        self.titles.sort(reverse=True)

    def get_mdb_by_name(self, name):
        for title in self.titles:
            name = name.replace(title, '').strip()

        for mdb in self.mdbs:
            for n in mdb['names']:
                if n[0] + ' ' + n[1] == name:
                    return mdb

        print('Could not resolve name: ' + name)

    def get_mdb_by_id(self, id_):
        for mdb in self.mdbs:
            if mdb['id'] == id_:
                return mdb

        print('Could not resolve id: ' + id_)

    @staticmethod
    def __download_xml():
        with open('samples/MDB_STAMMDATEN.XML', 'r', encoding='utf-8') as f:
            return ''.join(f.read())

    def __process_xml(self):
        root = ElementTree.fromstring(self.xml)

        mdbs = []
        for mdb in root.iter('MDB'):
            mdb_id = mdb.find('ID').text

            names = []
            for name in mdb.find('NAMEN').iter('NAME'):
                first_name = name.find('VORNAME').text
                last_name = name.find('NACHNAME').text
                if name.find('PRAEFIX').text:
                    last_name = name.find('PRAEFIX').text + ' ' + last_name
                if name.find('ADEL').text:
                    last_name = name.find('ADEL').text + ' ' + last_name
                from_date = name.find('HISTORIE_VON').text
                to_date = name.find('HISTORIE_BIS').text
                names.append((first_name, last_name, from_date, to_date))

            for period in mdb.iter('WAHLPERIODE'):
                for faction in period.iter('INSTITUTION'):
                    faction_name = faction.find('INS_LANG').text
                    part_of_faction_from = faction.find('MDBINS_VON').text
                    part_of_faction_to = faction.find('MDBINS_BIS').text

                    if not part_of_faction_from:
                        part_of_faction_from = period.find('MDBWP_VON').text

                    if not part_of_faction_to:
                        part_of_faction_to = period.find('MDBWP_BIS').text

                    if faction_name in faction_name_mapping.keys():
                        faction_name = faction_name_mapping[faction_name]

                    mdbs.append({
                        'id': mdb_id,
                        'names': names,
                        'faction': faction_name,
                        'period': period.find('WP').text,
                        'from': part_of_faction_from,
                        'to': part_of_faction_to
                    })
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
