import data_processing.comment_processing as cp

text = 'Das ist ja nicht verboten ich!'

doc = cp.nlp(text)

print(doc._.polarity)
for token in doc:
    print(token, token.lemma_, token._.polarity, token._.relevant, token._.intensified, token._.negated)
