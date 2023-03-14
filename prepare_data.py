import numpy as np
import pandas as pd
from math import isclose
from sklearn.model_selection import train_test_split


def drop_empty_rows(dataframe, column='text'):
    # If there is only '<BOS><EOS>' then it is considered empty
    drop_idx = dataframe[dataframe[column] == '<BOS><EOS>'].index
    dataframe.drop(drop_idx, inplace=True)
    dataframe.to_csv('data/data.csv', index=False)
    return dataframe


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


def clean(dataframe):
    dataframe = drop_empty_rows(dataframe)
    dataframe = deduplicate(dataframe)
    dataframe = filtering(dataframe)
    return dataframe


def extract_text(dataframe, path, column='text'):
    f = open(path, 'w')
    file = ''
    texts = dataframe[column].tolist()
    for text in texts:
        text = str(text).strip()
        file += text + '\n'
    f.write(file)


def split(dataset, ratio, directory=''):
    assert isclose(sum(ratio), 1)
    train_test_ratio = round(ratio[0] + ratio[1], 1)
    train_valid_ratio = ratio[0] / train_test_ratio
    train, test = train_test_split(dataset,
                                   train_size=train_test_ratio,
                                   random_state=69)
    train, valid = train_test_split(train,
                                    train_size=train_valid_ratio,
                                    random_state=69)
    extract_text(valid, f'{directory}valid.txt')
    extract_text(train, f'{directory}train.txt')
    extract_text(test, f'{directory}test.txt')


data = pd.read_csv('data/data.csv')
data = clean(data)
split(data, ratio=(0.7, 0.2, 0.1), directory='data/')
data.to_csv('data/data.csv', index=False)
