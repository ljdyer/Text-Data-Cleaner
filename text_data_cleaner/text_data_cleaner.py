import html
import re
import unicodedata
from collections import Counter

import numpy as np
import pandas as pd
from IPython.display import HTML

from typing import Union, List


# ====================
class TextDataCleaner:

    # ====================
    def __init__(self, docs: Union[List, pd.Series]):
        """Initialize an instance of the class

        Args:
          docs (Union[List, pd.Series]):
            The list of documents to clean.
        """

        if isinstance(docs, pd.Series):
            docs = docs.to_list()    
        self.docs_orig = docs
        self.docs_latest = docs

    # ====================
    def show_counts(self):
        """Print the numbers of documents, tokens, and characters in the
        latest version of the dataset.
        """        
    
        docs = self.docs_latest
        num_docs = len(docs)
        num_tokens = sum(map(len, map(lambda x: x.split(), docs)))
        num_chars = sum(map(len, docs))
        print('Number of documents: ', num_docs)
        print('Total number of tokens: ', num_tokens)
        print('Total number of characters: ', num_chars)

    # ====================
    def show_prohibited_chars(self,
                              prohibited_chars: str = None):
                            
        if prohibited_chars is not None:
            self.prohibited_chars = prohibited_chars
        else:
            if not hasattr(self, 'prohibited_chars'):
                raise ValueError(
                    "Prohibited characters have not been specified. " + \
                    "Call the method again with the prohibited_chars parameter."
                )

        prohibited_counter = Counter()
        docs_list = self.docs_latest.to_list()
        for text in docs_list:
            all_matches = re.findall(prohibited_chars, text)
            if all_matches:
                for match in all_matches:
                    prohibited_counter.update(match)

        prohibited_total = sum(prohibited_counter.values())
        prohibited_unique = set(prohibited_counter.keys())

        print(f'Total of {prohibited_total} occurrences of',
              f'{len(prohibited_unique)} prohibited characters',
              'in dataframe.')
        print(', '.join(prohibited_unique))
        top_10 = ', '.join([f'{char} ({count})'
                            for char, count in prohibited_counter.most_common(10)])
        print('Most common (up to 10 displayed): ', top_10)

    # ====================
    def preview_replace(self,
                        find_re: str,
                        replace_re: str,
                        num_samples: int = 10,
                        context_chars_before_after: int = 25,
                        normalize_spaces: bool = True):

        matches = []
        num_docs_with_matches = 0
        docs_list = self.docs_latest.to_list()
        for index, text in enumerate(docs_list):
            iter_matches = list(re.finditer(find_re, text))
            if iter_matches:
                num_docs_with_matches += 1
                for count, match in enumerate(iter_matches):
                    context_str = get_context_str(
                        text, match, context_chars_before_after)
                    text_before = color_matches_red(
                        find_re, context_str)
                    text_after = color_replacements_green(
                        find_re, replace_re, context_str, normalize_spaces)
                    match_number = f'{count+1}/{len(iter_matches)}'
                    matches.append((index, match_number, text_before, text_after))
        if not matches:
            print('No matches found!')
            return
        matches_df = pd.DataFrame(
            matches, columns=['Doc index', 'Match number', 'Before', 'After'])
        pd.set_option('display.max_colwidth', None)
        display(
            HTML(
                matches_df.sample(
                    n=min(len(matches_df), num_samples)
                ).to_html(escape=False, index=False)
            )
        )
        pd.set_option('display.max_colwidth', 50)
        print(f'Total of {len(matches)} matches in {num_docs_with_matches}',
            'documents (rows).')




    # ====================
    def regex_replace(self,
                      regex_list: list,
                    df: pd.DataFrame,
                    text_column_name: str = 'Text',
                    norm_spaces: bool = True,
                    drop_empty_rows: bool = True
                    ) -> pd.DataFrame:

        """Perform a sequence of one or more regex replace operations on all cells
        in the text column of your dataframe

        Required arguments:
        -------------------
        regex_list: list                    A list of (find, replace) tuples
                                            e.g. (r'\(\w+\)', r'')
        df: pd.DataFrame                    A dataframe with a text column

        Optional keyword arguments:
        ---------------------------
        text_column_name: str = 'Text'      The name of the text column in the
                                            dataframe
        norm_spaces: bool = True,           If True, normalizes spaces after
                                            performing replacement
        drop_empty_rows: bool = True        If True, drops any rows with empty
                                            strings following replacement
        """

        for find_re, replace_re in regex_list:
            df[text_column_name] = df[text_column_name].apply(
                lambda x: re.sub(find_re, replace_re, x))

        # Normalize spaces
        if norm_spaces:
            df = normalize_spaces(df, text_column_name=text_column_name)

        # Drop empty rows
        if drop_empty_rows:
            df[text_column_name].replace('', np.nan, inplace=True)
            df[text_column_name].replace(' ', np.nan, inplace=True)
            df.dropna(subset=[text_column_name], inplace=True)

        print('Done.')
        show_doc_and_word_counts(df, text_column_name=text_column_name)

        return df


