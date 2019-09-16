from os import listdir, remove
from os.path import isdir
from shutil import rmtree
import sys

from compile import Src


def make_file_list(dir='.', c_mode=False):
    lst = []
    for file_dir in listdir(dir):
        if file_dir[0] == '.' or file_dir == 'compile.py':
            continue

        new_dir = dir + '/' + file_dir
        file_splt = file_dir.split('.')
        src = Src(dir, '.'.join(file_splt[:-1]), file_splt[-1])
        if isdir(new_dir):
            lst += make_file_list(new_dir, c_mode)
        else:
            if not c_mode:
                if src.is_compiled():
                    lst.append(src)
            else:
                if src.is_cfile():
                    lst.append(src)
    return lst


def clean_everything():
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


def clean_c_files():
    c_files = make_file_list(c_mode=True)
    for c_file in c_files:
        remove(c_file.full_path())
    try:
        rmtree("./build")
    except:
        print("build directory not found")
    finally:
        print("All c files deleted :)")


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1 and args[1] == 'c-files':
        clean_c_files()
    else:
        clean_everything()
