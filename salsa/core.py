from os.path import exists, split, join
from os import access, environ, pathsep, X_OK

def which(program):
    """
        from http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/377028#377028
    """
    def is_exe(fpath):
        return exists(fpath) and access(fpath, X_OK)

    fpath, fname = split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in environ["PATH"].split(pathsep):
            exe_file = join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None
