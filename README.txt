s2hfs v0.8.5

s2hfs -- sshfs wrapper for easy automatic login on mount
===== == ===== ======= === ==== ========= ===== == =====

sshfs is a module to mount sftp as a filesystem. However logging in using a password, or generating keys is not very intuitive. This wrapper helps in automating this for you.

Run from command line:
=== ==== ======= =====

s2hfs: sshfs wrapper for easy automatic login on mount
Usage:
    s2hfs <arguments> <options>
    <arguments>:
        <service>   : url of ssh service
        <mountpoint>: mountpoint to mount to
    <options>:
        -h, --help             : this help file
        -v, --version          : print version information
        -s, --sshfshelp        : shows sshfs help and options
        -c, --credentialsadd   : adds credentials to credentials file
        -k, --keyadd           : generates, installs key and stores in key file
        -C, --credentialsdelete: delete credentials file
        -K, --keydelete        : uninstalls and deletes key file
        -r, --credentialsget   : return username if credentials exist
        -e, --keyget           : return key file location if key exists
        -f, --folder           : folder to mount if not in <service> format
        -u, --username         : username if not in <service> format
        -p, --password         : password to use
        -n, --nouser           : do not allow user to access mount (-o nouser)
        -N, --nokeep           : auto unmount when not accessed (-o nokeep)
        -o, --noautoaccept     : Do not auto accept new hosts (-o noautoaccept)
        -F, --force            : force deletion of keys and keys files
        -O, --options          : default mount options

<service> is in format: [username@]host:[folder]
Common usage:
    mount.s2hfs <service> <mountpoint> [-o options]
For adding credentials/ keys:
    mount.s2hfs <service> -c -p password (or interactive if omitted)
    mount.s2hfs <service> -k -p password (or interactive if omitted)
For deleting credentials/ keys:
    mount.s2hfs <service> -C/K

Integrate in fstab/ systemd-mount:
========= == ====== ==============

fstab:
[username@]host:[folder]	/mnt/MOUNTPOINT	s2hfs	_netdev,OTHER_MOUNT_OPTIONS	0	0

systemd-mount:
mnt-MOUNTPOINT.mount
--------------------------------------------------------------
[Unit]
Descritpion=whatever you want to mention here

[Mount]
Where=/mnt/MOUNTPOINT
What=[username@]host:[folder]
Type=s2hfs
TimeoutSec=10s
Options=_netdev,OTHER_MOUNT_OPTION
--------------------------------------------------------------

Automount is also possible in fstab (add x-systemd.automount as option)

or in systemd:
mnt-MOUNTPOINT.automount
--------------------------------------------------------------
[Unit]
Description=whatever you want to mention here

[Automount]
Where=/mnt/MOUNTPOINT
TimeoutIdleSec=30s
--------------------------------------------------------------

Installation:
=============

From github:
-------------
- Browse to: https://github.com/Helly1206/s2hfs
- Click the 'Clone or Download' button
- Click 'Download Zip'
- Unzip the zip file to a temporary location
- Open a terminal at this location
- Check sshfs is installed (e.g. install it with 'sudo apt install sshfs')
- Enter: 'sudo ./install.sh'
- Wait until completed

Installer options:
--------- --------
sudo ./install.sh    --> Installs s2hfs
sudo ./install.sh -u --> Uninstalls s2hfs
sudo ./install.sh -c --> Deletes compiled files in install folder (only required when copying or zipping the install folder)

Package install:
------- --------
S2hfs installs automatically from deb package/ apt repository (only for debian based distros like debian or ubuntu).
Install with 'sudo apt install s2hfs'. Manually installing sshfs is not required now.

That's all for now ...

Please send Comments and Bugreports to hellyrulez@home.nl
