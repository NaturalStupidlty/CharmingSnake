import os
import csv
import shutil
from subprocess import call


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
        self.dictList = []
        self.repos_file = None

    def scrap(self, repos_file, clone_folder='resources', max_file_size=1000000, extensions=None):
        """
        Scraps data of certain extensions, under certain max_file_size from file called repos to clone_folder.
        Then finds files and copy their data to json, so it could be saved to csv using save() method
        @param repos_file: a file name for file where each repository name separated with \n
        @param clone_folder: folder to clone repos to
        @param max_file_size: maximum file size in bites
        @param extensions: a list of file extensions to be considered
        @return:
        """
        if extensions is None:
            extensions = ['py']
        self.repos_file = repos_file
        with open(repos_file, 'r') as f:
            try:
                repos_names = f.readlines()
            except Exception as exception:
                print('DecoderError: ', repos_file)
                raise exception
        for repo_name in repos_names:
            self.__clone_repo(repo_name, clone_folder)
            files_path = self.__find_files(repo_name, clone_folder, max_file_size, extensions)
            self.__getFileContent(files_path)
            self.__remove_repo(repo_name, clone_folder)

    @staticmethod
    def __clone_repo(repo_name, clone_folder):
        """
        Clones repository called repo_name into clone_folder
        @param repo_name: name of a repository
        @param clone_folder: folder to copy repository to
        @return:
        """
        walking_dir = f'{clone_folder}/{"/".join(repo_name.strip().split("/")[-2:])}'
        call(['git', 'clone', repo_name.strip(), walking_dir])

    def __find_files(self, repo_name, clone_folder, max_file_size, extensions):
        """
        Method to find files path of certain extensions, under certain max_file_size
        in repository called repo_name in clone_folder.
        @param repo_name: name of a repository
        @param clone_folder: folder that repository had been cloned to
        @param max_file_size: maximum file size in bites
        @param extensions: a list of file extensions to be considered
        @return: a list of files path
        """
        files_path = []
        walking_dir = f'{clone_folder}/{"/".join(repo_name.strip().split("/")[-2:])}'
        for (current_path, folders, files) in os.walk(walking_dir):
            for file in files:
                size = os.path.getsize(self.repos_file)
                # Only files with certain extensions and under max_size
                if (file.split('.')[-1] in extensions) & (size < max_file_size):
                    files_path.append(os.path.join(current_path, file))
        return files_path

    def __getFileContent(self, files_path):
        """
        Read data from files in at files_path into list of dictionaries
        @return:
        """
        for path in files_path:
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
                self.dictList.append({self.fieldnames[0]: data,
                                      self.fieldnames[1]: repo_name,
                                      self.fieldnames[2]: file_path})

    @staticmethod
    def __remove_repo(repo_name, clone_folder):
        """
        Removes repository called repo_name from clone_folder
        @param repo_name: name of a repository
        @param clone_folder: folder to remove repository from
        """
        walking_dir = f'{clone_folder}/{"/".join(repo_name.strip().split("/")[-2:])}'
        shutil.rmtree(walking_dir)

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
                for data in self.dictList:
                    writer.writerow(data)
        except Exception as exception:
            print(f"Error writing to file: {str(exception)}")
            raise exception


scrapper = Scrapper()
scrapper.scrap('repos.txt')
scrapper.save('data/data.csv')
