# -*- coding: utf-8 -*-
"""Salsa

Usage:
    salsa list
    salsa show <name>
    salsa mount <name>
    salsa unmount <name>
    salsa add
    salsa edit <name>
    salsa delete <name>

Options:
    -h --help       Show this screen
    -v --version    Show current version
"""


from docopt import docopt
from core import ColoredOutput
from salsa.exceptions import SalsaException, SalsaConnectionException


class Cli(object):
    def __init__(self, salsa):
        self.salsa = salsa
        args = docopt(__doc__, version="Salsa 1.0.0")

        fn = 'do_' + [arg for arg in args if args[arg] is True].pop()

        try:
            if (fn in ('do_list', 'do_add')):
                success = getattr(salsa, fn)()
            else:
                success = getattr(salsa, fn)(args['<name>'])

            if success is not None:
                ColoredOutput().success(success)
        except SalsaConnectionException, err:
            ColoredOutput().error("\t%s" % str(err))
        except SalsaException, err:
            ColoredOutput().error("\t%s" % str(err))
        except Exception, err:
            ColoredOutput().error(
                "\t Something went wrong!!\n\t << %s >>" % err)
        except KeyboardInterrupt:
            pass
