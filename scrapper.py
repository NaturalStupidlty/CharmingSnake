import math
import os
import csv
from subprocess import call


def clone_repos(path, save_dir='resources'):
    with open(path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        walking_dir = f'{save_dir}/{line.strip().split("/")[-1]}'
        call(['git', 'clone', line.strip(), walking_dir])


def find_files(path, save_dir='resources', extension='.py'):
    with open(path, 'r') as f:
        lines = f.readlines()
    total_files = []
    for line in lines:
        walking_dir = f'{save_dir}/{line.strip().split("/")[-1]}'
        for (current_path, folders, files) in os.walk(walking_dir):
            for file in files:
                if file[-3:] == extension:
                    total_files.append(os.path.join(current_path, file))
    return total_files


def jsonify(files, bos_token='<BOS>', eos_token='<EOS>'):
    json = []
    for file in files:
        with open(file, 'r') as f:
            try:
                content = f.readlines()
            except UnicodeDecodeError:
                print('DecoderError: ', file)
            summary = ''.join(content)
            summary = str(summary).strip()
            data = bos_token + summary + eos_token
            json.append({'text': data})
    return json


def json_to_csv(json, path, fieldnames=None):
    if fieldnames is None:
        fieldnames = ['text']
    with open(path, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data in json:
            writer.writerow(data)


def save_json_data(json, split=0.9):
    train_size = math.ceil(len(json) * split)
    json_to_csv(json, 'data/data.csv')
    json_to_csv(json[:train_size], 'data/train.csv')
    json_to_csv(json[train_size:], 'data/test.csv')


clone_repos('repos.txt')
files_list = find_files('repos.txt')
json_data = jsonify(files_list)
save_json_data(json_data)
