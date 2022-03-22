import html
import re
import unicodedata
from collections import Counter

import pandas as pd
from IPython.display import HTML


# ====================
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


# ====================
def preview_regex_replace(find_re, replace_re, df, text_column_name='Text',
                          num_samples=10, chars_before_after=25,
                          normalize_spaces=True):
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
                text_to_display = html.escape(text[start_pos:end_pos])
                text_before = re.sub(
                    fr'({find_re})', r'<span style="color:red">\1</span>',
                    text_to_display
                )
                if normalize_spaces:
                    text_to_display = normalize_spaces_string(text_to_display)
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


# ====================
def regex_replace(find_re, replace_re, df, text_column_name='Text',
                  normalize_spaces=True):
    """Perform a regex replace operation to all cells of text column of
    dataframe"""

    df[text_column_name] = df[text_column_name].apply(
        lambda x: re.sub(find_re, replace_re, x))
    if normalize_spaces:
        df = normalize_spaces(df)

    return df


# ====================
def normalize_spaces_string(string):
    """Normalize spaces in a string"""

    return re.sub('  +', ' ', string)


# ====================
def normalize_spaces(df, text_column_name='Text'):
    """Normalize spaces in all cells in text column of a dataframe"""

    df[text_column_name] = df[text_column_name].apply(normalize_spaces_string)
    return df


# ====================
def normalize_unicode_string(string: str):
    """Normalize unicode characters (replace accented characters with their
    non-accented equivalents & remove other non-ascii characters) in a
    string"""

    return (unicodedata.normalize('NFKD', string)
            .encode('ascii', 'ignore').decode('utf8'))


# ====================
def normalize_unicode(df, text_column_name='Text'):
    """Normalize unicode characters (replace accented characters with their
    non-accented equivalents & remove other non-ascii characters) in all cells
    in text column of a dataframe"""

    df[text_column_name] = df[text_column_name].apply(normalize_unicode_string)
    return df


# ====================
def replace_with_equivalent_chars(df, text_column_name='Text'):
    """Replace special characters with equivalent ASCII characters."""

    EQUIVALENTS = {
        '’': "'",
        '‘': "'",
        'ʾ': "'",
        '“': '"',
        '…': '...'
    }

    def replace_with_equivalents(string):
        for find, replace in EQUIVALENTS.items:
            string = string.replace(find, replace)

    df[text_column_name] = df[text_column_name].apply(
        replace_with_equivalents)
    return df


# ====================
def show_prohibited_chars(df, prohibited_chars_re=r'[^A-Za-z0-9 \.,]',
                          text_column_name='Text', print_all=False):

    prohibited_counter = Counter()
    for _, row in df.iterrows():
        text = row[text_column_name]
        all_matches = re.findall(prohibited_chars_re, text)
        if all_matches:
            for match in all_matches:
                prohibited_counter.update(match)

    prohibited_total = sum(prohibited_counter.values())
    prohibited_unique = set(prohibited_counter.keys())

    print(f'Total of {prohibited_total} occurrences of',
          f'{len(prohibited_unique)} prohibited characters',
          'in dataframe.')
    if print_all:
        print(', '.join(prohibited_unique))
    top_10 = ', '.join([f'{char} ({count})'
                       for char, count in prohibited_counter.most_common(10)])
    print('Most common (up to 10 displayed): ',
          top_10)
