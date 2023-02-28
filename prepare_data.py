import pandas as pd
from math import isclose
from sklearn.model_selection import train_test_split


def extract_text(df, path, column='text'):
    f = open(path, 'w')
    file = ''
    texts = df[column].tolist()
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
split(data, ratio=(0.7, 0.2, 0.1), directory='data/')
