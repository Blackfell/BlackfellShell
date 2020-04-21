#!/usr/bin/python3

import cmd
import os

from menus import base
from common import bcolors as bc
from menus import listeners as lnrs
from menus import interact as intr
from menus import modules as mod

class BSAgentsMenu(base.BlackfellShell):
    def __init__(self, parent_menu):
        super(BSAgentsMenu, self).__init__()
        append = " : " + bc.green_format(bc.bold_format("Agents "), "> ")
        self.prompt = parent_menu.prompt[:2] + append
        self.root_menu = parent_menu.root_menu
        self.q = self.root_menu.q

    ################# COMMANDS #######################

    #List commands
    def do_list(self, line):
        self.root_menu.list_agents()

    def help_list(self):
        print("")
        bc.blue_print('[-] ','List Agents only cos we\'re in agents now.')
        print('Example:')
        print('\tlist')
        print('\t\tAgent-1 : an agent.')
        print("")

    #Kill commands
    def do_kill(self, line):
        if not line:
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
        print("")
        bc.blue_print('[-] ','Kill an agent.')
        print('Example:')
        print('\tkill Agent-2')
        print("")

    def complete_kill(self, text, line, begidx, endidx):
        return [i for i in self.enum_agents() if i.startswith(text)]

    '''
    def enum_agents(self):
        _AVAILABLE_LISTS = []
        for l in self.root_menu.listeners:
            for a in l.agent_list:
                _AVAILABLE_LISTS.append(a.name)
        return [i for i in _AVAILABLE_LISTS if i.startswith(text)]
    '''

    #Info commands
    def do_info(self, line):
        print("")
        bc.blue_print("[-] ", "Showing info for agent: {}\n".format(line))

    def help_info(self):
        print("")
        bc.blue_print('[-] ','Show information on an agent.')
        print('Example:')
        print('\tinfo Agent-2')
        print("")

    def complete_info(self, text, line, begidx, endidx):
        _AVAILABLE_LISTS = ('TODO - proper dynamic agent completion')
        return [i for i in _AVAILABLE_LISTS if i.startswith(text)]

    #Activeate commands
    def do_activate(self, line):
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
        print("")
        bc.blue_print('[-] ','Activate an agent, so that it can be interacted with.')
        print('Example:')
        print('\tactivate Agent-2')
        print("")

    def complete_activate(self, text, line, begidx, endidx):
        return [i for i in self.enum_agents() if i.startswith(text)]

    #Deactivate commands
    def do_deactivate(self, line):
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
        print("")
        bc.blue_print('[-] ','Deactivate an agent, so that it can be interacted with.')
        print('Example:')
        print('\tdeactivate Agent-2')
        print("")

    def complete_deactivate(self, text, line, begidx, endidx):
        return [i for i in self.enum_agents() if i.startswith(text)]

    #Interact commands
    def do_interact(self, line):
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
        print("")
        bc.blue_print('[-] ','Interact with all activated agents.')
        print("")

    def complete_interact(self, text, line, begidx, endidx):
        return [i for i in self.enum_agents() if i.startswith(text) ]

    def do_use(self, line):
        cmd, args, line = self.parseline(line)
        bc.blue_print("[-] ", "Using module:  {}".format(line))
        #Concatenate the use path (from base menu for modules, with the selected module name
        module_path = self.use_path + line
        #Handle calling bad modules by accident
        self.module_menu = mod.BSUseModuleMenu(self, module_path)
        self.module_menu.cmdloop()
        try:
            #module_menu = mod.BSUseModuleMenu(self, module_path)
            #module_menu.cmdloop()
            pass
        except Exception as e:
            bc.err_print("[!] ", "- Exception calling module, is this a real module? Check module guidance.\n\t{}".format(e))


    ############## SUBMENU STUFF ###################

    #Listeners submenu
    def do_listeners(self, line):
        print("")
        lnr = lnrs.BSListenersMenu(self)
        lnr.cmdloop()
        return True

    def help_listeners(self):
        print("")
        bc.blue_print('[-] ','Switch to a Listener context menu, to set up your listeners.')
        print("")

    #Agents Submenu
    #def do_agents(self, line):
    #    pass

    #Payloads submenus
    def do_payloads(self, line):
        print("")
        bc.blue_print("[-] ", "Would now switch to Payloads  menu")
        print("")
        #pld = BlackfellShellPayloads()
        #pld.cmdloop()

    def help_payloads(self):
        print("")
        bc.blue_print('[-] ','Switch to a Payloads context menu, to generate listeners or implants.')
        print("")

    #TODO - reload modules


    ################# UTILS ########################



    #Inherit shell, post_loop,  default

    def do_back(self, line):
        'Exit this submenu - back to main menu.'
        return True


def main():
    print("Did you mean to run the agents menu as main, really?")

if __name__ == '__main__':
        main()
