import re
import numpy as np
import pandas as pd
from math import isclose
from sklearn.model_selection import train_test_split


def remove_licences(text):
    lines = text.split('\n')
    output = []
    license_found = False
    for i in range(len(lines)):
        line = lines[i]
        if not license_found and ('copyright' in line.lower()
                                  or 'licence' in line.lower()
                                  or 'licensed' in line.lower()):
            license_found = True
            continue
        elif license_found and not line.startswith('#'):
            license_found = False
        elif license_found and line.startswith('#'):
            continue
        output.append(line)
    return '\n'.join(output)


def remove_links(text):
    text = re.compile(r'https?://\S+').sub('', text)
    return text if text else ''


def drop_empty_rows(dataframe, column='text'):
    drop_idx = dataframe[dataframe[column] == ''].index
    # If there is only '<BOS><EOS>' then it is also considered empty
    drop_idx.append(dataframe[dataframe[column] == '<BOS><EOS>'].index)
    return dataframe.drop(drop_idx)


def deduplicate(dataframe, column='text'):
    # Drop exact duplicates
    return dataframe.drop_duplicates(subset=[column])


def filtering(dataframe, column='text'):
    # Get the length of each line in the 'text' column
    line_lengths = dataframe[column].str.split('\n').apply(
        lambda x: [len(line) for line in x]
    )
    # Compute the average and maximum line length for each row
    avg_lengths = line_lengths.apply(np.mean)
    max_lengths = line_lengths.apply(np.max)
    # Compute the fraction of alphanumeric characters in each row
    alpha_numeric_fractions = dataframe[column].apply(
        lambda x: sum(c.isalnum() for c in x) / len(x)
    )
    # Filter out the rows that satisfy the given conditions
    mask = (avg_lengths <= 100) & (max_lengths <= 1000) & (alpha_numeric_fractions >= 0.25)
    filtered_dataframe = dataframe.loc[mask, :]
    return filtered_dataframe


def has_docstring(text):
    """
    Check if a given text contains a docstring.

    Args:
        text (str): The text to check.

    Returns:
        bool: True if the text contains a docstring, False otherwise.
    """
    docstring_pattern = r'("""|\'\'\')(.*?)\1'
    return re.search(docstring_pattern, text, re.DOTALL) is not None


def clean(dataframe, column='text'):
    # Clean samples
    dataframe[column] = dataframe[column].apply(remove_licences)
    dataframe[column] = dataframe[column].apply(remove_links)
    # Remove samples that do not match requirements
    dataframe = drop_empty_rows(dataframe)
    dataframe = deduplicate(dataframe)
    dataframe = filtering(dataframe)
    dataframe['has_docstring'] = dataframe[column].apply(has_docstring)
    dataframe = dataframe[dataframe['has_docstring']]
    return dataframe.drop('has_docstring', axis=1)


def extract_text(dataframe, path, column='text'):
    f = open(path, 'w')
    file = ''
    texts = dataframe[column].tolist()
    for text in texts:
        text = str(text).strip()
        file += text + '\n'
    f.write(file)


def split(dataset, ratio, directory='', random_state=69):
    assert isclose(sum(ratio), 1)
    train_test_ratio = round(ratio[0] + ratio[1], 1)
    train_valid_ratio = ratio[0] / train_test_ratio
    train, test = train_test_split(dataset,
                                   train_size=train_test_ratio,
                                   random_state=random_state)
    train, valid = train_test_split(train,
                                    train_size=train_valid_ratio,
                                    random_state=random_state)
    extract_text(valid, f'{directory}valid.txt')
    extract_text(train, f'{directory}train.txt')
    extract_text(test, f'{directory}test.txt')


data = pd.read_csv('data/data.csv')
data = clean(data)
split(data, ratio=(0.7, 0.2, 0.1), directory='data/')
data.to_csv('data/data.csv', index=False)
