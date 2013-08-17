# -*- coding: utf-8 -*-


from salsa_config import Config
from salsa_config import Salsa_Share
from core import MandatoryUserInput, OptionalUserInput, ColoredOutput
from termcolor import colored, cprint
from exceptions import SalsaException


class Salsa(object):
    """
    Initializes salsa config file
    and delegates functionality to Salsa class
    """

    def __init__(self, config_file=None):
        self.config_file = Config(config_file)
        self.config_file.load()

    def add_share(self):
        "Add new samba share to configuration."
        name = MandatoryUserInput("Name: ").get().variable
        server = MandatoryUserInput("Server: ").get().variable
        ss = Salsa_Share(name, server)

        ss.username = OptionalUserInput("Username: ").get().variable
        password = OptionalUserInput("Password: ").get().variable
        rp_password = OptionalUserInput("Repeat Password: ").get().variable
        while (password != rp_password):
            print "Passwords didn't match, pls retry kthxbai"
            password = OptionalUserInput("Password: ").get().variable
            rp_password = OptionalUserInput("Repeat Password: ").get().variable

        ss.password = password
        ss.share = OptionalUserInput("Folder: ").get().variable
        mount_point = OptionalUserInput("Mount Point: ").get().variable
        if (mount_point == ''):
            mount_point = ss.name

        # TODO mount_point should default to DEFAULT_MOUNT_POINT if none given
        ss.mount_point = mount_point

        test = OptionalUserInput("Test connection before saving?: [Y/n] ", 'Y').get().variable
        if test.upper() == 'Y':
            if not ss.can_connect():
                # TODO define what failed...
                proceed = OptionalUserInput("Connection failed! Proceed anyway?: [y/N] ", 'N').get().variable
                if proceed.upper() == 'N':
                    return

        self.config_file.add_share(ss)

        return ss.name

    def delete_share(self, name):
        "Delete samba share based on given name."
        self.config_file.lookup_share(name)  # Check if share exists.

        confirm = OptionalUserInput("Are you sure you want to delete %s?: [Y/n] " % name, 'Y').get().variable
        if confirm.upper() == 'Y':
            self.config_file.delete_share(name)

    def edit_share(self, name):
        "Edit samba share based on given name"
        ss = self.config_file.lookup_share(name)

        ui_new_name = OptionalUserInput("Name: [%s] " % ss.name, ss.name)
        new_name = ui_new_name.get().variable

        ui_server = OptionalUserInput("Server: [%s] " % ss.server, ss.server)
        server = ui_server.get().variable

        ss_ = Salsa_Share(new_name, server)

        ui_username = OptionalUserInput("Username: [%s] " %
                                        ss.username, ss.username)
        ss_.username = ui_username.get().variable

        password = OptionalUserInput("Password: ").get().variable
        rp_password = OptionalUserInput("Repeat Password: ").get().variable
        while (password != rp_password):
            print "Passwords didn't match, pls retry kthxbai"
            password = OptionalUserInput("Password: ").get().variable
            rp_password = OptionalUserInput("Repeat Password: ").get().variable

        ss_.password = password

        ui_share = OptionalUserInput("Folder: [%s]" % ss.share, ss.share)
        ss_.share = ui_share.get().variable

        ui_mount_point = OptionalUserInput("Mount Point: [%s]" %
                                           ss.mount_point, ss.mount_point)
        ss_.mount_point = ui_mount_point.get().variable

        self.config_file.edit_share(name, ss_)

    def list_shares(self):
        "List all samba shares"
        self.config_file.list_shares()

    def show_share_details(self, name):
        "Show samba share details based on given name"
        self.config_file.show_share_details(name)

    def mount_share(self, name):
        "Mount samba share based on given name"
        self.config_file.mount_share(name)

    def umount_share(self, name):
        "Unmount samba share based on given name"
        self.config_file.umount_share(name)
