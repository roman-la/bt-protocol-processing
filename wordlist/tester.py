import data_processing.comment_processing as cp

text = 'Möglichst wenig Antworten!'

doc = cp.nlp(text)

print(doc._.polarity)
for token in doc:
    print(token, token.lemma_, token._.polarity, token._.relevant, token._.intensified, token._.negated)
