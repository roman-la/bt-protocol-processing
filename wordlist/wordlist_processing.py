import spacy
import glob
from xml.etree import ElementTree

nlp = spacy.load('de_core_news_sm')


def process_morphcomp():
    words = {}

    for file in glob.glob('morphcomp/*.txt'):
        with open(file, 'r', encoding='utf-8') as f:
            for line in f.read().splitlines():

                # TODO: Maybe look into later
                if '_' not in line or '-' in line:
                    continue

                # Process word
                word_raw = line.split('_')[0]
                word = __process_word(word_raw)

                # Process polarity
                polarity_string = line[-3:]
                if polarity_string == 'NEG':
                    polarity = -0.5
                elif polarity_string == 'POS':
                    polarity = 0.5
                else:
                    polarity = 0

                # Add word and polarity to dict
                if word in words:
                    words[word].append(polarity)
                else:
                    words[word] = [polarity]

    with open('morphcomp/OPdict.xml', 'r', encoding='utf-8') as f:
        xml_root = ElementTree.fromstring(f.read())
        for entry in xml_root.findall('entry'):
            word_raw = entry.find('term').text

            # TODO: Maybe look into later
            if not word_raw or len(word_raw) < 2 or word_raw in ['zu”'] or any(char.isdigit() for char in word_raw):
                continue

            # Process word
            word = __process_word(word_raw)

            # Process polarity
            polarity = []
            for opinion in entry.findall('opinion'):
                polarity.append(float(opinion.get('polarity')))
            polarity = sum(polarity) / len(polarity)

            # Add word and polarity to dict
            if word in words:
                words[word].append(polarity)
            else:
                words[word] = [polarity]

    # Write result to file
    with open('data/combined_sentiments.txt', 'w', encoding='utf-8') as f:
        for word, polarity in words.items():
            mean_polarity = sum(polarity) / len(polarity)
            mean_polarity = round(mean_polarity, 4)
            f.write(f'{word} {mean_polarity}\n')


def process_bundestag_sentiments():
    words = {}
    with open('data/bundestag_sentiments.txt', 'r', encoding='utf-8') as f:
        for line in f.read().splitlines():
            word_raw, polarity = line.split(' ')

            # Process word and polarity
            word = __process_word(word_raw)
            polarity = float(polarity)

            # Add word and polarity to dict
            if word in words:
                words[word].append(polarity)
            else:
                words[word] = [polarity]

    # Write result to file
    with open('data/bundestag_sentiments.txt', 'w', encoding='utf-8') as f:
        for word, polarity in words.items():
            mean_polarity = sum(polarity) / len(polarity)
            mean_polarity = round(mean_polarity, 4)
            f.write(f'{word} {mean_polarity}\n')


def __process_word(word_raw):
    word = nlp(word_raw)[0].lemma_
    word = word.lower()
    word = word.replace('ä', 'ae')
    word = word.replace('ö', 'oe')
    word = word.replace('ü', 'ue')
    word = word.replace('ß', 'ss')
    word = word.strip()
    return word
