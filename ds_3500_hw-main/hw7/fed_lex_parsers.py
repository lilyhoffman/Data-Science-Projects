"""
File: fed_lex_parsers.py
Description: our json and federalist parsers for the federalist_lex library
"""

import json
from collections import Counter, defaultdict
import string


def json_parser(filename):
    """ parse a json file containing text data """

    # open the file
    f = open(filename)

    # load JSON data
    raw = json.load(f)
    text = raw['text']

    # split text into words
    words = text.split(" ")
    wc = Counter(words)
    num = len(words)

    # close the file
    f.close()

    return {'wordcount': wc, 'numwords':num}


def federalist_parser(filename, stop_words, k=5):
    """ parse a federalist paper text file """

    f = open(filename)

    # read text from file
    text = f.read()

    # clean text & extract words, avg sentence length and author information
    cleaned = _clean_fed_text(text)
    words = cleaned['words']
    avg_sent_len = cleaned['stats']
    author = cleaned['author']

    # filter out stop words
    filtered_words = [word for word in words if word not in stop_words]
    wc = Counter(filtered_words)
    num = len(filtered_words)

    # get the k most common words
    common_words = wc.most_common(k)
    sentiments = _get_sentiment_scores(wc)

    f.close()

    # returns parsed information
    return {
            'author': author,
            'wordcount': wc,
            'numwords': num,
            'avg_sent_leng': avg_sent_len,
            'most_common_words': common_words,
            'sentiments' : sentiments
            }
    

def _clean_fed_text(text):
    """ clean fedearlist paper text by lower casing,
    removing punctuation, and extracting author information """
    lowered_text = text.lower()
        
    sents = lowered_text.split('.')
    avg_len = sum(len(x.split()) for x in sents) / len(sents)
    closer = lowered_text.translate(str.maketrans('', '', string.punctuation))
    stripped = closer.strip()
    remove_newline = stripped.split('\n')
    author = remove_newline[0]
        
    cleaned = "".join(remove_newline)
    words = cleaned.split(" ")
    return_dict = {
            "author": author,
            "stats": avg_len,
            "words": words
        }
    return return_dict


def _get_sentiment_scores(counter):
    """ Calculate sentiment scores based on word occurrences in the text """

    result = defaultdict(dict)
    sentiment_map = {
        'federalism': ['federal', 'state', 'sovereignty', 'jurisdiction', 'union', 'confederation'],
        'representation': ['electorate', 'constituency', 'delegate', 'proportional', 'suffrage'],
        'rights': ['rights', 'liberties', 'freedoms', 'amendments', 'protections', 'welfare', 'tranquillity'],
        'education': ['enlightenment', 'informed', 'discourse', 'public sphere', 'civic engagement', 'literacy'],
        'power': ["authority","sovereignty","influence","control","dominion","governance","supremacy","command", 'unorganized', 'invasion']
    }

    # calculate sentiment scores for each category
    for sentiment, wl in sentiment_map.items():
        result[sentiment] = sum([counter.get(w,0) for w in wl])
    
    return result
        
