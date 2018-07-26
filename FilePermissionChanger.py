#!/usr/bin/python

import sys
from optget.GetOpt import *
import subprocess as sh


def change_owner(file, owner):
    """
    Change file owner(user:group).
    >>> change_owner("./Ekko", "1024:root")  # doctest: +SKIP
    """
    result = sh.call(["chown", owner, file])
    if result != 0:
        raise RuntimeError("action \'change_owner\'")


def change_mod(file, mod):
    """
    Change file mod.
    >>> change_mod("./Ekko", "755")  # doctest: +SKIP
    >>> change_mod("./Ekko", 317)  # doctest: +SKIP
    """
    result = sh.call(["chmod", str(mod), file])
    if result != 0:
        raise RuntimeError("action \'change_mod\'")


class _MyOptGetter(OptGetter):
    def __init__(self):
        options = "hf:o:m:"
        help_message = "usage: FilePermissionChanger [-h] [-f FILE_PATH] [-o OWNER] [-m MOD]"
        super(_MyOptGetter, self).__init__(options=options, help_message=help_message)


def handle_change_opt(argv):
    opt_getter = _MyOptGetter()

    try:
        opts, args = opt_getter.get(argv)
    except (OptHelpError, OptInvalidError) as e:
        raise RuntimeError(e)

    if (len(opts) <= 1) or (opts[0][0] != '-f'):
        raise RuntimeError("Insufficient parameters. Do nothing.")

    file_path = opts[0][1]
    try:
        for opt, arg in opts[1:]:
            if opt == '-o':
                change_owner(file_path, arg)
            elif opt == '-m':
                change_mod(file_path, arg)
            else:
                pass
    except RuntimeError as e:
        raise RuntimeError("RuntimeError on %s" % str(e))


def main(argv):
    """
    Change file's permission.
    >>> handle_change_opt(["-f", "file", "-o", "root:root", "-m", "755"])  # doctest: +SKIP

    Run doctest
    >>> main(["test"])  # doctest: +SKIP
    """
    if (len(argv) >= 1) and (argv[0] == "test"):
        import doctest
        doctest.testmod(report=True)
        print "Complete doctest."
        return

    try:
        handle_change_opt(argv)
    except Exception as e:
        print str(e)
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
