import shutil
import os
from pathlib import Path


class FileManager:

    @classmethod
    def dir_size(cls, path):
        size = 0
        for path, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(path, file)
                size += cls.file_size(file_path)
        return size

    @classmethod
    def str_size(cls, string):
        return len(string.encode())

    @classmethod
    def file_size(cls, path):
        return os.path.getsize(path)

    @staticmethod
    def ls():
        return '; '.join(os.listdir())

    def __init__(self, root, size=None):
        self._root = Path(root).resolve()
        if not self._root.is_dir():
            self.make_dir(self._root)
        os.chdir(self._root)
        self._size = size

    @property
    def root_size(self):
        return self.dir_size(self._root)

    def make_dir(self, path):
        path = self._get_path(path)
        if not path.exists():
            path.mkdir(parents=True)

    def make_file(self, path):
        path = self._get_path(path)
        if not path.exists():
            path.touch()

    def cd(self, path):
        path = self._get_path(path)
        if path.is_dir():
            os.chdir(path)

    def read(self, path):
        path = self._get_path(path)
        if path.is_file():
            return path.read_text()

    def delete(self, path):
        path = self._get_path(path)
        if path.is_dir():
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()

    def move(self, src_path, dst_path):
        src_path = self._get_path(src_path)
        dst_path = self._get_path(dst_path)
        if src_path.exists():
            shutil.move(src_path, dst_path)

    def pwd(self):
        path = str(Path.cwd().relative_to(self._root))
        path = path.replace('\\', '/').replace('.', '/')
        if path[0] != '/':
            path = '/' + path
        return path

    def enough(self, extra):
        if self._size and self.root_size + extra > self._size:
            return False
        return True

    def write(self, path, text):
        path = self._get_path(path)
        if path.is_file() and self.enough(self.str_size(text)):
            with open(path, 'w') as file:
                file.write(text)

    def copy(self, src_path, dst_path):
        src_path = self._get_path(src_path)
        dst_path = self._get_path(dst_path)
        if src_path.is_file() and self.enough(self.file_size(src_path)):
            shutil.copy(src_path, dst_path)
        elif src_path.is_dir() and self.enough(self.dir_size(src_path)):
            shutil.copytree(src_path, dst_path)

    def free(self):
        if self._size:
            free_size = self._size - self.root_size
            return f'Всего: {self._size}Б; Свободно: {free_size}Б'
        return 'Квотирование дискового простанство отключено'

    def _get_path(self, path):
        if isinstance(path, Path):
            str_path = str(path)
        else:
            str_path = path
        if str_path[0] == '/':
            path = Path(self._root, str_path[1:])
        elif str_path.find('..') != -1:
            path = Path()
            for path_part in Path(str_path).parts:
                resolved_path_part = Path(path_part).resolve()
                if (path_part == '..' and
                        resolved_path_part.is_relative_to(self._root)):
                    path = resolved_path_part
                elif path_part != '..':
                    path = path.joinpath(path_part)
                else:
                    path = self._root
        else:
            resolved_path = Path(str_path).resolve()
            if (resolved_path.is_absolute() and
                    resolved_path.relative_to(self._root)):
                path = Path(str_path).resolve()
            else:
                path = Path.cwd().joinpath(Path(str_path))
        return path
