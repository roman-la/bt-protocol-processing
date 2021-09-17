import spacy

nlp = spacy.load('de_core_news_sm')


def get_polarity_lexicon():
    polarities = {}
    with open('lexicon-data/polarity.csv', 'r', encoding='utf-8') as f:
        for line in f.read().splitlines():
            if line.startswith('%%'):
                continue
            word, polarity = line.split(',')
            polarities[word] = float(polarity)
    return polarities


def get_intensifier_lexicon():
    intensifiers = []
    with open('lexicon-data/intensifiers_raw.txt', 'r', encoding='utf-8') as f:
        for line in f.read().splitlines():
            if line.startswith('%%'):
                continue
            word = __lemmatization(line)
            intensifiers.append(word)
    return intensifiers


def get_negation_lexicon():
    negations = {}
    with open('lexicon-data/negations_raw.txt', 'r', encoding='utf-8') as f:
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
