# -*- coding: utf-8 -*-
#########################################################
# SERVICE : sshfs.py                                    #
#           sshfs python wrapper (executing sshfs)      #
#                                                       #
#           I. Helwegen 2021                            #
#########################################################

####################### IMPORTS #########################
import sys
import subprocess
#########################################################

####################### GLOBALS #########################
NAME = "sshfs"
#########################################################

###################### FUNCTIONS ########################

#########################################################

#########################################################
# Class : sshfs                                         #
#########################################################
class sshfs(object):
    def __init__(self):
        self.hasSshfs = False
        try:
            self.hasSshfs = self.checkInstalled()
        except Exception as e:
            sys.stderr.write("Error reading sshfs information\n")
            sys.stderr.write(e)
            sys.stderr.write("\n")
            exit(1)

    def __del__(self):
        pass

    def available(self):
        return self.hasSshfs

    def help(self):
        retval = ""
        out = self.runCommand(NAME + " -h")
        if out["retcode"] == 1:
            retval = (out["stdout"] + out["stderr"]).strip()
        return retval

    def version(self):
        retval = ""
        out = self.runCommand(NAME + " -V")
        if out["retcode"] == 0:
            retval = (out["stdout"] + out["stderr"]).strip()
        return retval

    def runStd(self, service, mountpoint, options, input = None):
        opts = self.buildOptions(options)
        cmd = NAME + " " + service + " " + mountpoint + opts
        out = self.runCommand(cmd, input)
        return self.checkOutput(out)

    def runPwd(self, service, mountpoint, options, password):
        self.runOptions(options)
        return self.runStd(service, mountpoint, options, password)

    def runId(self, service, mountpoint, options, IdFile):
        self.runOptions(options, IdFile)
        return self.runStd(service, mountpoint, options)

    def optionsNouser(self, options, nouser = False):
        if nouser or "nouser" in options:
            if "allow_other" in options:
                options.remove("allow_other")
        else:
            if not "allow_other" in options:
                options.append("allow_other")
        if "nouser" in options:
            options.remove("nouser")

    def optionsNokeep(self, options, nokeep = False):
        if nokeep or "nokeep" in options:
            if "reconnect" in options:
                options.remove("reconnect")
            # do not remove ServerAliveInterval, user can decide
        else:
            if not "reconnect" in options:
                options.append("reconnect")
            hasopt, value = self.getopt(options, "ServerAliveInterval")
            if not hasopt:
                self.setopt(options, "ServerAliveInterval", 15)
            #ServerAliveCountMax=3, not required as it is the standard setting
        if "nokeep" in options:
            options.remove("nokeep")

    def optionsNoautoaccept(self, options, noautoaccept = False):
        if noautoaccept or "noautoaccept" in options:
            hasopt, value = self.getopt(options, "StrictHostKeyChecking")
            if not hasopt:
                self.setopt(options, "StrictHostKeyChecking", "yes")
        else:
            if not "reconnect" in options:
                options.append("reconnect")
            hasopt, value = self.getopt(options, "StrictHostKeyChecking")
            if not hasopt:
                self.setopt(options, "StrictHostKeyChecking", "accept-new")
        if "noautoaccept" in options:
            options.remove("noautoaccept")

    ################## INTERNAL FUNCTIONS ###################

    def checkInstalled(self):
        retval = self.runCommand(NAME)
        return retval["retcode"] != 127

    def runOptions(self, options, IdFile = ""):
        if not IdFile: # password
            if not "password_stdin" in options:
                options.append("password_stdin")
            self.removeopt(options, "IdentityFile")
        else: # IdFile
            if "password_stdin" in options:
                options.remove("password_stdin")
            self.removeopt(options, "IdentityFile")
            self.setopt(options, "IdentityFile", IdFile)

    def buildOptions(self, options):
        opt = ",".join(options)
        if opt:
            opt = " -o " + opt
        return opt

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

    def checkOutput(self, out):
        retval = True
        if out["stdout"]:
            print(out["stdout"])
        if out["retcode"] != 0:
            retval = False
            sys.stderr.write(out["stderr"])

        return retval

    def setopt(self, options, tag, value):
        opt = tag.strip() + "=" + str(value)
        options.append(opt)

    def getopt(self, options, tag):
        hasopt = False
        value = 0

        for opt in options:
            if tag in opt:
                hasopt = True
                try:
                    value = opt.split("=")[1].strip()
                except:
                    pass
                break

        return hasopt, value

    def removeopt(self, options, tag):
        hasopt = False

        for opt in options:
            if tag in opt:
                hasopt = True
                options.remove(opt)
                break

        return hasopt

    def stripopt(self, opt):
        tag = ""

        try:
            tag = opt.split("=")[0].strip()
        except:
            pass

        return tag

######################### MAIN ##########################
if __name__ == "__main__":
    pass
