import sys

from salsa_config import Config
from salsa_config import Salsa_Share
from cli import cli

class Salsa(object):
    def __init__(self, config_file=None):
        self.config_file = Config(config_file)
        self.config_file.load()

    def add_share(self):
        name = raw_input("Name: ")
        while name == '':
            print "Pls fill in a name kthxbai"
            name = raw_input("Name: ")

        server = raw_input("Server: ")
        while server == '':
            print "Pls fill in a server kthxbai"
            server = raw_input("Server: ")

        ss = Salsa_Share(name, server)

        ss.username = raw_input("Username: ")
        password = raw_input("Password: ")
        rp_password = raw_input("Repeat Password: ")
        while (password != rp_password):
            print "Passwords didn't match, pls retry kthxbai"
            password = raw_input("Password: ")
            rp_password = raw_input("Repeat Password: ")

        ss.password = password
        ss.share = raw_input("Folder: ")
        mount_point = raw_input("Mount Point: ")
        if (mount_point == ''):
            mount_point = ss.name

        ss.mount_point = "/Volumes/" + mount_point

        self.config_file.add_share(ss)

        print "Share ", name, "was added"

    def delete_share(self, name):
        self.config_file.delete_share(name)
        print "Share ", name, "was deleted"

    def edit_share(self, name):
        ss = self.config_file.lookup_share(name)

        new_name = raw_input("Name:[" + ss.name + "] ")
        if new_name == '':
            new_name = ss.name

        server = raw_input("Server: [" + ss.server + "]")
        if server == '':
            server = ss.server

        ss_ = Salsa_Share(new_name, server)

        ss_.username = raw_input("Username: [" + ss.username + "]")
        if ss_.username == '':
            ss_.username = ss.username

        password = raw_input("Password: ")
        rp_password = raw_input("Repeat Password: ")
        while (password != rp_password):
            print "Passwords didn't match, pls retry kthxbai"
            password = raw_input("Password: ")
            rp_password = raw_input("Repeat Password: ")

        ss_.password = password

        ss_.share = raw_input("Folder: [" + ss.share + "]")
        if ss_.share == '':
            ss_.share = ss.share

        ss_.mount_point = raw_input("Mount Point: [" + ss.mount_point + "]")
        if ss_.mount_point == '':
            ss_.mount_point = ss.mount_point

        ss_.mount_point = "/Volumes/" + ss_.mount_point
        self.config_file.edit_share(name, ss_)

        print name, "was edited!"

    def list_shares(self):
        self.config_file.list_shares()

    def show_share_details(self, name):
        self.config_file.show_share_details(name)

    def mount_share(self, name):
        self.config_file.mount_share(name)

    def umount_share(self, name):
        self.config_file.umount_share(name)


salsa_ = Salsa()
cli_ = cli(salsa_)
