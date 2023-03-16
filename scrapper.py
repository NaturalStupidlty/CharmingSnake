import os
import csv
from subprocess import call


def clone_repos(repos, clone_folder):
    with open(repos, 'r') as f:
        lines = f.readlines()
    for line in lines:
        walking_dir = f'{clone_folder}/{"/".join(line.strip().split("/")[-2:])}'
        call(['git', 'clone', line.strip(), walking_dir])


class Scrapper:
    def __init__(self, bos_token='<BOS>', eos_token='<EOS>'):
        self.bos_token = bos_token
        self.eos_token = eos_token
        self.fieldnames = ['text', 'repo_name', 'path']
        self.files_path = []
        self.json = []

    def scrap(self, repos, clone_folder='resources', max_file_size=1000000, extensions=None):
        if extensions is None:
            extensions = ['py']
        clone_repos(repos, clone_folder)
        self.__find_files(repos, clone_folder, max_file_size, extensions)
        self.__jsonify()

    def save(self, path):
        self.__json_to_csv(path)

    def __find_files(self, repos, clone_folder, max_file_size, extensions):
        with open(repos, 'r') as f:
            lines = f.readlines()
        for line in lines:
            walking_dir = f'{clone_folder}/{"/".join(line.strip().split("/")[-2:])}'
            for (current_path, folders, files) in os.walk(walking_dir):
                for file in files:
                    size = os.path.getsize(repos)
                    # Only files with certain extensions and under max_size
                    if (file.split('.')[-1] in extensions) & (size < max_file_size):
                        self.files_path.append(os.path.join(current_path, file))

    def __jsonify(self):
        for path in self.files_path:
            with open(path, 'r') as f:
                try:
                    content = f.readlines()
                except UnicodeDecodeError:
                    print('DecoderError: ', path)
                summary = ''.join(content)
                summary = str(summary).strip()
                data = self.bos_token + summary + self.eos_token
                repo_name = '/'.join(path.split('/')[1:3])
                file_path = '/'.join(path.split('/')[3:])
                self.json.append({self.fieldnames[0]: data,
                                  self.fieldnames[1]: repo_name,
                                  self.fieldnames[2]: file_path})

    def __json_to_csv(self, path):
        with open(path, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
            writer.writeheader()
            for data in self.json:
                writer.writerow(data)


scrapper = Scrapper()
scrapper.scrap('repos.txt')
scrapper.save('data/data.csv')
