import pandas as pd
import html
import pickle
import urllib
from contextlib import contextmanager
from typing import Any, Tuple, List

from IPython.display import HTML, display   # type: ignore

WRAP_PRE = "<style>pre {white-space: pre-wrap;}</style>"


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
        return f'<span style="color:green">↓ {before-after}</span>'
    elif after < before:
        return f'<span style="color:red">↑ {after-before}</span>'
    else:
        return 'no change'


# ====================
def display_html(content: str):

    display(HTML(content))


# ====================
def display_html_pre(content: str):

    display_html(f"<pre>{content}</pre>")


# ====================
def display_text_wrapped(content: str):

    content = html.escape(content)
    display_html(WRAP_PRE + f"<pre>{content}</pre>")


# ====================
def save_pickle(data: Any, fp: str):
    """Save data to a .pickle file"""

    with open(fp, 'wb') as f:
        pickle.dump(data, f)


# ====================
def load_pickle(fp: str) -> Any:
    """Load a .pickle file and return the data"""

    if 'http' in fp:
        with urllib.request.urlopen(fp) as f:
            unpickled = pickle.load(f)
    else:
        with open(fp, 'rb') as f:
            unpickled = pickle.load(f)
    return unpickled


# ====================
@contextmanager
def pandas_options(options: List[Tuple]):

    before = [pd.get_option(option_name) for option_name, _ in options]
    for option in options:
        pd.set_option(*option)
    yield
    for option_idx, option in enumerate(options):
        pd.set_option(option[0], before[option_idx])
