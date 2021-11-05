#!/bin/bash

NAME="s2hfs"
SBINDIR="/sbin"
OPTDIR="/opt"
OPTLOC="$OPTDIR/$NAME"
PY=".py"
S2HFS="mount.$NAME"
SBINS2HFS="$SBINDIR/$NAME"
SBINMNTS2HFS="$SBINDIR/$S2HFS"
PYS2HFS="$OPTLOC/$NAME$PY"

DEBFOLDER="debian"
INSTALL="/usr/bin/install -c"
INSTALL_DATA="$INSTALL -m 644"
INSTALL_PROGRAM="$INSTALL"

if [ "$EUID" -ne 0 ]
then
	echo "Please execute as root ('sudo install.sh' or 'sudo make install')"
	exit
fi

if [ "$1" == "-u" ] || [ "$1" == "-U" ]
then
    echo "Uninstalling $NAME"

    # Remove links
    echo "Removing binaries"
    [ -L $SBINS2HFS ] && unlink $SBINS2HFS
    [ -L $SBINMNTS2HFS ] && unlink $SBINMNTS2HFS

    echo "Removing files"
	if [ -d "$OPTLOC" ]; then rm -rf "$OPTLOC"; fi
elif [ "$1" == "-h" ] || [ "$1" == "-H" ]
then
	echo "Usage:"
	echo "  <no argument>: install $NAME"
	echo "  -u/ -U       : uninstall $NAME"
	echo "  -h/ -H       : this help file"
	echo "  -d/ -D       : build debian package"
	echo "  -c/ -C       : Cleanup compiled files in install folder"
elif [ "$1" == "-c" ] || [ "$1" == "-C" ]
then
	echo "$NAME Deleting compiled files in install folder"
	py3clean .
	rm -f ./*.deb
	rm -rf "$DEBFOLDER"/$NAME
	rm -rf "$DEBFOLDER"/.debhelper
	rm -f "$DEBFOLDER"/files
	rm -f "$DEBFOLDER"/files.new
	rm -f "$DEBFOLDER"/$NAME.*
elif [ "$1" == "-d" ] || [ "$1" == "-D" ]
then
	echo "$NAME build debian package"
	py3clean .
	fakeroot debian/rules clean binary
	mv ../*.deb .
else
	echo "$NAME install script"

    echo "Installing $NAME"
    if [ -d "$OPTLOC" ]; then rm -rf "$OPTLOC"; fi
	if [ ! -d "$OPTLOC" ]; then
		mkdir "$OPTLOC"
		chmod 755 "$OPTLOC"
	fi

    # Install all files and folders
    echo "Installing files"
    cp -r ".$OPTLOC"/* "$OPTLOC"
	$INSTALL_PROGRAM ".$PYS2HFS" "$OPTLOC"

    # Add symbolic links
    echo "Installing binaries"
    ln -s $PYS2HFS $SBINS2HFS
    ln -s $PYS2HFS $SBINMNTS2HFS
fi
