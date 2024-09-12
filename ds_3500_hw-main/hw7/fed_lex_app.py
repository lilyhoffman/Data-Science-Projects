"""
File: fed_lex_app.py
Description: tests our federalist_lex library
"""


from federalist_lex import FederalistLex
import fed_lex_parsers as tp
import pprint as pp


def main():
    tt = FederalistLex()
    tt.load_text('texts/fed1.txt', 'fed1', parser=tp.federalist_parser)
    tt.load_text('texts/fed2.txt', 'fed2', parser=tp.federalist_parser)
    tt.load_text('texts/fed8.txt', 'fed8', parser=tp.federalist_parser)
    tt.load_text('texts/fed9.txt', 'fed9', parser=tp.federalist_parser)
    tt.load_text('texts/fed21.txt', 'fed21', parser=tp.federalist_parser)
    tt.load_text('texts/fed37.txt', 'fed37', parser=tp.federalist_parser)
    tt.load_text('texts/fed42.txt', 'fed42', parser=tp.federalist_parser)
    tt.load_text('texts/fed64.txt', 'fed64', parser=tp.federalist_parser)

    # creates visualizations
    tt.generate_word_clouds()
    tt.wordcount_sankey()
    tt.generate_radar_chart()


if __name__ == '__main__':
    main()
