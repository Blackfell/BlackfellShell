#!/usr/bin/python3

import cmd
import os

from menus import base
from common import bcolors as bc
from menus import listeners as lnrs
from menus import interact as intr
from menus import modules as mod

class BSAgentsMenu(base.BlackfellShell):
    """Overridden base menu in the agent configuration and management context"""

    def __init__(self, parent_menu):
        super(BSAgentsMenu, self).__init__()
        append = " : " + bc.green_format(bc.bold_format("Agents "), "> ")
        self.prompt = parent_menu.prompt[:2] + append
        self.root_menu = parent_menu.root_menu
        self.q = self.root_menu.q

    ################# COMMANDS #######################

    #List commands
    def do_list(self, line):
        """Overriden version of the base list function, this version
        simply excludes the listing of listeners since we're in the
        agent menu now."""

        self.root_menu.list_agents()

    def help_list(self):
        """Function to print help for this specific command."""

        print("")
        bc.blue_print('[-] ','List Agents only cos we\'re in agents now.')
        print('Example:')
        print('\tlist')
        print('\t\tAgent-1 : an agent.')
        print("")

    #Kill commands
    def do_kill(self, line):
        """Overridden version of the base kill function, this version
        only kills agents since we're in the agent menu now."""

        if not line or line == "*":
            input_str = bc.warn_format("[!]", " Do you want to kill all agents? [Y/n]:")
            if input(input_str.format(line)).lower() not in ['y', 'yes', 'ye']:
                return
        for l in self.root_menu.listeners:
            for a in l.agent_list:
                if line in a.name:
                    l.terminate_agent(a)
                #It's not our listener
                else:
                    bc.warn("Agent not found, not terminating.")

    def help_kill(self):
        """Function to print help for this specific command."""

        print("")
        bc.blue_print('[-] ','Kill an agent.')
        print('Example:')
        print('\tkill Agent-2')
        print("")

    def complete_kill(self, text, line, begidx, endidx):
        """Function to return all active agents."""

        return [i for i in self.enum_agents() if i.startswith(text)]

    #Activeate commands - TODO - change this from a variable to Event()
    def do_activate(self, line):
        """Activates agents, by setting an active flag. Interact commands
        will start an interaction with any agents that have been activated."""

        act = "*" if line == "" else line
        bc.info("Activating: {}".format(act))
        for l in self.root_menu.listeners:
            for a in l.agent_list:
                if line in a.name:
                    a.active = True
                #It's not our listener
                else:
                    pass

    def help_activate(self):
        """Function to print help for this specific command."""

        print("")
        bc.blue_print('[-] ','Activate an agent, so that it can be interacted with.')
        print('Example:')
        print('\tactivate Agent-2')
        print("")

    def complete_activate(self, text, line, begidx, endidx):
        """Function to return all agents associated with the shell."""

        return [i for i in self.enum_agents() if i.startswith(text)]

    #Deactivate commands
    def do_deactivate(self, line):
        """Unsets the active flag in a given agent, so that when interact
        starts, this agent isn't included in the interaction."""

        act = "*" if line == "" else line
        bc.info("Deactivating: {}".format(act))
        for l in self.root_menu.listeners:
            for a in l.agent_list:
                if line in a.name:
                    a.active = False
                #It's not our listener
                else:
                    pass

    def help_deactivate(self):
        """Function to print help for this specific command."""

        print("")
        bc.blue_print('[-] ','Deactivate an agent, so that it can be interacted with.')
        print('Example:')
        print('\tdeactivate Agent-2')
        print("")

    def complete_deactivate(self, text, line, begidx, endidx):
        """Function to return all activated agents in this menu."""

        return [i for i in self.enum_agents() if i.startswith(text)]

    #Interact commands
    def do_interact(self, line):
        """Opens an interact menu and starts an interactive interpreter with
        all agents whose active flag is set."""

        if not line:
            agents = []
            for l in self.root_menu.listeners:
                for a in l.agent_list:
                    if a.isAlive() == 1 and a.active:
                         agents.append(a)
            bc.blue_print("[+] ", "- Interacting with {} active agents".format(len(agents)))
            interact = intr.BSInteractMenu(self, agents)
            interact.cmdloop()
        else:
            if line in self.enum_agents():
                bc.blue_print("[+] ", "- Interacting with {}".format(line))
                interact = intr.BSInteractMenu(self, [line])
                interact.cmdloop()
            else:
                bc.err_print("[!] ", "- Error - Agent {} not available.".format(line))


    def help_interact(self):
        """Function to print help for this specific command."""

        print("")
        bc.blue_print('[-] ','Interact with all activated agents.')
        print("")

    def complete_interact(self, text, line, begidx, endidx):
        """Function to return all activated agents in this menu."""

        return [i for i in self.enum_agents() if i.startswith(text) ]

    ############## SUBMENU STUFF ###################

    #Listeners submenu
    def do_listeners(self, line):
        """Switch to listeners menu, to allow listener configuration."""

        print("")
        lnr = lnrs.BSListenersMenu(self)
        lnr.cmdloop()
        return True

    def help_listeners(self):
        """Function to print help for this specific command."""

        print("")
        bc.blue_print('[-] ','Switch to a Listener context menu, to set up your listeners.')
        print("")

    ################# UTILS ########################

    #Inherit shell, post_loop,  default

    def do_back(self, line):
        'Exit this submenu - back to main menu.'

        return True


def main():
    print("Did you mean to run the agents menu as main, really?")

if __name__ == '__main__':
        main()
