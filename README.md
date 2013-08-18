Salsa
=====

## What does it do

Lets you manage your samba connections via cli and mount/unmount them to the
specified directory.

## Installation

__Easy install__

    $ git clone git://github.com/fowbi/salsa.git
    $ cd salsa
    $ python setup.py build
    $ [sudo] easy_install .

__Pip__

    $ git clone git://github.com/fowbi/salsa.git
    $ cd salsa
    $ python setup.py build
    $ [sudo] pip install .

    or upgrade

    $ [sudo] pip install --upgrade .

## Usage

See `salsa --help`.

### Adding samba shares

    $ salsa add [-h]

A prompt will ask about name, server, username, password, share name and mount
point.
    
### Editing samba shares

    $ salsa edit [-h] name

A prompt will ask about name, server, username, password, share name and
mount point. If nothing is filled in, the old values will be re-used (except
for password)

### Deleting samba shares

    $ salsa delete [-h] name

### Mounting to samba share

    $ salsa mount [-h] name

### Unmounting samba share

    $ salsa unmount [-h] name

### Show list of samba shares

    $ salsa list [-h]

This will show a list of all samba shares in the config file. They will be
listed as a connection string.

### Show details of single samba share

    $ salsa show [-h] name

This will show a single samba share from the config file. Again showing it as a
connection string.

### salsa_config

Everything will be saved in yaml format in a .salsa_config file on the home
directory.

## Known issues

Everything is `really` buggy right now, use at your own risk kthxbai
