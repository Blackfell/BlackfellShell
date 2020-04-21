#!/usr/bin/env python3

import cmd
import os, sys
import signal
import argparse
import threading
import time
import queue

from menus import home
#import menus
from common import bcolors as bc

def SigintHandler(SIG, FRM):
    print("^C")

def get_args():
    parser = argparse.ArgumentParser()
    #group = parser.add_mutually_exclusive_group()
    #group.add_argument("-H", "--LHOST", type = str, help = "LHOST halue to set")
    parser.add_argument("-r", "--resource-file", type = str, help = "Run the Blackfell Shell from a resource file.")
    parser.add_argument("-y", "--noconfirm", action="store_true", help = "Don't prompt for privilege confirmation on startup.")
    return parser.parse_args()

def check_root(no_confirm):
    decision = ''
    if os.getuid() != 0 and not no_confirm:
        bc.warn_print("[!] ", "- You are not running as root, you may not be able to do certain actions, e.g. bind to low ports.")
        while decision != 'y' and decision != 'n':
            decision = input("Do you want to continue anyway? [y/n]:").lower()
        if decision == 'n':
            sys.exit(0)
        else:
            pass

def main():
    args = get_args()
    check_root(args.noconfirm)

    #Add Ctrl C handling
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, SigintHandler)

    ## Run the shell
    bs = home.BSMainMenu()

    #Handle resource files
    if args.resource_file:
        #Declare to interpreter that we're running a resource file
        bs.q['read'].put("RESOURCE")
        #time.sleep(0.1)

        #Run interpreter as a thread
        t = threading.Thread(target = bs.cmdloop)
        t.start()
        #time.sleep(0.1)

        #bs.q['read'].put("RESOURCE")
        #Declare to interpreter that we're running a resource file
        #bs.q['read'].put("RESOURCE")
        with open( args.resource_file, 'r') as f:
            #Pipe commands via stdin, can't use standard run utils because nested interpreters
            sys.stdin = f
            while True:
                #time.sleep(0.1)
                if not bs.q['write'].empty() and bs.q['write'].get() == "DONE":
                    bc.green_print("[+] ", " - Resource file complete.")
                    sys.stdin=sys.__stdin__
                    break
                else:
                    #Not done yet
                    time.sleep(0.1)
    else:
        #bs.cmdloop()
        # The real thing to be done once done developing!
        try:
            bs.cmdloop()
        except Exception as e:
            print("Exception in loop : {} ".format(e))
            bc.err_print("[!] ", "- Exiting.")

if __name__ == '__main__':
        main()
