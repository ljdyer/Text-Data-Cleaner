import html
import random
import re
import unicodedata
from collections import Counter
from contextlib import contextmanager
from typing import List, Tuple, Union

import pandas as pd
from IPython.display import HTML, display
from IPython.core.getipython import get_ipython

PREVIEW_BEFORE = """\
<pre>{ellipsis_before}{text_before}\
<span style="color:red">{match}</span>\
{text_after}{ellipsis_after}</pre>"""
PREVIEW_AFTER = """\
<pre>{ellipsis_before}{text_before}\
<span style="color:green">{replacement}</span>\
{text_after}{ellipsis_after}</pre>"""

NAMED_OPERATIONS = {
    'NORMALIZE_UNICODE_TO_ASCII': 'Normalize unicode to ascii'
}


# ====================
def set_css():
    display(HTML('''
    <style>
        pre {
            white-space: pre-wrap;
        }
    </style>
    '''))


get_ipython().events.register('pre_run_cell', set_css)


# ====================
class TextDataCleaner:

    # ====================
    def __init__(self,
                 docs: Union[List, pd.Series],
                 normalize_spaces: bool = True):
        """Initialize an instance of the class

        Args:
          docs (Union[List, pd.Series]):
            The list of documents to clean.
          normalize_spaces (bool, optional):
            Whether or not to replace two or more subsequent spaces with a
            single space after carrying out each operation. Defaults to True.
        """

        if isinstance(docs, pd.Series):
            docs = docs.to_list()
        self.docs_orig = docs
        self.docs_latest = docs
        self.operation_history = []
        self.normalize_spaces = normalize_spaces
        print("Initialized.")
        print()
        self.show_counts(show_change=False)

    # ====================
    def show_counts(self, show_change: bool = True):
        """Print the numbers of documents, tokens, and characters in the
        latest version of the dataset.
        """

        docs = self.docs_latest
        if show_change is True:
            docs_before = self.num_docs
            tokens_before = self.num_tokens
            chars_before = self.num_chars
        num_docs = len(docs)
        num_tokens = sum(map(len, map(lambda x: x.split(), docs)))
        num_chars = sum(map(len, docs))
        if show_change is False:
            print('Number of documents:', num_docs)
            print('Total number of tokens:', num_tokens)
            print('Total number of characters:', num_chars)
        else:
            print(f'Number of documents: {num_docs} ' +
                  f' {show_change(docs_before, num_docs)}')
            print(f'Total number of tokens: {num_tokens} ' +
                  f' {show_change(tokens_before, num_tokens)}')
            print(f'Total number of characters: {num_chars} ' +
                  f' {show_change(chars_before, num_chars)}')
        self.num_docs = num_docs
        self.num_tokens = num_tokens
        self.num_chars = num_chars

    # ====================
    def show_doc(self, doc_idx: int):

        print(self.docs_latest[doc_idx])

    # ====================
    def show_unwanted_chars(self,
                            unwanted_chars: str = None):
        """Show unwanted characters in the latest version of the dataset

        Args:
          unwanted_chars (str, optional):
            A regular expression that matches unwanted characters.
            E.g. r'[^A-Za-z0-9 \.,]'      # noqa: W605
            if you only want alphanumeric characters, spaces, periods,
            and commas in the cleaned dataset.

        Raises:
          ValueError:
            If unwanted_chars has not been set for the class instances and
            is also not passed as a parameter.
        """
        if unwanted_chars is not None:
            self.unwanted_chars = unwanted_chars
        else:
            if not hasattr(self, 'unwanted_chars'):
                raise ValueError(
                    "Unwanted characters have not been specified. " +
                    "Call the method again with the unwanted_chars parameter."
                )
        docs = self.docs_latest
        unwanted_counter = Counter(
            match for text in docs
            for match in re.findall(unwanted_chars, text)
        )
        unwanted_total = sum(unwanted_counter.values())
        unwanted_unique = set(unwanted_counter.keys())
        print(f'Total of {unwanted_total} occurrences of',
              f'{len(unwanted_unique)} unwanted characters',
              'in dataframe.')
        print(', '.join(unwanted_unique))
        top_10 = ', '.join(
            [f'{char} ({count})'
             for char, count in unwanted_counter.most_common(10)]
        )
        print('Most common (up to 10 displayed): ', top_10)

    # ====================
    def show_operation_history(self):

        for operation_idx, operation in enumerate(
         self.operation_history(), start=1):
            print(f"{operation_idx}: ", end='')
            if isinstance(operation, tuple):
                find, replace = operation
                print(f'Regex replacement: {find} => {replace}')
            elif isinstance(operation, str):
                print(operation)

    # ====================
    def preview_replace(self,
                        find_replace: Tuple[str],
                        num_samples: int = 10,
                        context_chars_before_after: int = 25):
        """Preview the effect of carrying out a regular expression replacement
        operation on the dataset.

        Args:
          find_replace (Tuple[str]):
            A tuple (find, replace) of the regular expression find and replace strings.
            Examples:
                (r'[\(|\)]', '')    # noqa W605
                (r'([0-9]+):([0-9]+)', r'\1 \2')
          num_samples (int, optional):
            The number of samples (locations in documents where a replacement would take place)
            to display. Defaults to 10.
          context_chars_before_after (int, optional):
            The number of characters to display before and after the replacement location in
            each sample. Defaults to 25.
        """

        find, replace = find_replace
        docs = self.docs_latest
        matches_by_doc = [list(re.finditer(find, text)) for text in docs]
        num_docs_with_matches = len([m for m in matches_by_doc if len(m) > 0])
        if num_docs_with_matches == 0:
            print('No matches found!')
            return
        doc_and_match_idxs = [
            (doc_idx, match_idx)
            for doc_idx in range(len(docs))
            for match_idx in range(len(matches_by_doc[doc_idx]))
        ]
        if num_samples > len(doc_and_match_idxs):
            sample_idxs = doc_and_match_idxs
        else:
            sample_idxs = random.sample(doc_and_match_idxs, k=num_samples)
        samples = []
        for doc_idx, match_idx in sample_idxs:
            doc = docs[doc_idx]
            match = matches_by_doc[doc_idx][match_idx]
            preview_before, preview_after = self.preview_before_and_after(
                doc, find, replace, match, context_chars_before_after)
            samples.append(
                {
                    'Document index': doc_idx,
                    'Match number': (f"{match_idx+1} of " +
                                     f"{len(matches_by_doc[doc_idx])}"),
                    'Before': preview_before,
                    'After': preview_after
                }
            )
        samples_df = pd.DataFrame(samples)
        with pandas_options([('display.colheader_justify', 'center')]):
            display(
                HTML(
                    samples_df.to_html(escape=False, index=False)
                )
            )
        print(
            f'Total of {len(doc_and_match_idxs)} matches in ' +
            f'{num_docs_with_matches} documents (rows).'
        )
        print()
        self.last_previewed = find_replace
        print("To apply this replacement operation to the dataset, run the" +
              "apply_last_previewed method.")

    # ====================
    def apply_last_previewed(self):

        self.replace(self.last_previewed)

    # ====================
    def replace(self,
                find_replace: Union[List[Tuple], Tuple]):
        """Perform a regular expression replacement operation on the whole
        dataset.

        Args:
          find_replace (Union[List[Tuple], Tuple]):
            A tuple (find, replace) of regular expression find and replace strings,
            or a list of such tuples.
            Examples of (find, replace) tuples:
                (r'[\(|\)]', '')    # noqa W605
                (r'([0-9]+):([0-9]+)', r'\1 \2')
        """                

        if isinstance(find_replace, tuple):
            find_replace = [find_replace]
        for find, replace in find_replace:
            self.docs_latest = [
                self.re_replace(find, replace, doc) for doc in self.docs_latest
            ]
        # Drop empty docs
        len_before = len(self.docs_latest)
        self.docs_latest = [
            doc for doc in self.docs_latest
            if not (doc.isspace() or len(doc) == 0)
        ]
        len_after = len(self.docs_latest)
        if len_after < len_before:
            print(
                "Removed {len_before-len_after} documents that were empty " +
                "or contained only spaces following the operations."
            )
        print('Done.')
        self.operation_history.extend(find_replace)
        print()
        self.show_counts()

    # ====================
    def preview_before_and_after(self,
                                 doc: str,
                                 find: str,
                                 replace: str,
                                 match: re.Match,
                                 context_chars_before_after: int
                                 ) -> Tuple[str]:

        match_start, match_end = match.span()
        match_str = doc[match_start:match_end]
        text_before = doc[:match_start]
        text_after = doc[match_end:]
        ellipsis_before, context_before = \
            get_context_before(text_before, context_chars_before_after)
        ellipsis_after, context_after = \
            get_context_after(text_after, context_chars_before_after)
        preview_before = PREVIEW_BEFORE.format(
            ellipsis_before=ellipsis_before,
            text_before=html.escape(context_before),
            match=html.escape(match_str),
            text_after=html.escape(context_after),
            ellipsis_after=ellipsis_after
        )
        text_before = self.re_replace(find, replace, text_before)
        text_after = self.re_replace(find, replace, text_after)
        replacement = self.re_replace(find, replace, match_str)
        ellipsis_before, context_before = \
            get_context_before(text_before, context_chars_before_after)
        ellipsis_after, context_after = \
            get_context_after(text_after, context_chars_before_after)
        preview_after = PREVIEW_AFTER.format(
            ellipsis_before=ellipsis_before,
            text_before=html.escape(context_before),
            replacement=html.escape(replacement),
            text_after=html.escape(context_after),
            ellipsis_after=ellipsis_after
        )
        return preview_before, preview_after

    # ====================
    def re_replace(self,
                   find: str,
                   replace: str,
                   text: str) -> str:

        replaced = re.sub(find, replace, text)
        if self.normalize_spaces:
            replaced = re.sub(r'  +', ' ', replaced)
        return replaced

    # ====================
    def normalize_unicode_to_ascii(self):
        """Normalize all unicode characters in the dataset to the ascii equivalents.

        Replaces accented characters with their non-accented equivalents and
        removes other non-ascii characters.
        """

        self.docs_latest = [
            (unicodedata.normalize('NFKD', doc)
                .encode('ascii', 'ignore').decode('utf8'))
            for doc in self.docs_latest
        ]
        self.operation_history.append('NORMALIZE-UNICODE-TO-ASCII')


# # === HELPER FUNCTIONS ===

# ====================
def get_context_before(text: str,
                       context_len: int) -> Tuple[str, str]:

    ellipsis = '... ' if len(text) > context_len else '    '
    context = text[-context_len:].rjust(context_len)
    return ellipsis, context


# ====================
def get_context_after(text: str,
                      context_len: int) -> Tuple[str, str]:

    ellipsis = ' ...' if len(text) > context_len else '    '
    context = text[:context_len].ljust(context_len)
    return ellipsis, context


# ====================
def show_change_(before, after):

    if before > after:
        return f'<span style="color:green">↓ {after-before}</span>'
    elif after < before:
        return f'<span style="color:red">↑ {before-after}</span>'
    else:
        return 'no change'


# ====================
def display_html(x: str):

    display(HTML(x))


# # === CONTEXT MANAGERS ===

# =====
@contextmanager
def pandas_options(options: List[Tuple]):

    before = [pd.get_option(option_name) for option_name, _ in options]
    for option in options:
        pd.set_option(*option)
    yield
    for option_idx, option in enumerate(options):
        pd.set_option(option[0], before[option_idx])
