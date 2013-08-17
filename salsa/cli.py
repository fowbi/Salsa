# -*- coding: utf-8 -*-


import argparse
from core import ColoredOutput
from exceptions import SalsaException, SalsaConnectionException


class Cli(object):
    def __init__(self, salsa):
        self.salsa = salsa
        self.parser = argparse.ArgumentParser(
            description='Manage samba connections')

        subparsers = self.parser.add_subparsers(dest="command")

        # Show single share command
        parser_show = subparsers.add_parser('show',
                                            help='Show single share')
        parser_show.add_argument('name', help='Name of samba share')

        # Show all shares command
        subparsers.add_parser('list',
                              help="List all shares available")

        # Add command
        subparsers.add_parser('add',
                              help="Add a new share")

        # Edit command
        parser_edit = subparsers.add_parser('edit',
                                            help="Edit existing share")
        parser_edit.add_argument('name', help='Name of samba share')

        # Delete command
        parser_delete = subparsers.add_parser('delete',
                                              help="Delete existing share")
        parser_delete.add_argument('name', help='Name of samba share')

        # Mount command
        parser_mount = subparsers.add_parser('mount',
                                             help='Mount existing share')
        parser_mount.add_argument('name', help='Name of samba share')

        # Unmount command
        parser_umount = subparsers.add_parser(
            'umount',
            help='Unmount existing and mounted share')
        parser_umount.add_argument('name', help='Name of samba share')

        # Execute command
        self.execute(self.parser.parse_args())

    def execute(self, args):
        #print args

        try:
            if args.command == 'show':
                self.salsa.show_share_details(args.name)
            elif args.command == 'list':
                self.salsa.list_shares()
            elif args.command == 'add':
                name = self.salsa.add_share()
                ColoredOutput().success("Share %s has been added!" % name)
            elif args.command == 'edit':
                self.salsa.edit_share(args.name)
                ColoredOutput().success("Share %s has been edited!" % args.name)
            elif args.command == 'delete':
                self.salsa.delete_share(args.name)
                ColoredOutput().success("Share %s has been deleted!" % args.name)
            elif args.command == 'mount':
                self.salsa.mount_share(args.name)
                ColoredOutput().success("Share %s has been mounted" % args.name)
            elif args.command == 'umount':
                self.salsa.umount_share(args.name)
                ColoredOutput().success("Share %s has been unmounted" % args.name)
        except SalsaConnectionException, err:
            ColoredOutput().error("\t%s" % str(err))
        except SalsaException, err:
            ColoredOutput().error("\t%s" % str(err))
        except Exception, err:
            ColoredOutput().error("\t Something went wrong!!\n\t << %s >>" % err)
        except KeyboardInterrupt:
            pass

        print "\n"
