# -*- coding: utf-8 -*-
#########################################################
# SERVICE : keys.py                                     #
#           Handles keys file for sshfs                 #
#                                                       #
#           I. Helwegen 2021                            #
#########################################################

####################### IMPORTS #########################
import os
import pwd
import subprocess
#########################################################

####################### GLOBALS #########################
S2HFSKEYS    = "/root/.s2hfskeys-"
KEYSMODE     = 0o600
SSH          = "ssh"
SSHPASS      = "sshpass"
SSHKEYGEN    = "ssh-keygen"
ROOTSSH      = "/root/.ssh"
SSHMODE      = 0o644
#########################################################

###################### FUNCTIONS ########################

#########################################################

#########################################################
# Class : keys                                          #
#########################################################
class keys(object):
    def __init__(self):
        pass

    def __del__(self):
        pass

    def available(self, host, username):
        retval = False
        keys = self.getKey(host, username)
        if keys:
            retval = True
        return retval

    def addKey(self, host, username, idFile):
        retval = True
        if self.hasKeysFile(host):
            self.delKey(host, username)
        self.checkKeysFile(host)
        self.addKey_(host, username, idFile)
        return retval

    def delKey(self, host, username, idFile = ""):
        retval = False
        if self.hasKeysFile(host):
            keys = self.findKey(host, username)
            if keys:
                if not idFile or keys["idFile"] == idFile:
                    self.removeKey(host, keys["line"])
                    retval = True
            #remove file if empty
            keys = self.findKey(host)
            if not keys:
                self.removeKeysFile(host)
        return retval

    def getKey(self, host, username):
        keys = {}
        if self.hasKeysFile(host):
            keys = self.findKey(host, username)
        return keys

    def generateKeyFiles(self, host, username, password):
        retval = self.SshKeysGenerate(host, username, password)

        if retval["result"]:
            retval = self.SshKeysInstall(host, username, password, retval["idFile"])
        return retval

    def removeKeyFiles(self, host, username, password, idFile, force = False):
        retval = self.SshKeysUninstall(host, username, password, idFile)

        if retval["result"] or force:
            if force and not retval["result"]:
                self.SshKeysRemove(idFile)
            else:
                retval = self.SshKeysRemove(idFile)
        return retval

    ################## INTERNAL FUNCTIONS ###################

    def hasKeysFile(self, host):
        keysfile = self.getKeysFile(host)
        return os.path.isfile(keysfile)

    def checkKeysFile(self, host):
        keysfile = self.getKeysFile(host)
        if not self.hasKeysFile(host):
            with open(keysfile, "wt") as fp:
                fp.writelines(["# s2hfs keys file\n","# Host: {}\n\n".format(host)])
            os.chown(keysfile, pwd.getpwnam('root').pw_uid, pwd.getpwnam('root').pw_gid) # set user:group as root:root
            os.chmod(keysfile, KEYSMODE)

    def findKey(self, host, username = ""):
        key = {}
        linenr = 0
        keysfile = self.getKeysFile(host)
        with open(keysfile, "rt") as fp:
            for line in fp:
                if len(line.strip()) > 0:
                    if line.strip()[0] != "#":
                        content = line.split("::")
                        if len(content) > 1:
                            if content[0] == username or not username:
                                key['username'] = content[0]
                                key['idFile'] = content[1]
                                key['line'] = linenr
                                break
                linenr += 1
        return key

    def removeKey(self, host, line):
        keysfile = self.getKeysFile(host)
        with open(keysfile, "rt") as fp:
            lines = fp.readlines()

        lines.pop(line)

        with open(keysfile, "wt") as fp:
            fp.writelines(lines)

    def addKey_(self, host, username, idFile):
        keysfile = self.getKeysFile(host)
        with open(keysfile, "rt") as fp:
            filetext = str(fp.read())
        newline = "\n"
        if filetext[-1] == newline:
            newline = ""

        with open(keysfile, "at") as fp:
            fp.writelines(["{}{}::{}".format(newline, username, idFile)])

    def removeKeysFile(self, host):
        keysfile = self.getKeysFile(host)
        try:
            os.remove(keysfile)
        except:
            pass

    def getKeysFile(self, host):
        return "{}{}".format(S2HFSKEYS,self.getKeysSuffix(host))

    def getKeysSuffix(self, host):
            return host.replace('/',"_").replace(":","_")

    ### Command handling ###

    def runCommand(self, cmd, input = None, timeout = None):
        retval = {}
        retval["retcode"] = 127
        retval["stdout"] = ""
        retval["stderr"] = ""
        if input:
            input = input.encode("utf-8")
        try:
            if timeout == 0:
                timout = None
            out = subprocess.run(cmd, shell=True, capture_output=True, input = input, timeout = timeout)
            retval["retcode"] = out.returncode
            retval["stdout"] = out.stdout.decode("utf-8")
            retval["stderr"] = out.stderr.decode("utf-8")
        except subprocess.TimeoutExpired:
            retval["retcode"] = 124
        return retval

    def findCommand(self, cmd):
        loc = ""
        cmd2 = "command -v " + cmd
        retval = self.runCommand(cmd2)
        if retval["retcode"] == 0:
            loc = retval["stdout"].strip()
        return loc

    def generateKeysFile(self, host, username):
        # if not exists ROOTSSH
        if not os.path.exists(ROOTSSH):
            os.mkdir(ROOTSSH)
            os.chown(ROOTSSH, pwd.getpwnam('root').pw_uid, pwd.getpwnam('root').pw_gid) # set user:group as root:root
            os.chmod(ROOTSSH, SSHMODE)

        return ROOTSSH + "/id_ecdsa_" + username.replace("/","_").replace(":","_") + "@" + host.replace("/","_").replace(":","_")

    def getPubFile(self, idFile):
        return idFile+".pub"

    def SshKeysGenerate(self, host, username, password):
        retval = {}
        retval["result"] = True
        retval["text"] = ""
        retval["idFile"] = ""

        loc = self.findCommand(SSHKEYGEN)
        if not loc:
            retval["result"] = False
            retval["text"] = "Required package not installed: {}".format(SSHKEYGEN)
        else:
            keyfile = self.generateKeysFile(host, username)
            # generate filename from host, username
            cmd = loc + " -q -t ecdsa -b 521 -f " + keyfile + " -N " + password
            out = self.runCommand(cmd)
            if out["retcode"] != 0:
                retval["result"] = False
                retval["text"] = out["stderr"]
            else:
                retval["idFile"] = keyfile

        return retval

    def SshKeysRemove(self, idFile):
        retval = {}
        retval["result"] = True
        retval["text"] = ""
        retval["idFile"] = idFile

        pubfile = self.getPubFile(idFile)

        if os.path.exists(idFile):
            os.remove(idFile)
        else:
            retval["result"] = False
            retval["text"] = "File doesn't exists: {}".format(idFile)

        if os.path.exists(pubfile):
            os.remove(pubfile)
        else:
            if retval["result"]:
                retval["result"] = False
                retval["text"] = "File doesn't exists: {}".format(pubfile)

        return retval

    def SshKeysInstall(self, host, username, password, idFile):
        retval = {}
        retval["result"] = True
        retval["text"] = ""
        retval["idFile"] = idFile

        loc = self.findCommand(SSH)
        locpass = ""
        if not loc:
            retval["result"] = False
            retval["text"] = "Required package not installed: {}".format(SSH)
        else:
            locpass = self.findCommand(SSHPASS)
            if not locpass:
                retval["result"] = False
                retval["text"] = "Required package not installed: {}".format(SSHPASS)

        if retval["result"]:
            service = username + "@" + host
            passcmd = locpass + " -p " + password + " "
            cmd = passcmd + loc + " " + service + " \"umask 077; test -d .ssh || mkdir .ssh\""
            out = self.runCommand(cmd)
            if out["retcode"] != 0:
                retval["result"] = False
                retval["text"] = out["stderr"]
            else:
                #load pubkey
                pubFile = self.getPubFile(idFile)
                if not os.path.exists(pubFile):
                    retval["result"] = False
                    retval["text"] = "Public key file doesn't exist: {}".format(pubFile)
                else:
                    with open(pubFile, "rt") as fp:
                        pubKey = str(fp.read()).strip()

                    cmd = passcmd + loc + " " + service + " \"echo {} >> .ssh/authorized_keys\"".format(pubKey)
                    out = self.runCommand(cmd)
                    if out["retcode"] != 0:
                        retval["result"] = False
                        retval["text"] = out["stderr"]

        return retval

    def SshKeysUninstall(self, host, username, password, idFile):
        retval = {}
        retval["result"] = True
        retval["text"] = ""
        retval["idFile"] = idFile

        loc = self.findCommand(SSH)
        locpass = ""
        if not loc:
            retval["result"] = False
            retval["text"] = "Required package not installed: {}".format(SSH)
        else:
            locpass = self.findCommand(SSHPASS)
            if not locpass:
                retval["result"] = False
                retval["text"] = "Required package not installed: {}".format(SSHPASS)

        if retval["result"]:
            #load pubkey
            pubFile = self.getPubFile(idFile)
            if not os.path.exists(pubFile):
                retval["result"] = False
                retval["text"] = "Public key file doesn't exist: {}".format(pubFile)
            else:
                with open(pubFile, "rt") as fp:
                    pubKey = str(fp.read()).strip().replace("/","\/")
                service = username + "@" + host
                passcmd = locpass + " -p " + password + " "
                cmd = passcmd + loc + " " + service + " \"sed -i '/{}/d' .ssh/authorized_keys\"".format(pubKey)
                out = self.runCommand(cmd)
                if out["retcode"] != 0:
                    retval["result"] = False
                    retval["text"] = out["stderr"]
        return retval

######################### MAIN ##########################
if __name__ == "__main__":
    pass
