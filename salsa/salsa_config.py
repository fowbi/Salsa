# -*- coding: utf-8 -*-


import yaml
import pexpect

from os.path import exists, dirname, join, isdir, expanduser
from os import listdir, rmdir, makedirs
from core import which
from exceptions import SalsaException, SalsaConnectionException


class Config(object):
    """
        Configuration for samba share
    """
    def __init__(self, config_file=None):
        if not config_file:
            config_file = self.get_default_salsa_config()

        self.config_file = config_file

        if not exists(self.config_file):
            if not exists(dirname(self.config_file)):
                makedirs(dirname(self.config_file))
            open(self.config_file, 'w+').close()

        self.shares = []

    def get_default_salsa_config(self):
        """
            Get default salsa_config location
        """
        return expanduser('~/.salsa_config')

    def load(self):
        """
            Load share list from configuration file
        """
        self.shares = []
        docs = yaml.load_all(open(self.config_file, 'r'))

        for doc in docs:
            ss = Salsa_Share(doc['name'], doc['server'])
            ss.username = doc['username']
            ss.password = doc['password'] if doc['password'] is not None else ''
            ss.share = doc['share']
            ss.mount_point = doc['mount_point']

            self.shares.append(ss)

    def write(self):
        """
            Write share list to configuration file
        """
        dict_list = []
        for share in self.shares:
            # Fallback to guest login when username is empty
            if (share.username == ''):
                share.username = 'guest'
                share.password = ''

            dict_list.append(share.__dict__)

        yaml.dump_all(dict_list, open(self.config_file, 'w'),
                      default_flow_style=False)

    def add_share(self, salsa_share):
        """
            Add new samba share to the configuration file
        """
        if not self.is_duplicate_share(salsa_share):
            self.shares.append(salsa_share)
            self.write()
        else:
            raise SalsaException("A share with the name \"%s\" already exists!" % salsa_share.name)

    def delete_share(self, name):
        """
            Delete share by given name
        """
        self.lookup_share(name)  # Check if share exists.

        # Build new list excluding the share to delete.
        self.shares = [share for share in self.shares if share.name != name]
        self.write()

    def edit_share(self, name, salsa_share):
        """
            Edit samba share by given name
        """
        share = self.lookup_share(name)

        share.name = salsa_share.name
        share.username = salsa_share.username
        share.password = salsa_share.password
        share.share = salsa_share.share
        share.mount_point = salsa_share.mount_point
        self.write()

    def list_shares(self):
        """
            List all samba share from the loaded configuration file
        """
        for share in self.shares:
            print share

    def show_share_details(self, name):
        "Show samba share details by given name"
        print self.lookup_share(name)

    def mount_share(self, name):
        """
            Mount samba share by given name
        """
        share = self.lookup_share(name)
        share.pre_mount()
        share.mount()
        share.post_mount()

    def umount_share(self, name):
        """
            Unmount samba share by given name
        """
        share = self.lookup_share(name)
        share.pre_umount()
        share.umount()
        share.post_umount()

    def is_duplicate_share(self, salsa_share):
        """
            Check if given samba share is already listed in the configuration file.
        """
        try:
            self.lookup_share(salsa_share.name)
            return True
        except SalsaException:
            return False

    def lookup_share(self, name):
        """
            Check if share with given name exists
            Raises SalsaException if it does not find anything.
        """

        share_ = [share for share in self.shares if share.name == name]
        if not share_:
            raise SalsaException("A share with the name \"%s\" was not found!" % name)

        return share_.pop()


class Salsa_Share(object):
    """
        Main Salsa object containing everything needed to connect to a samba share
    """

    username = "guest"
    password = ""
    share = ""
    mount_point = ""

    def __init__(self, name, server):
        self.name = name
        self.server = server

    def can_connect(self):
        "Test samba connection"
        try:
            self.pre_mount()
            self.mount()
            self.post_mount()
            self.pre_umount()
            self.umount()
            self.post_umount()
            return True
        except SalsaConnectionException:
            self.post_umount()
            return False

    def __repr__(self):
        "Custom representation of samba share"
        slash_server_path = join("/", self.share)
        cmd = "//%s:%s@%s%s %s"
        cmd = cmd % (
            self.username,
            self.password,
            self.server,
            slash_server_path,
            self.mount_point)

        return self.name + "\n\t" + cmd

    def pre_mount(self):
        "Define operations before mounting the samba share"
        # Create mount point directory
        if not exists(self.mount_point):
            makedirs(self.mount_point)

        if not isdir(self.mount_point):
            raise Exception("Directory \"%s\" was not found/not created" % self.mount_point)

    def post_mount(self):
        "Define operations after mounting the samba share"
        pass

    def mount(self):
        "Mount samba share to designated mount point"
        mount_bin = which("mount_smbfs")
        slash_server_path = join("/", self.share)
        cmd = "%s //%s:%s@%s%s %s"
        cmd = cmd % (
            mount_bin,
            self.username,
            self.password,
            self.server,
            slash_server_path,
            self.mount_point)
        (output, returncode) = pexpect.run(cmd, withexitstatus=1, timeout=5)

        if returncode != 0:
            raise SalsaConnectionException("Could not mount %s%s\n\t<< %s >>" % (
                self.server, slash_server_path, output))

    def pre_umount(self):
        "Define operations before unmounting the samba share"
        pass

    def post_umount(self):
        "Define operations after unmounting the samba share"
        if isdir(self.mount_point) and not listdir(self.mount_point):
            rmdir(self.mount_point)

    def umount(self):
        "Unmount the samba share from its mount point"
        umount_bin = which("umount")
        cmd = "%s %s" % (umount_bin, self.mount_point)
        (output, returncode) = pexpect.run(cmd, withexitstatus=1, timeout=5)

        if returncode != 0:
            raise SalsaConnectionException("Could not umount %s\n\t<< %s >>" %
                            (self.mount_point, output))
