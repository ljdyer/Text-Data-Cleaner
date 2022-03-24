# Text data cleaner

Helper functions for cleaning text data in a pandas dataframe.

## How to use

Recommended method to include the module in your notebook is Method A.2.1 in:

https://colab.research.google.com/github/jckantor/cbe61622/blob/master/docs/A.02-Downloading_Python_source_files_from_github.ipynb

## Functions

### show_doc_and_word_counts

```python
# ====================
def show_doc_and_word_counts(df: pd.DataFrame,
                             text_column_name: str = 'Text'):

    """Show the number of documents (rows) and words in a text column of a
    pandas dataframe.

    Words are defined simply as consecutive chains of non-whitespace characters
    (because word tokenizing takes time!)

    Required arguments:
    -------------------
    df: pd.DataFrame    A dataframe with a text column

    Optional keyword arguments:
    ---------------------------
    text_column_name: str = 'Text'      The name of the text column in the
                                        dataframe
    """
```

(to be continued)
