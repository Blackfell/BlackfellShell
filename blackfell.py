#!/usr/bin/env python3

import cmd
import os, sys
import signal
import argparse
import threading
import time
import queue
import ctypes
import colorama

from pynput import keyboard

from menus import home
from common import bcolors as bc

def SigintHandler(SIG, FRM):
    print("^C")

def get_args():
    """Get arguments for the main CLI tool, blackfell shell"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--resource-file", type = str, help = "Run the Blackfell Shell from a resource file.")
    parser.add_argument("-y", "--noconfirm", action="store_true", help = "Don't prompt for privilege confirmation on startup.")
    return parser.parse_args()

def check_root(no_confirm):
    """Check user privs and prompt user that they may want to
            elevate to enable certain networking stuff"""
    decision = ''
    if sys.platform == 'win32':
        if not ctypes.windll.shell32.IsUserAnAdmin() != 0 and not no_confirm:
            bc.warn_print("[!] ", "- You are not running as Admin, you may not be able to do certain actions, e.g. bind to low ports.")
            while decision != 'y' and decision != 'n':
                decision = input("Do you want to continue anyway? [y/n]:").lower()
            if decision == 'n':
                sys.exit(0)
            else:
                pass
    else:
        if os.getuid() != 0 and not no_confirm:
            bc.warn_print("[!] ", "- You are not running as root, you may not be able to do certain actions, e.g. bind to low ports.")
            while decision != 'y' and decision != 'n':
                decision = input("Do you want to continue anyway? [y/n]:").lower()
            if decision == 'n':
                sys.exit(0)
            else:
                pass



def main():
    """Function that runs the Blackfell Shell C2, including setting up modules etc."""

    colorama.init()     #Ansi escape codes in Windows!
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
        #Run interpreter as a thread
        t = threading.Thread(target = bs.cmdloop)
        t.start()
        with open( args.resource_file, 'r') as f:
            """Pipe commands via stdin, can't use standard run utils because
            we're using nested interpreters"""
            sys.stdin = f
            """Stdin doesn't reassign properly until a keypress don't ask me
            why it just doesn't OK? This is a workaround to get the interpreter
            to start. If it's stupid and it works, it's not stupid. Mostly."""
            kbd = keyboard.Controller()
            kbd.press(keyboard.Key.enter)
            kbd.release(keyboard.Key.enter)
            #Read all the lines of resource file, then back to normal
            while True:
                #Now check if resource file done and if so, reset stdin
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
