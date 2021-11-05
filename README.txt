s2hfs v0.8.0

s2hfs -- sshfs wrapper for easy automatic login on mount
===== == ===== ======= === ==== ========= ===== == =====

sshfs is a module to mount sftp as a filesystem. However logging in using a password, or generating keys is not very intuitive. This wrapper helps in automating this for you.

Run from command line:
=== ==== ======= =====

TBD

Integrate in fstab/ systemd-mount:
========= == ====== ==============

TBD

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
