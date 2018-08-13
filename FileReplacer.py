#!/usr/bin/python

import sys
import subprocess as sh
import os.path

from optget.GetOpt import *
from fileinfo.FileMap import find_file
from FilePermissionChanger import handle_change_opt


class FileReplacer(object):
    @staticmethod
    def form_backup_file(origin_file):
        return "%s.bakByEkko" % origin_file

    @staticmethod
    def backup_target_file(target, force_backup=False):
        if not os.path.exists(target):
            print "  Old file not existed. Skipping backup."
            return

        backup_file = FileReplacer.form_backup_file(target)
        if not force_backup and os.path.exists(backup_file):
            """ Backup file existed. Skipping. """
            return

        result = sh.call(['cp', '-f', target, backup_file])
        if result != 0:
            print "  Failed on action \'backup_target_file\' for %s. Skipping backup." % target

    @staticmethod
    def recover_backup_file(target):
        backup_file = FileReplacer.form_backup_file(target)

        if not os.path.exists(backup_file):
            print "  Backup file not existed (Maybe it is a new file?). Skipping recover."
            return

        result = sh.call(['mv', '-f', backup_file, target])
        if result != 0:
            raise RuntimeError("action \'recover_backup_file\'")

    @staticmethod
    def change_permission(file):
        handle_change_opt(['-f', file.target, '-o', file.owner, '-m', file.mod])

    @staticmethod
    def get_corresponding_file(filename):
        file = find_file(filename)
        if file is None:
            raise RuntimeError("Given file \"%s\" is NOT in maps." % (filename))
        return file


class FilePathReplacer(FileReplacer):
    @staticmethod
    def move_file_with_backup(source, target):
        FileReplacer.backup_target_file(target)

        result = sh.call(['mv', source, target])
        if result != 0:
                raise RuntimeError("action \'move_file_with_backup\'")

    @staticmethod
    def get_filename(file_path):
        return os.path.basename(file_path)

    @classmethod
    def replace(self, file_path):
        filename = self.get_filename(file_path)
        file = self.get_corresponding_file(filename)

        self.move_file_with_backup(file_path, file.target)
        self.change_permission(file)

        return file

    @classmethod
    def recover(self, file_path):
        filename = self.get_filename(file_path)
        file = self.get_corresponding_file(filename)

        self.recover_backup_file(file.target)
        self.change_permission(file)


class FilenameReplacer(FileReplacer):
    @staticmethod
    def copy_file_with_backup(source, target):
        FileReplacer.backup_target_file(target)

        result = sh.call(['cp', '-f', source, target])
        if result != 0:
            raise RuntimeError("action \'copy_file_with_backup\'")

    @classmethod
    def replace(self, filename):
        file = self.get_corresponding_file(filename)

        self.copy_file_with_backup(file.default_source, file.target)
        self.change_permission(file)

        return file

    @classmethod
    def recover(self, filename):
        file = self.get_corresponding_file(filename)

        self.recover_backup_file(file.target)
        self.change_permission(file)


class _MyOptGetter(OptGetter):
    def __init__(self):
        options = "hf:p:r"
        help_message = "usage: FileReplacer [-h] [-f FILENAME / -p FILE_PATH] [-r]"
        help_message += "\n    h: help"
        help_message += "\n    f/p: object to replace, listed by priority"
        help_message += "\n       f: Copy file from corresponding default source of given filename."
        help_message += "\n       p: Copy file from given file path."
        help_message += "\n    r: recover backup object"
        super(_MyOptGetter, self).__init__(options=options, help_message=help_message)


def _get_corresponding_replacer(options):
    """
    Determine replacer and target corresponding to given target type.
    """
    filename = options.get('-f', None)
    file_path = options.get('-p', None)

    if filename is not None:
        return FilenameReplacer(), filename
    elif file_path is not None:
        return FilePathReplacer(), file_path
    else:
        raise RuntimeError()


def handle_replacement_opt(argv):
    opt_getter = _MyOptGetter()

    try:
        options, arguments = opt_getter.get(argv, options_in_dict=True)
    except (OptHelpError, OptInvalidError) as e:
        raise RuntimeError(e)

    try:
        replacer, target = _get_corresponding_replacer(options)
    except RuntimeError:
        raise RuntimeError("Insufficient parameters. Do nothing.")

    if '-r' in options:
        file = replacer.recover(target)
    else:
        file = replacer.replace(target)
    print "Done: [%s]." % file.target


def main(argv):
    """
    Replace file from dev-file to test-machine. With proper permission.
    >>> handle_replacement_opt(["-p", "/volume1/dltarget/download.js"])  # doctest: +SKIP
    >>> handle_replacement_opt(["-f", "download.js" "-r"])  # doctest: +SKIP

    Run doctest
    >>> main(["test"])  # doctest: +SKIP
    """
    if (len(argv) >= 1) and (argv[0] == "test"):
        import doctest
        doctest.testmod(report=True)
        print "Complete doctest."
        return

    try:
        handle_replacement_opt(argv)
    except Exception as e:
        print str(e)
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
