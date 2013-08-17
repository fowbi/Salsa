# -*- coding: utf-8 -*-


from os.path import exists, split, join
from os import access, environ, pathsep, X_OK
from termcolor import colored


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


class UserInput(object):
    def __init__(self, question):
        self.question = question
        self.variable = ""

    def get(self):
        self.variable = raw_input(self.question)

        return self


class MandatoryUserInput(UserInput):
    def get(self):
        UserInput.get(self)
        while self.variable == '':
            print "Pls fill in something!"
            self.get()

        return self


class OptionalUserInput(UserInput):
    def __init__(self, question, default=""):
        UserInput.__init__(self, question)
        self.default = default

    def get(self):
        UserInput.get(self)
        if self.variable == '':
            self.variable = self.default

        return self


class ColoredOutput(object):
    "Colorize the output"
    def error(self, message):
        "Print colored error message"
        text = colored("ERROR :: ", 'red', attrs=['bold'])
        text += colored("\n" + message, 'red')
        print text

    def success(self, message):
        "Print colored success message"
        text = colored("SUCCESS :: ", 'green', attrs=['bold'])
        text += colored("\n" + message, 'green')
        print text
