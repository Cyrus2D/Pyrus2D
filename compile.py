from distutils.core import setup
from distutils.extension import Extension
from os import listdir
from os.path import isdir
from shutil import move

from Cython.Distutils import build_ext


class Src:
    def __init__(self, dir=None, name=None, ext=None):
        self.dir = dir
        self.name = name
        self.ext = ext

    def full_path(self):
        return f"{self.dir}/{self.name}.{self.ext}"

    def so(self):
        return f"{self.name}.cpython-36m-x86_64-linux-gnu.so"

    def __repr__(self):
        return self.full_path()

    def is_python(self):
        if self.ext == "py":
            return True
        return False

    def is_compiled(self):
        if self.ext == "so" or self.ext == "c":
            return True
        return False


def make_file_list(dir='.'):
    lst = []
    for file_dir in listdir(dir):
        if file_dir[0] == '.' or file_dir == 'compile.py':
            continue

        new_dir = dir + '/' + file_dir
        file_splt = file_dir.split('.')
        src = Src(dir, '.'.join(file_splt[:-1]), file_splt[-1])
        if isdir(new_dir):
            lst += make_file_list(new_dir)
        else:
            if src.is_python():
                lst.append(src)
    return lst


def move_files(files):
    for file in files:
        print(file.so(), file.dir)
        move(file.so(), file.dir)


def main():
    files = make_file_list()

    # ext_modules = []
    # for file in files:
    #     print(file,'\t',file[:-3].split('/')[-1])
    #     ext_modules.append(Extension(file[:-3], [file]))
    ext_modules = [Extension(file.name, [file.full_path()]) for file in files]

    setup(
        name='My Program Name',
        cmdclass={'build_ext': build_ext},
        ext_modules=ext_modules
    )

    move_files(files)


if __name__ == '__main__':
    main()
