# -*- coding: utf-8 -*-
#########################################################
# SERVICE : options.py                                  #
#           options file for parsing argumnets and      #
#           options                                     #
#                                                       #
#           I. Helwegen 2021                            #
#########################################################

####################### IMPORTS #########################
import os
import signal
import getpass
#########################################################

####################### GLOBALS #########################
VERSION = "0.8.0"
HELPSTANDARD     = {"help": "this help file",
                    "version": "print version information"}
NOARGS           = "no arguments"
#########################################################

###################### FUNCTIONS ########################

#########################################################

#########################################################
# Class : options                                       #
#########################################################

class options(object):
    def __init__(self, name):
        self.name = name
        self.settings = {}
        signal.signal(signal.SIGINT, self.exitSignal)
        signal.signal(signal.SIGTERM, self.exitSignal)

    def __del__(self):
        del self.settings

    def __str__(self):
        str = """s2hfs: sshfs wrapper for easy automatic login on mount
Version: {}""".format(VERSION)
        return str

    def __repr__(self):
        return "s2hfs: sshfs wrapper for easy automatic login on mount"

    def isSudo(self):
        return os.getuid() == 0

    def needSudo(self):
        if not self.isSudo():
            print(repr(self))
            print("Superuser access required for this operation")
            print("Try running with: 'sudo {}'".format(self.name))
            exit(2)

    def parseOpts(self, argv, opts, specopts, args, extra):
        parsedOpts = []
        parsedArgs = []
        parsedSpec = []
        try:
            optlong, optshort, speclong, specshort = self.buildOpts(opts, specopts)
            parsedOpts, parsedArgs, parsedSpec = self.GetOpt(argv[1:], optshort, optlong, speclong, specshort)
        except:
            self.parseError()
        for opt, arg in parsedOpts.items():
            if opt in ("help"):
                self.printHelp(opts, args, extra, specopts)
                exit()
            elif opt in ("version"):
                print(self)
        return parsedOpts, parsedArgs, parsedSpec

    def parseError(self, opt = ""):
        print(repr(self))
        print("Invalid option entered")
        if opt:
            print(opt)
        print("Enter '{} -h' for help".format(self.name))
        exit(2)

    def toBool(self, val):
        retval = False
        if val == '':
            retval = True
        else:
            try:
                f = float(val)
                if f > 0:
                    retval = True
            except:
                if val.lower() == "true":
                    retval = True

        return retval

    def toInt(self, val):
        retval = 0
        try:
            retval = int(val)
        except:
            pass
        return retval

    def toFloat(self, val):
        retval = 0.0
        try:
            retval = float(val)
        except:
            pass
        return retval

    def hasSetting(self, settings, testkey):
        return testkey in settings

    def hasSettingBool(self, settings, testkey):
        retval = False
        if testkey in settings:
            retval = settings[testkey]
        return retval

    def exitSignal(self, signum = 0, frame = 0):
        print("Execution interrupted, exit ...")
        exit(0)

    def tryInt(self, var):
        val = 0
        if not isinstance(var, int):
            try:
                val = int(var)
            except:
                pass
        else:
            val = var
        return val

    def enterUsername(self, username):
        if username == "":
            print("Username required")
            username = input("Enter username:")
        return username

    def enterPassword(self, password):
        if password == "":
            print("Password required")
            password = getpass.getpass("Enter password:")
        return password

    def enterPassword2x(self):
        print("Password required")
        password  = getpass.getpass("Enter password:")
        password2 = getpass.getpass("Enter password again:")
        if password != password2:
            password = ""
        return password

    ################## INTERNAL FUNCTIONS ###################
    def buildOpts(self, opts, specopts):
        longopts = []
        shortopts = []
        speclong = []
        specshort = []
        allopts = HELPSTANDARD.copy()
        allopts.update(opts)

        for key, value in allopts.items():
            shortopt = self.mkShortOpt(shortopts, key)
            if shortopt:
                longopts.append(key)
                shortopts.append(shortopt)
        for key, value in specopts.items():
            shortopt = self.mkShortOpt(shortopts, key)
            if shortopt:
                speclong.append(key)
                specshort.append(shortopt)

        return longopts, shortopts, speclong, specshort

    def mkShortOpt(self, shortopts, name):
        opt = ""
        if len(name):
            st1 = name[0].lower()
            st2 = name[0].upper()
            if st1 in shortopts:
                if st2 in shortopts:
                    opt = self.mkShortOpt(shortopts, name[1:])
                else:
                    opt = st2
            else:
                opt = st1
        return opt

    def printHelp(self, opts, args, extra, specopts):
        allopts = HELPSTANDARD.copy()
        allopts.update(opts)

        HasOpts = len(allopts)>0
        HasArgs = len(args)>0
        HasSpecOpts = len(specopts)>0

        Arglist = ""
        MaxArg = 0
        MaxOpt = 0
        Dash = False
        if HasArgs:
            for key, value in args.items():
                if key == "-":
                    Dash = True
                    key = "<" + NOARGS + ">"
                if len(key) > MaxArg:
                    MaxArg = len(key)
            if Dash:
                key = NOARGS
                args[key] = args["-"]
                del args["-"]
            Arglist += "<arguments> "
        if HasOpts:
            Arglist += "<options> "
            for key, value in allopts.items():
                if len(key) > MaxOpt:
                    MaxOpt = len(key)
        if HasSpecOpts:
            for key, value in specopts.items():
                if len(key) > MaxOpt:
                    MaxOpt = len(key)

        print(repr(self))
        print("Usage:")
        print("    {} {}".format(self.name, Arglist))
        if HasArgs:
            print("    <arguments>:")
            for key, value in args.items():
                if key == NOARGS:
                    key = "<" + NOARGS + ">"
                spaces = " " * (MaxArg - len(key))
                print("        {}{}: {}".format(key, spaces, value))
        if HasOpts:
            print("    <options>: ")
            shortopts = []
            for key, value in allopts.items():
                shortopt = self.mkShortOpt(shortopts, key)
                shortopts.append(shortopt)
                if shortopt:
                    spaces = " " * (MaxOpt - len(key))
                    print("        -{}, --{}{}: {}".format(shortopt, key, spaces, value))
        if HasSpecOpts:
            shortspecopts = []
            for key, value in specopts.items():
                shortopt = self.mkShortOpt(shortopts, key)
                shortopts.append(shortopt)
                if shortopt:
                    spaces = " " * (MaxOpt - len(key))
                    print("        -{}, --{}{}: {}".format(shortopt, key, spaces, value))
        if extra:
            print("")
            print(extra)

    def GetOpt(self, argv, optshort, optlong, speclong, specshort):
        args = []
        opts = {}
        specopts = {}
        i = 0
        argc = len(argv)
        while i < argc:
            key = ""
            spec = False
            if argv[i][0] == "-": #opt
                if argv[i][1] == "-": # long opt
                    key, value, nextind = self.ParseOpt(argv, i, optshort, optlong)
                    try:
                        ind = optlong.index(key) # ValueError if not in list
                    except ValueError as e:
                        #check special option
                        key, value, nextind = self.ParseOpt(argv, i, specshort, speclong)
                        try:
                            ind = speclong.index(key) # ValueError if not in list
                            spec = True
                        except ValueError as e:
                            key = ""
                            raise ValueError(e)
                    i += nextind
                else: # short opt
                    key, value, nextind = self.ParseOpt(argv, i, optshort, optlong)
                    try:
                        ind = optshort.index(key) # ValueError if not in list
                        key = optlong[ind]
                    except ValueError as e:
                        #check special option
                        key, value, nextind = self.ParseOpt(argv, i, specshort, speclong)
                        try:
                            ind = specshort.index(key) # ValueError if not in list
                            key = speclong[ind]
                            spec = True
                        except ValueError as e:
                            key = ""
                            raise ValueError(e)
                    i += nextind
                if key:
                    if spec:
                        if not key in specopts:
                            specopts[key] = []
                        arrval = value.split(",")
                        specopts[key].extend(arrval)
                    else:
                        opts[key] = value
            else: # arg
                args.append(argv[i])
                i += 1
        return opts, args, specopts

    def ParseOpt(self, argv, i, optshort, optlong):
        key = ""
        value = ""
        isLong = argv[i][1] == "-"
        argc = len(argv)
        IsPos = argv[i].find("=")
        SpacePos = argv[i].find(" ")
        nextind = 1

        if isLong:
            if IsPos >= 0:
                key = argv[i][2:IsPos]
                value = argv[i][IsPos+1:]
            elif SpacePos >= 0:
                key = argv[i][2:SpacePos]
                value = argv[i][SpacePos+1:]
            else:
                key = argv[i][2:]
                #try to find value in next word
                if (i+2) < argc:
                    if (len(argv[i+2]) > 0) and (argv[i+2][0] == "-"):
                        if len(argv[i+1]) == 0:
                            nextind = 2
                        elif argv[i+1][0] != "-":
                            value = argv[i+1]
                            nextind = 2
                elif (i+1) < argc:
                    if len(argv[i+1]) == 0:
                        nextind = 2
                    elif argv[i+1][0] != "-":
                        value = argv[i+1]
                        nextind = 2
        else: # short
            key = argv[i][1]
            slen = len(argv[i][1:])
            if IsPos == 2:
                value = argv[i][IsPos+1:]
            elif SpacePos == 2:
                value = argv[i][SpacePos+1:]
            elif slen > 1:
                value = argv[i][2:]
            else:
                #try to find value in next word
                if (i+2) < argc:
                    if (len(argv[i+2]) > 0) and (argv[i+2][0] == "-"):
                        if len(argv[i+1]) == 0:
                            nextind = 2
                        elif argv[i+1][0] != "-":
                            value = argv[i+1]
                            nextind = 2
                elif (i+1) < argc:
                    if len(argv[i+1]) == 0:
                        nextind = 2
                    elif  argv[i+1][0] != "-":
                        value = argv[i+1]
                        nextind = 2
        return key, value, nextind

######################### MAIN ##########################
if __name__ == "__main__":
    pass
