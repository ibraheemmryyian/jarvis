import os

class IO:
    @staticmethod
    def read_file(file_path):
        with open(file_path, "r") as f:
            return f.read()

    @staticmethod
    def write_file(file_path, content):
        with open(file_path, "w") as f:
            f.write(content)

    @staticmethod
    def list_files(directory):
        return os.listdir(directory)