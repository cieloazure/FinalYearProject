from nltk.metrics.distance import *
from nltk import stem, tokenize
stemmer = stem.PorterStemmer()


def normalize(s):
    tokenizer = tokenize.RegexpTokenizer(r'\w+')
    words = tokenizer.tokenize(s.lower().strip())
    return ' '.join([stemmer.stem(w) for w in words])


def fuzzy_match(s1, s2, max_dist=3):
    return edit_distance(normalize(s1), normalize(s2)) <= max_dist
