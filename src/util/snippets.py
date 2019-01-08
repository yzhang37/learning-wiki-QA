__all__ = ['CalledProcessError', 'unzip_dict', 'get_file_lines_quick']
import subprocess
import os

CalledProcessError = subprocess.CalledProcessError


def unzip_dict(fs: dict, *args):
    ret = []
    for key in args:
        ret.append(fs[key])
    return ret


def get_file_lines_quick(file_name: str):
    if not os.path.exists(file_name):
        raise FileNotFoundError("{0} not exists.".format(file_name))
    if not os.path.isfile(file_name):
        raise TypeError("{0} is not a file".format(file_name))
    return int(subprocess.check_output(['wc', '-l', file_name]).strip().split()[0])
