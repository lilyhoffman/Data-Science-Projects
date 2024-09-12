"""
File: federalist_lex.py
Description: A reusable library for text analysis and comparison
"""

import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import string
import sankey as sk
import pandas as pd
from wordcloud import WordCloud
import plotly.graph_objects as go


class FederalistLex:

    def __init__(self):
        """ constructor """
        self.data = defaultdict(dict)

    @staticmethod
    def _default_parser(filename, stop_words):
        """ default text parser for processing simple unformatted text files. """
        
        f = open(filename)
        text = f.read()
        cleaned = FederalistLex.clean_text(text)
        words = cleaned['words']
        avg_len = cleaned['stats']
        filtered_words = [word for word in words if word not in stop_words]

        results = {
            'wordcount': Counter(filtered_words),
            'numwords': len(filtered_words),
            'avg_sentence_length': avg_len
        }
        print("Parsed: ", filename, ": ", results)
        return results
    
    @staticmethod
    def load_stop_words(stopfile):
        """ load stop words from a file """

        f = open(stopfile)
        stop_words = f.read().split("\n")
        return stop_words
    
    @staticmethod
    def clean_text(text):
        """ Clean the text by lower casing,
        removing punctuation, and extracting words. """

        lowered_text = text.lower()
        sents = lowered_text.split('.')
        avg_len = sum(len(x.split()) for x in sents) / len(sents)
        closer = lowered_text.translate(str.maketrans('', '', string.punctuation))
        stripped = closer.strip()
        remove_newline = stripped.split('\n')
        cleaned = "".join(remove_newline)
        words = cleaned.split(" ")
        return_dict = {
            "stats": avg_len,
            "words": words
        }
        return return_dict

    def load_text(self, filename, label=None, parser=None):
        """ Load text from a file, parse it, and store the results. """

        stop_words = FederalistLex.load_stop_words('texts/stop_words.txt')
        if parser is None:
            results = FederalistLex._default_parser(filename, stop_words)
        else:
            results = parser(filename, stop_words)

        if label is None:
            label = filename

        for k, v in results.items():
            self.data[k][label] = v

    def generate_radar_chart(self):
        """
            Generate a radar chart based on sentiment scores.
        """

        cats = list(self.data['sentiments']['fed1'].keys())
        fig = go.Figure()
        
        for text, sl in self.data['sentiments'].items():
            fig.add_trace(go.Scatterpolar(
                r=[val for rep, val in sl.items()],
                theta=cats,
                fill='toself',
                name=text
                ))
            fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                        )),
                    showlegend=True
                    )

        fig.show()

    def generate_word_clouds(self):
        """
        generates word clouds for each text file, the size of each word shows frequency in txt
        """
        num_files = len(self.data['wordcount'])
        num_cols = 2  # Number of columns for subplots
        num_rows = (num_files + num_cols - 1) // num_cols  # calc num of rows based on num of files

        # creates subplots
        fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 7))

        for i, (label, word_count) in enumerate(self.data['wordcount'].items()):
            wordcloud = WordCloud(width=400, height=200, background_color='white').generate_from_frequencies(word_count)

            # subplot indices
            row_index = i // num_cols
            col_index = i % num_cols

            # plot word cloud on subplot
            if num_rows == 1:  # for single row, axes will not be a list
                axes[col_index].imshow(wordcloud, interpolation='bilinear')
                axes[col_index].set_title(f'Word Cloud for {label}')
                axes[col_index].axis('off')
            else:
                axes[row_index, col_index].imshow(wordcloud, interpolation='bilinear')
                axes[row_index, col_index].set_title(f'Word Cloud for {label}')
                axes[row_index, col_index].axis('off')

        # hide any empty subplots
        for j in range(num_files, num_rows * num_cols):
            if num_rows == 1:  # For a single row, axes will not be a list
                axes[j].axis('off')
            else:
                row_index = j // num_cols
                col_index = j % num_cols
                axes[row_index, col_index].axis('off')

        plt.tight_layout()
        plt.show()

    def wordcount_sankey(self, word_list= None, k= 5):
        """ Generate a Sankey diagram based on word counts. """

        rows = []
        if word_list is None:
            most_common = self.data['most_common_words']
            rows = [[self.data['author'][text], word, count] for text, wc in most_common.items() for word, count in wc]
        
        else:
            wc = self.data['wordcount']
            rows = [[self.data['author'][text], word, counter.get(word, 0)] for text, counter in wc.items() for word in word_list]

        df = pd.DataFrame(rows, columns=['text', 'word', 'counts'])
        sk.make_sankey(df, 'text', 'word', vals='counts')
