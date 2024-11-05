from types import NotImplementedType
import json
import re
import spacy
from english_words import get_english_words_set
from pprint import pprint
words = get_english_words_set(['web2'], lower=True)

nlp=spacy.load('en_core_web_sm')


with open('./Twitter Data.json', 'r') as f:
    d = json.load(f)
data = d[:10000]
tweet = [n['content'] for n in data]
doc= nlp(''.join(tweet))
lemma = [token.lemma_ for token in doc]

with open('./parole.txt', 'w') as j:
  file = j
  for token in lemma:
    if token in words:
      file.write(token + ' ')
