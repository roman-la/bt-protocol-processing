import spacy
import glob
import os

nlp = spacy.load('de_core_news_sm')


class Lexicons:
    def __init__(self):
        self.polarity_lexicon = get_polarity_lexicon()
        self.intensifier_lexicon = get_intensifier_lexicon()
        self.negation_lexicon = get_negation_lexicon()

        # Remove intesifiers from polarity_lexicon
        # for word in self.intensifier_lexicon:
        # self.polarity_lexicon.pop(word, None)

        # Remove negations from polarity_lexicon
        # for word in self.negation_lexicon:
        # self.polarity_lexicon.pop(word, None)


def get_polarity_lexicon():
    words = {}
    for file in glob.glob(os.path.dirname(__file__) + '/data/*_sentiments.txt'):
        with open(file, 'r', encoding='utf-8') as f:
            for line in f.read().splitlines():
                word, polarity = line.split(' ')
                polarity = float(polarity)
                if word in words:
                    words[word].append(polarity)
                else:
                    words[word] = [polarity]

    for word, polarity in words.items():
        mean_polarity = sum(polarity) / len(polarity)
        mean_polarity = round(mean_polarity, 4)
        words[word] = mean_polarity
    return words


def get_intensifier_lexicon():
    intensifiers = []
    with open(os.path.dirname(__file__) + '/data/intensifiers_raw.txt', 'r', encoding='utf-8') as f:
        for line in f.read().splitlines():
            if line.startswith('%%'):
                continue
            word = __lemmatization(line)
            intensifiers.append(word)
    return intensifiers


def get_negation_lexicon():
    negations = {}
    with open(os.path.dirname(__file__) + '/data/negations_raw.txt', 'r', encoding='utf-8') as f:
        for line in f.read().splitlines():
            if line.startswith('%%'):
                continue
            word, _, scope, pos = line.split(' ')
            word = __lemmatization(word)
            scope = scope[1:-1].split(',')
            pos = pos.strip()
            negations[word] = [scope, pos]
    return negations


def __lemmatization(word):
    doc = nlp(word)
    return doc[0].lemma_.lower()
