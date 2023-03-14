import pandas as pd
from math import isclose
from sklearn.model_selection import train_test_split


def extract_text(dataframe, path, column='text'):
    f = open(path, 'w')
    file = ''
    texts = dataframe[column].tolist()
    for text in texts:
        text = str(text).strip()
        file += text + '\n'
    f.write(file)


def drop_empty_rows(dataframe):
    drop_idx = dataframe[dataframe['text'] == '<BOS><EOS>'].index
    dataframe.drop(drop_idx, inplace=True)
    dataframe.to_csv('data/data.csv', index=False)
    return dataframe


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
data = drop_empty_rows(data)
split(data, ratio=(0.7, 0.2, 0.1), directory='data/')
