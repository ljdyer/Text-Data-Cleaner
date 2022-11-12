from setuptools import setup

REQUIREMENTS = [
    'pandas'
]

setup(
    name='text_data_cleaner',
    version='0.1',
    description="""Clean text data for machine learning projects""",
    author='Laurence Dyer',
    author_email='ljdyer@gmail.com',
    url='https://github.com/ljdyer/text-data-cleaner',
    packages=['text_data_cleaner'],
    install_requires=REQUIREMENTS
)
