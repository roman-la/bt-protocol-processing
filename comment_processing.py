import spacy
from spacy.tokens import Doc, Span, Token
from spacy.language import Language
import lexicons

Doc.set_extension('polarity', default=0.0)
Span.set_extension('polarity', default=0.0)
Token.set_extension('relevant', default=True)
Token.set_extension('negated', default=False)
Token.set_extension('intensified', default=False)

nlp = spacy.load('de_core_news_sm')

polarity_lexicon = lexicons.get_polarity_lexicon()
negation_lexicon = lexicons.get_negation_lexicon()
intensifier_lexicon = lexicons.get_intensifier_lexicon()


def get_comment_polarity(text):
    return nlp(text)._.polarity


@Language.component('normalization')
def __normalization(doc):
    for i, token in enumerate(doc):
        doc[i].lemma_ = doc[i].lemma_.lower()
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
                token.head._.intensified = True
                token._.relevant = False
    return doc


@Language.component('polarity_calculation')
def __polarity_calculation(doc):
    # Calculate polarity value for each token
    for sentence in doc.sents:
        for token in sentence:
            if token.pos_ == 'PUNCT':
                continue
            if token._.relevant and token.lemma_ in polarity_lexicon.keys():
                if token._.negated:
                    sentence._.polarity += (-1.0) * polarity_lexicon[token.lemma_]
                if token._.intensified:
                    sentence._.polarity += 1.5 * polarity_lexicon[token.lemma_]
                else:
                    sentence._.polarity += polarity_lexicon[token.lemma_]

    # Count doc length and sum polarities
    doc_length = 0
    for sentence in doc.sents:
        doc._.polarity += sentence._.polarity
        doc_length += sum(1 for token in sentence if token.pos_ != 'PUNCT')

    # Calculate doc polarity with min-max-scaling
    if doc_length > 0:
        if doc._.polarity > 0.0:
            doc._.polarity = (doc._.polarity + 1.0) / (doc_length + 1.0)
        elif doc._.polarity < 0.0:
            doc._.polarity = (doc._.polarity - 1.0) / (doc_length + 1.0)
    return doc


nlp.add_pipe('normalization', last=True)
nlp.add_pipe('negation_detection', last=True)
nlp.add_pipe('intensifier_detection', last=True)
nlp.add_pipe('polarity_calculation', last=True)
