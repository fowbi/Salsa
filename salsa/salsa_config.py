import yaml
import pexpect

from os.path import exists, dirname, join, isdir, expanduser
from os import listdir, rmdir, makedirs
from core import which


class Config(object):
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
        return expanduser('~/.salsa_config')

    def load(self):
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
        dict_list = []
        for share in self.shares:
            # Fallback to guest login when username is empty
            if (share.username == ''):
                share.username = 'guest'
                share.password = ''

            dict_list.append(share.__dict__)

        yaml.dump_all(dict_list, open(self.config_file, 'w'), default_flow_style=False)

    def add_share(self, salsa_share):
        if not self.is_duplicate_share(salsa_share):
            self.shares.append(salsa_share)
            self.write()
        else:
            raise Exception('duplicate name')

    def delete_share(self, name):
        new_shares = [share for share in self.shares if share.name != name]
        if (len(new_shares) == len(self.shares)):
            return False

        self.shares = new_shares
        self.write()
        return True

    def edit_share(self, name, salsa_share):
        for share in self.shares:
            print share.name
            if share.name == name:
                share.name = salsa_share.name
                share.username = salsa_share.username
                share.password = salsa_share.password
                share.share = salsa_share.share
                share.mount_point = salsa_share.mount_point
                self.write()
                return

        raise Exception(name + ' does not exist')

    def list_shares(self):
        for share in self.shares:
            print share

    def show_share_details(self, name):
        for share in self.shares:
            if share.name == name:
                print share
                return

        print name, "not found"

    def mount_share(self, name):
        for share in self.shares:
            if share.name == name:
                share.pre_mount()
                share.mount()
                share.post_mount()
                return

    def umount_share(self, name):
        for share in self.shares:
            if share.name == name:
                share.umount()
                return

    def is_duplicate_share(self, salsa_share):
        for share in self.shares:
            if share.name == salsa_share.name:
                return True

        return False

    def lookup_share(self, name):
        for share in self.shares:
            if name == share.name:
                return share

        raise Exception(name + " does not exist")


class Salsa_Share(object):
    username = "guest"
    password = ""
    share = ""
    mount_point = ""

    def __init__(self, name, server):
        self.name = name
        self.server = server

    def test_connection(self):
        print "test connection"

    def __repr__(self):
        slash_server_path = join("/", self.share)
        cmd = "//%s:%s@%s%s %s"
        cmd = cmd % (self.username, self.password, self.server, slash_server_path,
            self.mount_point)

        return self.name + "\n\t" + cmd

    def pre_mount(self):
        # Create mount point directory
        if not exists(self.mount_point):
            try:
                makedirs(self.mount_point)
            except:
                print 'nope'
                pass
        if not isdir(self.mount_point):
            raise Exception("Error while creating dir : %s" % self.mount_point)

    def post_mount(self):
        pass

    def mount(self):
        mount_bin = which("mount_smbfs")
        slash_server_path = join("/", self.share)
        cmd = "%s //%s:%s@%s%s %s"
        cmd = cmd % (mount_bin, self.username, self.password, self.server, slash_server_path,
                self.mount_point)
        (output, returncode) = pexpect.run(cmd, withexitstatus=1, timeout=5)

        if returncode != 0:
            raise Exception("Error while mounting : %s" % output)

    def pre_umount(self):
        pass

    def post_umount(self):
        if isdir(self.mount_point) and listdir(self.mount_point) == []:
            rmdir(self.mount_point)

    def umount(self):
        umount_bin = which("umount")
        cmd = "%s %s" % (umount_bin, self.mount_point)
        (output, returncode) = pexpect.run(cmd, withexitstatus = 1, timeout = 5)

        if returncode != 0:
            raise Exception("Error while umounting : %s\n%s" %
                    (self.mount_point, output))
