#!/usr/bin/python3

import cmd
import os
import readline
import glob

from menus import base
from common import bcolors as bc
from menus import agents as agts
from menus import modules as mod

class BSListenersMenu(base.BlackfellShell):
    """Overridden base menu class for listener configuration etc."""

    def __init__(self, parent_menu):
        super(BSListenersMenu, self).__init__()
        append = " : " + bc.green_format(bc.bold_format("Listeners "), "> ")
        self.prompt = parent_menu.prompt[:2] + append
        self.root_menu = parent_menu.root_menu
        self.q = self.root_menu.q
        self.use_path = parent_menu.use_path + 'listeners/'
        readline.set_completer_delims(' \t\n')

    ################# COMMANDS #######################

    #List commands
    def do_list(self, line):
        """Overridden base list commmand, for listeners only now"""
        self.root_menu.list_listeners()

    def help_list(self):
        """Function to print help for this specific command."""
        print("")
        bc.blue_print('[-] ','List listeners only cos we\re in listeners now.')
        print('Example:')
        print('\tlist')
        print('\t\tListener-1 : a listener.')
        print("")

    #Kill commands
    def do_kill(self, line):
        """OVerridden kill method, acting only on listeners in this context"""
        if not line:
            input_str = bc.warn_format("[!]", " Do you want to kill all listeners? [Y/n]:")
            if input(input_str.format(line)).lower() not in ['y', 'yes', 'ye']:
                return
        for l in self.root_menu.listeners:
            if line in l.name:
                l.terminate()
            #It's not our listener
            else:
                bc.warn("Listener not found, not terminating.")

    def help_kill(self):
        """Function to print help for this specific command."""
        print("")
        bc.blue_print('[-] ','Kill a listener.')
        print('Example:')
        print('\tkill Listener-2')
        print("")

    def complete_kill(self, text, line, begidx, endidx):
        """Returns list of listers to allow tab completion of kill commands"""
        return [i for i in self.enum_listeners() if i.startswith(text)]


    ############## SUBMENU STUFF ###################

    #Agents Submenu
    def do_agents(self, line):
        """SWitch to agents menu"""
        print("")
        agt = agts.BSAgentsMenu(self)
        agt.cmdloop()
        return True

    def help_agents(self):
        """Function to print help for this specific command."""
        print("")
        bc.blue_print('[-] ','Switch to an Agents context menu, to manage your active agents.')
        print("")

    def do_use(self, line):
        """Overridden use method, now using listener modules only"""
        cmd, args, line = self.parseline(line)
        bc.blue_print("[-] ", "Using listener:  {}".format(line))
        #Concatenate the use path (from base menu for modules, with the selected module name
        module_path = self.use_path + line
        #Handle calling bad modules by accident
        try:
            module_menu = mod.BSUseModuleMenu(self, module_path)
            module_menu.cmdloop()
        except Exception as e:
            bc.err_print("[!] ", "- Exception calling module, is this a real module? Check module guidance.\n\t{}".format(e))


    def help_use(self):
        """Function to print help for this specific command."""
        print("")
        bc.blue_print('[-] ','Select a listener to run.')
        print('Example:')
        print('\tuse bs_http')
        print('\tuse bs_http')
        print("")
        #TODO - modules/droppers/exploits

    def complete_use(self, text, line, begidx, endidx):
        """Return listener module paths to allow tab completion of listeners"""
        text = self.use_path + text
        if os.path.isdir(text):
            sm = base.scrub_matched(glob.glob(os.path.join(text, '*')) , len(self.use_path) )
            return sm
        else:
            sm = base.scrub_matched(glob.glob(text + '*'), len(self.use_path))
            return sm


    ################# UTILS ########################

    #Inherit shell, post_loop,  default


    def do_back(self, line):
        'Exit this submenu - back to main menu.'
        return True



def main():
    print("Did you mean to run the listener menu as main, really?")

if __name__ == '__main__':
        main()
