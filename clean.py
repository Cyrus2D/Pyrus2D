from os import listdir, remove
from os.path import isdir
from shutil import rmtree

from compile import Src


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
            if src.is_compiled():
                lst.append(src)
    return lst


def main():
    binarys = make_file_list()
    for binary in binarys:
        remove(binary.full_path())
    try:
        rmtree("./build")
    except:
        print("build directory not found")
    try:
        rmtree("./binary")
    except:
        print("binary directory not found")
    finally:
        print("All binarys deleted :)")


if __name__ == '__main__':
    main()
