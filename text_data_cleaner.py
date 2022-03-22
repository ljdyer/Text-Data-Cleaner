import pandas as pd
import re
import html
import unicodedata
from collections import Counter
from IPython.display import HTML


def show_doc_and_word_counts(df, text_column_name='Text'):
    """Show the number of documents (rows) and words in a text column of a
    pandas dataframe.

    Words are defined simply as consecutive chains of non-whitespace characters
    (because word tokenizing takes time)"""

    # Doc (word) count
    num_docs_total = len(df)
    # Word count
    df['num_words'] = df[text_column_name].apply(lambda x: len(x.split()))
    num_words_total = sum(df['num_words'])

    print(f'{num_words_total} words in {num_docs_total} documents (rows).')


def preview_regex_replace(find_re, replace_re, df, text_column_name='Text',
                          num_samples=10, chars_before_after=25):
    """Preview the effects of a regex replace operation before you apply it."""

    matches = []
    num_docs_with_matches = 0
    for index, row in df.iterrows():
        text = row[text_column_name]
        iter_matches = list(re.finditer(find_re, text))
        if iter_matches:
            num_docs_with_matches += 1
            for count, match in enumerate(iter_matches):
                match_start, match_end = match.span()
                start_pos = max(0, match_start-chars_before_after)
                end_pos = min(match_end + chars_before_after, len(text))
                text_to_display = text[start_pos:end_pos]
                text_before = re.sub(
                    fr'({find_re})', r'<span style="color:red">\1</span>',
                    text_to_display
                )
                text_after = re.sub(
                    fr'({find_re})',
                    fr'<span style="color:green">{replace_re}</span>',
                    text_to_display
                )
                matches.append((index, f'{count}/{len(iter_matches)}',
                                text_before, text_after))

    matches_df = pd.DataFrame(matches)
    matches_df.columns = ['Row index', 'Match number', 'Before', 'After']
    pd.set_option('display.max_colwidth', None)
    display(HTML(matches_df.sample(n=num_samples)
                 .to_html(escape=False, index=False)))
    pd.set_option('display.max_colwidth', 50)

    print(f'Total of {len(matches)} matches in {num_docs_with_matches}',
          'documents (rows).')
