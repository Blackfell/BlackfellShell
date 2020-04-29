#!/usr/bin/python3

import cmd
import os
import sys
import glob
import readline
import socket
import time
import signal
import re

from Crypto.PublicKey import RSA

from menus import listeners as lnrs
from menus import agents as agts
from menus import modules as mod
from common import bcolors as bc
from menus import base, demo

class BSMainMenu(base.BlackfellShell):
    def __init__(self):
        super().__init__()
        self.prompt = "BS > "
        self.intro = self.generate_banner()
        self.root_menu = self
        self.listeners = []
        #Global options
        self.global_options = {
                'LHOST' : '',
                'LOOT_DIR' : 'BS-loot/',
                'LOOT_FILE' : 'loot.yml',
                'RSA_KEY' : 'bs.pem'
                }
        #Configure the default LHOST setting
        self.get_network()
        self.check_key()
        self.defaults = {}
        for key, value in self.global_options.items():
            self.defaults[key] = value

    ################# COMMANDS #######################

    #List commands - Inherit is fine

    #Set commands
    def do_set(self, line):
        """Setting of a global option associated with the root menu."""

        option, value, line = self.parseline(line)
        if not option in self.global_options:
            bc.warn_print("[!] ", "- {} not a valid option!".format(option))
        else:
            self.global_options[option] = value
            bc.blue_print("[-] ", "{} set to: {}".format(option, value))

    def help_set(self):
        """Function to print help for this specific command."""

        print("")
        bc.blue_print('[-] ','Set global options and default values.')
        print('Example:')
        print('\tset LHOST 192.168.1.100')
        print('\tset LOOT_DIR ./custom_loot/')
        print('\tset LOOT_FILE ./custom_loot/my_loot_brings_all_the_boys.yml')
        print("")

    def complete_set(self, text, line, begidx, endidx):
        """Function to return settings matches for this command."""

        _AVAILABLE_LISTS = list(self.global_options.keys())
        return [i for i in _AVAILABLE_LISTS if i.startswith(text)]

    #Kill commands - Inherit is fine

    #Info commands
    def do_info(self, line):
        """Show global settings associted with the root menu"""

        info_list=[]
        for option, value in self.global_options.items():
            default = self.defaults[option] if option in self.defaults else None
            info_list.append([str(option), str(value), str(default)])
        bc.blue_print("[-] ", "Showing global idefault settings:\n")
        w, h = os.get_terminal_size()
        w = 0.9*w #Scale for beauty
        format_string = "{{:<{}}} {{:<{}}} {{:<{}}}".format(
                int(0.3*w), int(0.55*w), int(0.15*w))
        #format_string = "{:<25} {:<45} {:<10}"
        underline = "=" * int(w)
        bc.bold_print(format_string.format("Option", "Value", "Default"), "")
        bc.blue_print(underline, "")
        for option in info_list:
            print(format_string.format(option[0], option[1], option[2]))
        print("")

    def help_info(self):
        """Function to print help for this specific command."""

        print("")
        bc.blue_print('[-] ','Show info on global defaults, not required, but useful.')
        print("")

    #Reset commands
    def do_reset(self, line):
        """reset a global option back to the default"""

        try:
            self.global_options[line] = self.defaults[line]
            #If we're resetting keys, also check & generate if needed
            if line == 'RSA_KEY':
                self.check_key(self)
        except Exception as e:
            bc.err_print("[!] ", "- Exception when setting {} :\n\t{}".format(line, e))

    def help_reset(self):
        """Function to print help for this specific command."""

        print("")
        bc.blue_print('[-] ','Reset a global option.')
        print('Example:')
        print('\treset LOOT_DIR')
        print('\treset LHOST')
        print("")

    def complete_reset(self, text, line, begidx, endidx):
        """Function to return settings matches for this command."""

        _AVAILABLE_LISTS = list(self.global_options.keys())
        return [i for i in _AVAILABLE_LISTS if i.startswith(text)]

    def do_use(self, line):
        """select and initialise a BS module, will find module specs
        and load the associated python file for configuration."""

        cmd, args, line = self.parseline(line)
        bc.blue_print("[-] ", "Using module:  {}".format(line))
        #Concatenate the use path (from base menu for modules, with the selected module name
        module_path = self.use_path + line
        #Handle calling bad modules by accident
        try:
            module_menu = mod.BSUseModuleMenu(self, module_path)
            module_menu.cmdloop()
        except Exception as e:
            bc.err_print("[!] ", "- Exception calling module, is this a real module? Check module guidance.\n\t{}".format(e))


    ################## SUBMENUS #######################

    #Listeners submenu
    def do_listeners(self, line):
        """Switch to listeners menu, to allow listener only configuration."""

        print("")
        self.lnr = lnrs.BSListenersMenu(self)
        self.lnr.cmdloop()

    def help_listeners(self):
        """Function to print help for this specific command."""

        print("")
        bc.blue_print('[-] ','Switch to a Listener context menu, to set up your listeners.')
        print("")

    #Agents Submenu
    def do_agents(self, line):
        """Switch to agents menu, to allow agent only configuration."""

        print("")
        self.agt = agts.BSAgentsMenu(self)
        self.agt.cmdloop()

    def help_agents(self):
        """Function to print help for this specific command."""

        print("")
        bc.blue_print('[-] ','Switch to an Agents context menu, to manage your active agents.')
        print("")

    ################## DEMO ########################

    def do_demo(self, line):
        """Walkthrough BShell key functions within the interpreter"""
        input_str = bc.warn_format("[-]", " This will run through a demo of the BlackfellShell for a couple of minutes, do you want to continue? [Y/n]:")
        if '-y' not in line and input(input_str.format(line)).lower() not in ['y', 'yes', 'ye']:
            return False
        else:
            demo.demo()




    ################# UTILS ########################

    #Inherit - shell  & default

    def get_network(self):
        """Get network interface information to auto-populate listener settings"""

        test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            test_sock.connect(("1.1.1.1", 1))
            self.global_options['LHOST'] = test_sock.getsockname()[0]
        except:
            bc.warn_print("[!] ", "- Error setting global LHOST, check network settings")
            self.global_options['LHOST'] = ""
        finally:
            test_sock.close()

    def generate_key(self):
        """Generate an RSA key for the shell."""

        q = "No valid key found at: {}, create one? [y/n] : ".format(self.global_options['RSA_KEY'])
        if input(q).lower() not in ['y', 'yes', 'ye']:
            bc.err("Encryption operations may fail, try setting RSA key in home menu.")
        else:
            key = RSA.generate(2048)
            with open(self.global_options['RSA_KEY'], 'wb') as f:
                f.write(key.export_key('PEM'))

    def check_key(self):
        """Check that the shell has an RSA key that can be used in
        future functionality"""

        if not os.path.exists(self.global_options['RSA_KEY']):
            self.generate_key()
        else:
            with open(self.global_options['RSA_KEY']) as f:
                try:
                    key = RSA.import_key(f.read())
                    bc.success("RSA Key {} valid.".format(self.global_options['RSA_KEY']))
                except Exception as e:
                    bc.err("Key: {} not valid : {}".format(self.global_options['RSA_KEY'], e))
                    self.generate_key()

    def generate_banner(self):
        """Return ascii art banner, eventually will return random,
        for now just returns one main banner, until more are made"""

        b1 =  """
                             /\\
                            /^^\_
                    /\     /^^^^^\\
                   /^^|   /^^^^^^^\_
                  /^^^^\_/^^^^^^^^^^\\
                _/  \ /    /  |  \   \\
               /   /   \    |  \    \ \\
              /                        \\
             /   $    $   /     $  $    |
            / $  |  $ |    $    |  |  $  \\
           /  |  $  |   $  |$  $    $ |$  \\
        ######################################
        #              WELCOME!              #
        #                                    #
        #       To the Blackfell Shell       #
        #                 by                 #
        #             @blackf3ll             #
        #         info@blackfell.net         #
        #                                    #
        ######################################
"""
        b2 = bc.blue_format("""
                     .ooooooo...
                  .oo8888888888888ooo.
                 .o88888888888888888888o
                .8888**            *8888.
                8888*               *8888.
              .888.                 8888.
             .888                  .888.
             8888.               .8888.
           .8888oo.           ..8888
          .888888888oooo888888888*
          888888888888888888888888.
         .888888**         **888888.
         88888*              *888888.
        8888*                8888888.    __     __    ___  __ _  ____  ____  __    __
       .8888                 8888888*   (  )   / _\  / __)(  / )(  __)(  __)(  )  (  )
       88888                 8888888*   / (_/\/    \( (__  )  (  ) _)  ) _) / (_/\/ (_/\\
      .88888                8888888*    \____/\_/\_/ \___)(__\_)(__)  (____)\____/\____/
      888888.         ..oo8888888*
     *88888888888888888888888888*    ..ood888888888888bo..
      *8888888888888888888888*     .88888888888888888888888.
       *oo888888ooooo****         .88888**************888888.
                                 .888**                  **888
                                 8888                      *88
                                 8888.                      8*
                                  *888..
                                    *888888oo.
                                        *888888888888oo..
                                           **888888888888888..
                                                 ***88888888888.
                                                        *8888888.
                                                         88888888
                                                         88888888
                                 8                      88888888  _  _  ____  __    __
                                88                    .o8888888* / )( \(  __)(  )  (  )
                              .8888.              ..oo88888888*  ) __ ( ) _) / (_/\/ (_/\\
                             .88888o....  ...oo8888888888888*    \_)(_/(____)\____/\____/
                            .888888888888888888888888888*
                            **8888888888888888888**
                               ***o8888o***


""", "")
        return b2


def main():
    bc.err_print("[!] ", "- You're running the Main Menu as __main__, did you mean to?")

if __name__ == '__main__':
        main()
