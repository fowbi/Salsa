# -*- coding: utf-8 -*-


import yaml
import pexpect
import os

from core import which
from salsa.exceptions import SalsaException, SalsaConnectionException


class Config(object):
    """
        Configuration for samba share
    """

    _base_mp_directory = ''
    _default_mp_directory = 'share'

    def __init__(self, config_file=None):
        if not config_file:
            config_file = self.get_default_salsa_config()

        self.config_file = os.path.abspath(config_file)

        if not os.path.exists(self.config_file):
            if not os.path.exists(os.path.dirname(self.config_file)):
                os.makedirs(os.path.dirname(self.config_file))
            open(self.config_file, 'w+').close()

        self.shares = []
        self.base_mp_directory = self.get_system_based_base_mp_directory()

    def get_default_salsa_config(self):
        """
            Get default salsa_config location
        """
        return os.path.expanduser('~/.salsa_config')

    def load(self):
        """
            Load share list from configuration file
        """
        self.shares = []
        doc = yaml.load(open(self.config_file, 'r'))

        if not doc:  # Write new configuration file.
            self.write()
            return

        write_doc = False
        if 'base_mp_directory' in doc and doc['base_mp_directory']:
            self.base_mp_directory = doc['base_mp_directory']
        else:
            write_doc = True

        if 'default_mp_directory' in doc:
            self.default_mp_directory = doc['default_mp_directory']
        else:
            write_doc = True

        if 'shares' in doc:
            for share in doc['shares']:
                ss = Salsa_Share(share['name'], share['server'])
                ss.username = share['username']
                ss.password = share['password'] if share['password'] is not None else ''
                ss.share = share['share']
                ss.mount_point = share['mount_point']
                self.shares.append(ss)

        if write_doc:
            self.write()

    @property
    def base_mp_directory(self):
        "Getter for base_mp_directory"
        return self._base_mp_directory

    @base_mp_directory.setter
    def base_mp_directory(self, directory):
        """
            Setter for base_mp_directory
            Falls back to a system based directory.
        """
        if not directory:
            directory = self.get_system_based_base_mp_directory()
        self._base_mp_directory = directory

    @property
    def default_mp_directory(self):
        "Getter for default_mp_directory"
        return self._default_mp_directory

    @default_mp_directory.setter
    def default_mp_directory(self, directory):
        """
            Setter for default_mp_directory
            Falls back to 'share' if none given
        """
        if not directory:
            directory = 'share'
        self._default_mp_directory = directory

    def get_system_based_base_mp_directory(self):
        if os.name.lower() == 'linux':
            return '/mnt/'
        else:
            return '/Volumes/'

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

        doc_ = [{
            'base_mp_directory': self.base_mp_directory,
            'default_mp_directory': self.default_mp_directory,
            'shares': dict_list
        }]
        #print doc_

        yaml.dump_all(doc_, open(self.config_file, 'w'),
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
        slash_server_path = os.path.join("/", self.share)
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
        if not os.path.exists(self.mount_point):
            os.makedirs(self.mount_point)

        if not os.path.isdir(self.mount_point):
            raise Exception("Directory \"%s\" was not found/not created" % self.mount_point)

    def post_mount(self):
        "Define operations after mounting the samba share"
        pass

    def mount(self):
        "Mount samba share to designated mount point"
        mount_bin = which("mount_smbfs")
        slash_server_path = os.path.join("/", self.share)
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
        if os.path.isdir(self.mount_point) and not os.listdir(self.mount_point):
            os.rmdir(self.mount_point)

    def umount(self):
        "Unmount the samba share from its mount point"
        umount_bin = which("umount")
        cmd = "%s %s" % (umount_bin, self.mount_point)
        (output, returncode) = pexpect.run(cmd, withexitstatus=1, timeout=5)

        if returncode != 0:
            raise SalsaConnectionException("Could not umount %s\n\t<< %s >>" %
                            (self.mount_point, output))

#if __name__ == "__main__":