# # ====================
# def normalize_unicode(df: pd.DataFrame,
#                       text_column_name='Text'
#                       ) -> pd.DataFrame:

#     """Normalize unicode characters (replace accented characters with their
#     non-accented equivalents & remove other non-ascii characters) in all cells
#     in the text column of your dataframe.

#     Required arguments:
#     -------------------
#     df: pd.DataFrame                    A dataframe with a text column

#     Optional keyword arguments:
#     ---------------------------
#     text_column_name: str = 'Text'      The name of the text column in the
#                                         dataframe
#     """

#     df[text_column_name] = df[text_column_name].apply(normalize_unicode_string)
#     return df


# # === HELPER FUNCTIONS ===

# ====================
def get_context_str(text: str,
                    match: re.Match,
                    context_chars_before_after: int) -> str:
    """Return a substring showing the context of a regex match in a string"""

    match_start, match_end = match.span()
    start_pos = max(0, match_start-context_chars_before_after)
    ellipsis_before = '...' if start_pos > 0 else ''
    end_pos = min(match_end+context_chars_before_after, len(text))
    ellipsis_after = '...' if end_pos < len(text) else ''
    return ellipsis_before + text[start_pos:end_pos] + ellipsis_after


# ====================
def color_matches_red(find_re: str, input_str: str) -> str:
    """Return an HTML string in which all instances of the regex in the string
    are colored red"""

    colored = re.sub(f"({find_re})", r'RED_START\1COLOR_END', input_str)
    colored = html.escape(colored)
    colored = colored.replace('RED_START', '<span style="color:red">')
    colored = colored.replace('COLOR_END', '</span>')
    return colored

# ====================
def color_replacements_green(find_re: str,
                             replace_re: str,
                             input_str: str,
                             norm_spaces: bool
                             ) -> str:
    """Perform a regex find and replace operation on an HTML string in which all of
    the replaced parts are colored green"""

    colored = re.sub(find_re, rf'GREEN_START{replace_re}COLOR_END', input_str)
    if norm_spaces:
        colored = normalize_spaces_string(colored)
    colored = html.escape(colored)
    colored = colored.replace('GREEN_START', '<span style="color:green">')
    colored = colored.replace('COLOR_END', '</span>')
    return colored


# ====================
def normalize_spaces(df: pd.DataFrame,
                     text_column_name='Text'
                     ) -> pd.DataFrame:

    """Normalize spaces in all cells in text column of a dataframe"""

    df[text_column_name] = df[text_column_name].apply(normalize_spaces_string)
    return df


# ====================
def normalize_spaces_string(input_str: str) -> str:

    """Normalize spaces in a string"""

    return re.sub('  +', ' ', input_str)


# ====================
def normalize_unicode_string(input_str: str) -> str:

    """Normalize unicode characters (replace accented characters with their
    non-accented equivalents & remove other non-ascii characters) in a
    string"""

    return (unicodedata.normalize('NFKD', input_str)
            .encode('ascii', 'ignore').decode('utf8'))
