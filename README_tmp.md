[-^TARGET=README.md
[-^TDC=text_data_cleaner/text_data_cleaner.py
# Text Data Cleaner

A Python library for cleaning text data for use in machine learning and natural language processing applications

Designed to be used in IPython notebooks (Jupyter, Google Colab, etc.).

Developed and used for the paper "Comparison of Token- and Character-Level Approaches to Restoration of Spaces, Punctuation, and Capitalization in Various Languages", which is scheduled for publication in December 2022.

## Interactive demo

The quickest and best way to get acquainted with the library is through the interactive demo [here](https://colab.research.google.com/drive/1tXnlmjPEzJx1ZNAAVXcvP3N2Q-kxpsQL?usp=sharing), where you can walk through the steps involved in using the library and clean some sample data from the Ted Talks dataset used in the paper.

Alternatively, scroll down for instructions on getting started and basic documentation.

## Getting started

### Install the library using `pip`

```
!pip install git+https://github.com/ljdyer/Text-Data-Cleaner.git
```

### Import the `TextDataCleaner` class

```python
from text_data_cleaner import text_data_cleaner
```

## Clean data using the `TextDataCleaner` class

### Initialize an instance of the `TextDataCleaner` class

#### `TextDataCleaner.__init__`

[-*func_or_method TDC>__init__

#### Example usage:

```python
my_fre = FeatureRestorationEvaluator(
    data_cleaner = TextDataCleaner(data['transcript'])
)
```

<img src="readme-img/01-init.PNG"></img>

### Show unwanted characters in the dataset

#### `TextDataCleaner.show_unwanted_chars`

[-*func_or_method FRMG>show_unwanted_chars

#### Example usage:

```python
my_fre.show_prfs()
```

<img src="readme-img/02-show_prfs.PNG"></img>

### Show confusion matrices

#### `FeatureRestorationEvaluator.show_confusion_matrices`

[-*func_or_method FRMG>show_confusion_matrices

#### Example usage:

```python
my_fre.show_confusion_matrices('all', ['CAPS'])
```

<img src="readme-img/03-show_confusion_matrices.PNG"></img>

### Show word error rate (WER) information

#### `FeatureRestorationEvaluator.show_wer_info`

[-*func_or_method FRMG>show_wer_info

#### Example usage:

```python
my_fre.show_wer_info()
```

<img src="readme-img/04-show_wer_info.PNG"></img>

### Display the hypothesis document with false positives and false negatives highlighted

#### `FeatureRestorationEvaluator.show_text_display`

[-*func_or_method FRMG>show_text_display

#### Example usage:

```python
my_fre.show_text_display(0, num_rows=5, chars_per_row=40)
```

<img src="readme-img/05-show_text_display.PNG"></img>

### Display a list of errors for a given feature in a given document

#### `FeatureRestorationEvaluator.show_feature_errors`

[-*func_or_method FRMG>show_feature_errors

#### Example usage:

```python
my_fre.show_feature_errors(0, '.')
```

<img src="readme-img/06-show_feature_errors.PNG"></img>