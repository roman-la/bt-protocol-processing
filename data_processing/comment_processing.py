import spacy
from spacy.tokens import Doc, Span, Token
from spacy.language import Language
from wordlist.lexicons import Lexicons

nlp = spacy.load('de_core_news_sm')

# Set custom spacy object properties
Doc.set_extension('polarity', default=0.0)
Token.set_extension('polarity', default=0.0)
Token.set_extension('relevant', default=True)
Token.set_extension('negated', default=False)
Token.set_extension('intensified', default=False)

# Load lexicons
lexicons = Lexicons()
polarity_lexicon = lexicons.polarity_lexicon
negation_lexicon = lexicons.negation_lexicon
intensifier_lexicon = lexicons.intensifier_lexicon


def get_comment_polarity(comment):
    return nlp(comment)._.polarity


@Language.component('normalization')
def __normalization(doc):
    for i, token in enumerate(doc):
        doc[i].lemma_ = doc[i].lemma_.lower()
        doc[i].lemma_ = doc[i].lemma_.replace('ä', 'ae')
        doc[i].lemma_ = doc[i].lemma_.replace('ö', 'oe')
        doc[i].lemma_ = doc[i].lemma_.replace('ü', 'ue')
        doc[i].lemma_ = doc[i].lemma_.replace('ß', 'ss')
    return doc


@Language.component('negation_detection')
def __negation_detection(doc):
    for sentence in doc.sents:
        for token in sentence:
            if token.lemma_ not in negation_lexicon.keys():
                continue

            # Negation particle
            if 'dependent' in negation_lexicon[token.lemma_][0]:
                token._.relevant = False
                token.head._.negated = True

            # Negation preposition
            elif 'objp-ohne' in negation_lexicon[token.lemma_][0]:
                if token.i + 1 < len(doc):
                    token._.relevant = False
                    doc[token.i + 1]._.negated = True

            # Negation adverbs and indefinite pronouns
            elif 'clause' in negation_lexicon[token.lemma_][0]:
                token._.relevant = False
                for t in sentence:
                    t._.negated = True

            # Negation nouns genitive modifier
            elif 'gmod' in negation_lexicon[token.lemma_][0]:
                if negation_lexicon[token.lemma_][1] == 'nomen':
                    for t in sentence:
                        if t.dep_ == 'ag':
                            token._.relevant = False
                            t._.negated = True

            # Negation verbs
            elif (dep.startsWith('obj') for dep in negation_lexicon[token.lemma_][0]):
                if negation_lexicon[token.lemma_][1] == 'verb':
                    for t in sentence:
                        if t.dep_ in ['oa', 'oa2', 'oc', 'og', 'op']:
                            token._.relevant = False
                            t._.negated = True
    return doc


@Language.component('intensifier_detection')
def __intensifier_detection(doc):
    for sentence in doc.sents:
        for token in sentence:
            if token.lemma_ in intensifier_lexicon:
                if token.head != token:
                    token.head._.intensified = True
                    token._.relevant = False
    return doc


@Language.component('polarity_calculation')
def __polarity_calculation(doc):
    # Calculate polarity value for each token
    for token in doc:
        if token.pos_ == 'PUNCT' or not token._.relevant:
            continue
        if token.lemma_ not in polarity_lexicon.keys():
            continue

        if token._.negated:
            token._.polarity = (-1.0) * polarity_lexicon[token.lemma_]
        if token._.intensified:
            token._.polarity = 1.5 * polarity_lexicon[token.lemma_]
        else:
            token._.polarity = polarity_lexicon[token.lemma_]

    # Sum polarities
    for token in doc:
        doc._.polarity += token._.polarity

    # Count doc length
    doc_length = sum([1 for token in doc if token.pos_ != 'PUNCT'])

    # Calculate doc polarity with min-max-scaling
    if doc_length > 0:
        if doc._.polarity > 0.0:
            doc._.polarity = (doc._.polarity + 1.0) / (doc_length + 1.0)
        elif doc._.polarity < 0.0:
            doc._.polarity = (doc._.polarity - 1.0) / (doc_length + 1.0)
    return doc


# Add custom pipeline components to default pipeline
nlp.add_pipe('normalization', last=True)
nlp.add_pipe('negation_detection', last=True)
nlp.add_pipe('intensifier_detection', last=True)
nlp.add_pipe('polarity_calculation', last=True)
