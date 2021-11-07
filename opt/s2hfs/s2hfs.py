#!/usr/bin/python3

# -*- coding: utf-8 -*-
#########################################################
# SCRIPT : s2hfs.py                                     #
#          sshfs wrapper for easy automatic login       #
#          on mount                                     #
#                                                       #
#          I. Helwegen 2021                             #
#########################################################

####################### IMPORTS #########################
import sys
import os
from common.options import options
from common.credentials import credentials
from common.keys import keys
from sshfs.sshfs import sshfs
#########################################################

####################### GLOBALS #########################

#########################################################

###################### FUNCTIONS ########################

#########################################################
# Class : s2hfs                                         #
#########################################################
class s2hfs(options, sshfs):
    def __init__(self):
        options.__init__(self, "s2hfs")
        sshfs.__init__(self)
        self.credentials = credentials()
        self.keys = keys()

    def __del__(self):
        del self.keys
        del self.credentials
        sshfs.__del__(self)
        options.__del__(self)

    def run(self, argv):
        checkResults = []
        result = ""
        self.handleArgs(argv)
        if not self.available():
            sys.stderr.write("Error: sshfs not installed\n")
            sys.stderr.write("Install sshfs first, e.g. with 'sudo apt install sshfs'\n")
            exit(1)
        elif "sshfshelp" in self.settings:
            print(repr(self))
            print("------")
            print(self.help())
            print("------")
            exit(1)
        elif "version" in self.settings:
            print(self.version())
            exit(0)
        elif "credentialsadd" in self.settings:
            self.needSudo()
            print("Adding credentials ...")
            if not "password" in self.settings:
                self.settings["password"] = ""
            self.settings["username"] = self.enterUsername(self.settings["username"])
            if not self.settings["username"]:
                sys.stderr.write("Error: invalid username\n")
                exit(1)
            self.settings["password"] = self.enterPassword(self.settings["password"])
            self.credentials.addCredentials(self.settings["host"], self.settings["username"], self.settings["password"])
            print("Credentials added")
            exit(0)
        elif "keyadd" in self.settings:
            self.needSudo()
            print("Generating and installing key ...")
            if not "password" in self.settings:
                self.settings["password"] = ""
            self.settings["username"] = self.enterUsername(self.settings["username"])
            if not self.settings["username"]:
                sys.stderr.write("Error: invalid username\n")
                exit(1)
            self.settings["password"] = self.enterPassword(self.settings["password"])
            if self.keys.available(self.settings["host"], self.settings["username"]):
                sys.stderr.write("Error: key already exists. Delete key first before adding a new one\n")
                exit(1)
            retval = self.keys.generateKeyFiles(self.settings["host"], self.settings["username"], self.settings["password"])
            if not retval["result"]:
                sys.stderr.write("Error: error occured when generating or installing key file\n{}\n".format(retval["text"]))
                exit(1)
            elif not retval["idFile"]:
                sys.stderr.write("Error: error occured when generating or installing key file\n")
                exit(1)
            self.keys.addKey(self.settings["host"], self.settings["username"], self.settings["password"], retval["idFile"])
            print("Keys generated and installed")
            exit(0)
        elif "credentialsdelete" in self.settings:
            self.needSudo()
            print("Deleting credentials ...")
            self.settings["username"] = self.enterUsername(self.settings["username"])
            if not self.settings["username"]:
                sys.stderr.write("Error: invalid username\n")
                exit(1)
            retval = self.credentials.delCredentials(self.settings["host"], self.settings["username"])
            if not retval:
                sys.stderr.write("Error: credentials not deleted\n")
                exit(1)
            print("Credentials deleted")
            exit(0)
        elif "keydelete" in self.settings:
            self.needSudo()
            print("Deleting and uninstalling keys ...")
            if not "password" in self.settings:
                self.settings["password"] = ""
            self.settings["username"] = self.enterUsername(self.settings["username"])
            if not self.settings["username"]:
                sys.stderr.write("Error: invalid username\n")
                exit(1)
            force = ("force" in self.settings)
            key = self.keys.getKey(self.settings["host"], self.settings["username"])
            if not key:
                sys.stderr.write("Error: key file not found\n")
                exit(1)
            if not self.settings["password"]:
                if key["password"]:
                    self.settings["password"] = key["password"]
                else:
                    self.settings["password"] = self.enterPassword(self.settings["password"])
            retval = self.keys.removeKeyFiles(self.settings["host"], self.settings["username"], self.settings["password"], key["idFile"], force)
            if not retval["result"]:
                sys.stderr.write("Error: removing key files\n{}\n".format(retval["text"]))
                if not force:
                    exit(1)
            retval2 = self.keys.delKey(self.settings["host"], self.settings["username"])
            if not retval2:
                sys.stderr.write("Error: keys not deleted\n")
                if not force:
                    exit(1)
            if not retval["result"] or not retval2:
                sys.stderr.write("Error: errors occured in deleting keys, you may have to delete them manually\n")
                exit(1)
            else:
                print("Keys deleted and uninstalled")
                exit(0)
        elif "credentialsget" in self.settings:
            cred = {}
            cred["username"] = ""
            self.needSudo()
            self.settings["username"] = self.enterUsername(self.settings["username"])
            if not self.settings["username"]:
                sys.stderr.write("Error: invalid username\n")
                exit(1)
            if self.credentials.available(self.settings["host"], self.settings["username"]):
                cred = self.credentials.getCredentials(self.settings["host"], self.settings["username"])
            print(cred["username"])
            exit(0)
        elif "keyget" in self.settings:
            key = {}
            key["idFile"] = ""
            self.needSudo()
            self.settings["username"] = self.enterUsername(self.settings["username"])
            if not self.settings["username"]:
                sys.stderr.write("Error: invalid username\n")
                exit(1)
            if self.keys.available(self.settings["host"], self.settings["username"]):
                key = self.keys.getKey(self.settings["host"], self.settings["username"])
            print(key["idFile"])
            exit(0)
        else:
            self.needSudo()
            retval = False
            service = self.buildService()
            if "password" in self.settings:
                retval = self.runPwd(service, self.settings["mountpoint"], self.settings["options"], self.settings["password"])
            elif self.keys.available(self.settings["host"], self.settings["username"]):
                key = self.credentials.getKey(self.settings["host"], self.settings["username"])
                retval = self.runId(service, self.settings["mountpoint"], self.settings["options"], key["IdFile"])
            elif self.credentials.available(self.settings["host"], self.settings["username"]):
                creds = self.credentials.getCredentials(self.settings["host"], self.settings["username"])
                retval = self.runPwd(service, self.settings["mountpoint"], self.settings["options"], creds["password"])
            else:
                retval = self.runStd(service, self.settings["mountpoint"], self.settings["options"])
            exit(0 if retval else 1)

    def handleArgs(self, argv):
        xargs = {"<service>": "url of ssh service",
                 "<mountpoint>": "mountpoint to mount to"}
        xopts = {"sshfshelp": "shows sshfs help and options",
                 "credentialsadd": "adds credentials to credentials file",
                 "keyadd": "generates, installs key and stores in key file",
                 "credentialsdelete": "delete credentials file",
                 "keydelete": "uninstalls and deletes key file",
                 "credentialsget": "return username if credentials exist",
                 "keyget": "return key file location if key exists",
                 "folder": "folder to mount if not in <service> format",
                 "username": "username if not in <service> format",
                 "password": "password to use",
                 "nouser": "do not allow user to access mount (-o nouser)",
                 "nokeep": "auto unmount when not accessed (-o nokeep)",
                 "noautoaccept": "do not auto accept new hosts (-o noautoaccept)",
                 "force": "force deletion of keys and keys files"}
        specopts = {"options": "default mount options"}
        extra = ('<service> is in format: [username@]host:[folder]\n'
                 'Common usage:\n'
                 '    mount.s2hfs <service> <mountpoint> [-o options]\n'
                 'For adding credentials/ keys:\n'
                 '    mount.s2hfs <service> -c -p password (or interactive if omitted)\n'
                 '    mount.s2hfs <service> -k -p password (or interactive if omitted)\n'
                 'For deleting credentials/ keys:\n'
                 '    mount.s2hfs <service> -C/K')
        self.fillSettings(self.parseOpts(argv, xopts, specopts, xargs, extra))

    def fillSettings(self, optsnargs):
        self.settings["service"] = ""
        self.settings["mountpoint"] = ""
        if len(optsnargs[1]) > 0:
            self.settings["service"]=optsnargs[1][0]
        if len(optsnargs[1]) > 1:
            self.settings["mountpoint"]=optsnargs[1][1]

        if not self.settings["service"] and not ("sshfshelp" in optsnargs[0]) and not ("version" in optsnargs[0]):
            self.parseError("Not enough arguments, no service defined")
        optlist = ["sshfshelp", "version", "credentialsadd", "keyadd", "credentialsdelete", "keydelete", "credentialsget", "keyget"]
        if not self.settings["mountpoint"] and not any(item in optlist for item in optsnargs[0]):
            self.parseError("Not enough arguments, no mountpoint defined")

        #service to username and location
        if self.settings["service"]:
            hostfolder = self.settings["service"].split(":")
            self.settings["host"] = hostfolder[0]
            if not "folder" in optsnargs[0]:
                if len(hostfolder) > 1:
                    self.settings["folder"] = hostfolder[1]
                else:
                    self.settings["folder"] = "/"
            if not "username" in optsnargs[0]:
                servuserloc = self.settings["host"].split("@")
                if len(servuserloc) > 1:
                    self.settings["username"] = servuserloc[0]
                    self.settings["host"] = "@".join(servuserloc[1:])
                else:
                    self.settings["username"] = ""
                    self.settings["host"] = self.settings["host"]

        self.settings.update(optsnargs[0])
        self.settings.update(optsnargs[2])

        if "folder" in self.settings:
            if self.settings["folder"][0] != "/":
                self.settings["folder"] = "/" + self.settings["folder"]

        if not "options" in self.settings:
            self.settings["options"] = []

        nouser = False
        if "nouser" in self.settings:
            nouser = self.settings["nouser"]
        self.optionsNouser(self.settings["options"], nouser)

        nokeep = False
        if "nokeep" in self.settings:
            nokeep = self.settings["nokeep"]
        self.optionsNokeep(self.settings["options"], nokeep)

        noautoaccept = False
        if "noautoaccept" in self.settings:
            noautoaccept = self.settings["noautoaccept"]
        self.optionsNoautoaccept(self.settings["options"], noautoaccept)

    def buildService(self):
        service = ""
        if self.settings["username"]:
            service = self.settings["username"] + "@" + self.settings["host"] + ":" + self.settings["folder"]
        else:
            service = self.settings["host"] + ":" + self.settings["folder"]
        return service
#########################################################

######################### MAIN ##########################
if __name__ == "__main__":
    s2hfs().run(sys.argv)
