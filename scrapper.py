import os
import csv
from subprocess import call


def clone_repos(repos, clone_folder):
    """
    Clones repositories from repos file into clone_folder
    @param repos: a file with each name separated with \n
    @param clone_folder: folder to copy repos to
    @return:
    """
    with open(repos, 'r') as f:
        try:
            lines = f.readlines()
        except Exception as exception:
            print('DecoderError: ', repos)
            raise exception
    for line in lines:
        walking_dir = f'{clone_folder}/{"/".join(line.strip().split("/")[-2:])}'
        call(['git', 'clone', line.strip(), walking_dir])


class Scrapper:
    def __init__(self, bos_token='<BOS>', eos_token='<EOS>'):
        """
        Initialises required fields, including bos_token and eos_token.
        @param bos_token: token to mark beginning of a sentence
        @param eos_token: token to mark end of a sentence
        """
        self.bos_token = bos_token
        self.eos_token = eos_token
        self.fieldnames = ['text', 'repo_name', 'path']
        self.files_path = []
        self.json = []

    def scrap(self, repos, clone_folder='resources', max_file_size=1000000, extensions=None):
        """
        Scraps data of certain extensions, under certain max_file_size from repos to clone_folder.
        Then find files and copy their data to json, so it could be saved to csv using save() method
        @param repos: a file with each name separated with \n
        @param clone_folder: folder to clone repos to
        @param max_file_size: maximum file size in bites
        @param extensions: a list of file extensions to be considered
        @return:
        """
        if extensions is None:
            extensions = ['py']
        clone_repos(repos, clone_folder)
        self.__find_files(repos, clone_folder, max_file_size, extensions)
        self.__jsonify()

    def save(self, path):
        """
        Saves scrapped repositories to dataframe (.csv) at a given path.
        Should probably be used after scrap() method had been called.
        @param path: path to save dataframe, like 'data/my_dataframe.csv'
        @return:
        """
        try:
            with open(path, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
                writer.writeheader()
                for data in self.json:
                    writer.writerow(data)
        except Exception as exception:
            print(f"Error writing to file: {str(exception)}")
            raise exception

    def __find_files(self, repos, clone_folder, max_file_size, extensions):
        """
        Method to find files of certain extensions, under certain max_file_size from repos in clone_folder.
        @param repos: a python list with repos' names
        @param clone_folder: folder that repos had been cloned to
        @param max_file_size: maximum file size in bites
        @param extensions: a list of file extensions to be considered
        @return:
        """
        with open(repos, 'r') as f:
            try:
                lines = f.readlines()
            except Exception as exception:
                print('DecoderError: ', repos)
                raise exception
        for line in lines:
            walking_dir = f'{clone_folder}/{"/".join(line.strip().split("/")[-2:])}'
            for (current_path, folders, files) in os.walk(walking_dir):
                for file in files:
                    size = os.path.getsize(repos)
                    # Only files with certain extensions and under max_size
                    if (file.split('.')[-1] in extensions) & (size < max_file_size):
                        self.files_path.append(os.path.join(current_path, file))

    def __jsonify(self):
        """
        Read data from files in self.files_path into json format.
        @return:
        """
        for path in self.files_path:
            with open(path, 'r') as f:
                try:
                    content = f.readlines()
                except UnicodeDecodeError:
                    print('DecoderError: ', path)
                    continue
                summary = ''.join(content)
                summary = str(summary).strip()
                data = self.bos_token + summary + self.eos_token
                repo_name = '/'.join(path.split('/')[1:3])
                file_path = '/'.join(path.split('/')[3:])
                self.json.append({self.fieldnames[0]: data,
                                  self.fieldnames[1]: repo_name,
                                  self.fieldnames[2]: file_path})


scrapper = Scrapper()
scrapper.scrap('repos.txt')
scrapper.save('data/data.csv')
