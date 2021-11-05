# -*- coding: utf-8 -*-
#########################################################
# SERVICE : credentials.py                              #
#           Handles credentials file for sshfs          #
#                                                       #
#           I. Helwegen 2021                            #
#########################################################

####################### IMPORTS #########################
import os
import pwd
#########################################################

####################### GLOBALS #########################
S2HFSCREDS    = "/root/.s2hfscredentials-"
CREDSMODE     = 0o600
#########################################################

###################### FUNCTIONS ########################

#########################################################

#########################################################
# Class : credentials                                   #
#########################################################
class credentials(object):
    def __init__(self):
        pass

    def __del__(self):
        pass

    def available(self, host, username):
        retval = False
        creds = self.getCredentials(host, username)
        if creds:
            retval = True
        return retval

    def addCredentials(self, host, username, password):
        retval = True
        if self.hasCredsFile(host):
            self.delCredentials(host, username)
        self.checkCredsFile(host)
        self.addCred(host, username, password)
        return retval

    def delCredentials(self, host, username, password = ""):
        retval = False
        if self.hasCredsFile(host):
            creds = self.findCred(host, username)
            if creds:
                if not password or creds["password"] == password:
                    self.removeCred(host, creds["line"])
                    retval = True
            #remove file if empty
            creds = self.findCred(host)
            if not creds:
                self.removeCredsFile(host)
        return retval

    def getCredentials(self, host, username):
        creds = {}
        if self.hasCredsFile(host):
            creds = self.findCred(host, username)
        return creds

    ################## INTERNAL FUNCTIONS ###################

    def hasCredsFile(self, host):
        credsfile = self.getCredsFile(host)
        return os.path.isfile(credsfile)

    def checkCredsFile(self, host):
        credsfile = self.getCredsFile(host)
        if not self.hasCredsFile(host):
            with open(credsfile, "wt") as fp:
                fp.writelines(["# s2hfs credentials file\n","# Host: {}\n\n".format(host)])
            os.chown(credsfile, pwd.getpwnam('root').pw_uid, pwd.getpwnam('root').pw_gid) # set user:group as root:root
            os.chmod(credsfile, CREDSMODE)

    def findCred(self, host, username = ""):
        cred = {}
        linenr = 0
        credsfile = self.getCredsFile(host)
        with open(credsfile, "rt") as fp:
            for line in fp:
                if len(line.strip()) > 0:
                    if line.strip()[0] != "#":
                        content = line.split("::")
                        if len(content) > 1:
                            if content[0] == username or not username:
                                cred['username'] = content[0]
                                cred['password'] = content[1]
                                cred['line'] = linenr
                                break
                linenr += 1
        return cred

    def removeCred(self, host, line):
        credsfile = self.getCredsFile(host)
        with open(credsfile, "rt") as fp:
            lines = fp.readlines()

        lines.pop(line)

        with open(credsfile, "wt") as fp:
            fp.writelines(lines)

    def addCred(self, host, username, password):
        credsfile = self.getCredsFile(host)
        with open(credsfile, "rt") as fp:
            filetext = str(fp.read())
        newline = "\n"
        if filetext[-1] == newline:
            newline = ""

        with open(credsfile, "at") as fp:
            fp.writelines(["{}{}::{}".format(newline, username, password)])

    def removeCredsFile(self, host):
        credsfile = self.getCredsFile(host)
        try:
            os.remove(credsfile)
        except:
            pass

    def getCredsFile(self, host):
        return "{}{}".format(S2HFSCREDS,self.getCredsSuffix(host))

    def getCredsSuffix(self, host):
        return host.replace('/',"_").replace(":","_")

######################### MAIN ##########################
if __name__ == "__main__":
    pass
