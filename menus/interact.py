#!/usr/bin/python3

import cmd
import os
import glob
import importlib
import time
import yaml

from types import MethodType

from menus import base
from common import bcolors as bc
from common import importer

class BSInteractMenu(base.BlackfellShell):
    """Main menu class, inherited for agent interaction specifically"""

    def __init__(self, parent_menu, agents):
        super(BSInteractMenu, self).__init__()
        self.root_menu = parent_menu.root_menu
        self.q = self.root_menu.q
        self.active_agents = []
        self.methods = {
                'do_back' : 'Stop interacting and return to previous menu.',
                'do_exit' : 'Alias for back, return to previous menu.',
                'do_info' : 'Provide information on current interaction.'
                }
        self.loaded_methods = {}
        self.method_help = {}
        self.get_active_agents(agents)
        self.get_load_path()
        self.check_loaded()
        append = " : " + bc.green_format(bc.bold_format("Interacting - {} Agents ".format(len(self.active_agents))), "> ")
        self.base_prompt = parent_menu.prompt[:2] + append
        self.prompt = self.base_prompt


    ################# INIT METHODS ###################

    def get_load_path(self):
        """Get the load path for each agent, checking that they don't clash"""

        last_lp = None
        lp = None
        for agent in self.active_agents:
            last_lp = lp
            lp = agent.load_path
            if last_lp and last_lp != lp:
                bc.err_print("[!] ", "- Your agents have different load paths, have you actiated different types of agent?")
                self.do_exit('exit')
        self.load_path = lp

    #Check loaded module status and populate internal variables
    def check_loaded(self):
        """Check all loaded commands and methods, reporting on any clashes"""

        try:
            ##print("Checking loaded")
            loaded_methods = {}
            help = {}
            for agent in self.active_agents:
                for mod in agent.modules.keys():
                    #print("DEBUG _ TRying to add to loaded methods: {}\n adding help for {}\n from {}".format(loaded_methods, mod, agent.modules))
                    loaded_methods[mod] = agent.modules[mod]['help']
                    help[mod] = agent.modules[mod]['commands']
            #print("Check loaded retunred: {}".format(loaded_methods))
            #Finally, set the global loaded methods variable
            self.loaded_methods = loaded_methods
            for h in help.values():
                for cmd, hlp in h.items():
                    self.method_help[cmd] = hlp
            #Now check if any agents are missing a methods
            for agent in self.active_agents:
                for mod, meths in self.loaded_methods.items():
                    #print("DEBUG - Agent: {} module: {}, methods: {}".format(agent.name, mod, meths))
                    if mod not in agent.modules:
                        bc.warn_print("\n[!] ", "- Agent: {} missing module: {}.\n".format(agent.name, mod))
                        return False
            #print("DEBUG - loaded_methods: {}".format(self.loaded_methods))
        except:
            bc.err_print("[!] ", "Error checking loaded modules, are some agents missing modules?")

    def get_active_agents(self, agents):
        """Given an agent list, add to class variable."""

        for l in self.root_menu.listeners:
            for a in l.agent_list:
                if a in agents:
                    self.active_agents.append(a)

    ################# COMMANDS #######################

    #Info commands
    def do_info(self, line):
        """Simply list out agents currently interacted on."""

        for agent in self.active_agents:
            bc.blue_print("[-] ", "Acting on agent: {}, which is alive: {}".format(agent.name, agent.is_alive()))

    def help_info(self):
        """Function to print help for this specific command."""

        bc.blue_print('\n[-] ','Show information on current agents.\n')

    def do_load(self, line):
        """Load a module into agent, implant or menu, based off module spec
        files, which are found and loaded into the menu, agent and implant
        as needed."""

        if not line:
            bc.warn_print("[!] ", "No module specified.")
            return
        try:
            #Load module functionality into agent(s)
            module_spec = self.load_path + line +'.yml'
            bc.blue_print("[+] ", "- Loading module: {}".format(line))
            with open(module_spec) as f:
                ms = yaml.load(f, Loader=yaml.FullLoader)

            #Menu modules not often loaded, so check before you load.
            for m in ms['methods']:
                if m['menu']:
                    self.load_methods(ms)

            for agent in self.active_agents:
                #agent.load_agent_methods(ms)
                agent.send_q.put('load_agent_methods ')
                agent.send_q.put(ms)
                time.sleep(1)   #Let agent catch up, smooths experience for user
            self.check_loaded()
            bc.blue_print("[+] ", "Load command sent.")
            ms = '' #reset variable


        #Now load agent and implant modules
        except Exception as e:
            bc.err_print("[!] ", "- Exception loading menu module:\n{}".format(e))
        finally:
            self.check_loaded()

    def complete_load(self, text, line, begidx, endidx):
        """return module spec files that can be loaded into the active agents"""

        text = self.load_path + text
        if os.path.isdir(text):
            sm = base.scrub_matched(glob.glob(os.path.join(text, '*')), len(self.load_path))
            return sm
        else:
            sm = base.scrub_matched(glob.glob(text + '*'), len(self.load_path))
            return sm


    def do_help(self, line):
        """Function to print help for this specific command."""


        if line in self.method_help.keys():
            bc.blue_print("\n[-] ",  self.method_help[line])
            print("")
        elif "help_" + line in dir(self):
            try:
                caller = getattr(self, 'help_' + line)
                caller()
            except:
                bc.err_print("[!] ", "- Error, helop for {} not implemented correctly".format(line))
        else:
            self.print_loaded_methods()


    def default(self, line):
        """Gets called if no agent method is loaded, will send command
        down to implant for processing."""

        for agent in self.active_agents:
            try:
                agent.send_q.put(line)
                time.sleep(0.5) #time to let the agent process
            except Exception as e:
                bc.err_print("[!] ", "- Exception calling agent method {} on agent {}:\n\t{}".format(line, agent.name, e))


    ################# UTILS ########################

    #Module loading method helpers
    def load_methods(self, mod_spec):
        """Actually does the loading of menu methods to the interact menu.
        Not yet really used, but may develop menu methods in future."""

        for method in (i for i in mod_spec['methods'] if i['menu']):
            import_dict = {method['name'] : ''}
            filename = mod_spec['load_dir'] + method['menu']
            with open(filename, 'r') as f:
                for line in f:
                    import_dict[method['name']] += line
            imported_mod = importer.bs_import(import_dict)
            for func in imported_mod[1]:
                try:
                    g = getattr(self, func)
                    bc.err("Error, method already exists in the menu!\n{}".format(g))
                except:
                    #It's not there, let's make it
                    setattr(self, func, MethodType(eval('imported_mod[0].' + func), self))
                    self.methods['do_' + method['name']] = method['help']

    #Inherit shell, post_loop,
    def print_loaded_methods(self):
        """Rationalises and prints methods loaded into the agents
        REports on any descrepancies to the user between agents."""

        bc.green_print("[-] ", "Menu options:\n")
        format_string = "\t{:<15} {:<50}"
        underline = "\t" + "=" * 70
        bc.bold_print(format_string.format("Method", "Description"), "")
        bc.blue_print(underline, "")
        for nme, hlp in self.methods.items():
            print(format_string.format(str(nme[3:]), hlp))
        bc.green_print("\n[-] ", "Loaded agent options:")

        self.check_loaded()
        for mod, meths in self.loaded_methods.items():
            bc.green_print("\n\t[-] ", "{} Methods:\n".format(mod.title()))
            bc.bold_print(format_string.format("Method", "Description"), "")
            bc.blue_print(underline, "")
            for meth in meths:
                print(format_string.format(meth[0], meth[1]))
        print("")

    def completenames(self, text, *ignored):
        """Returns all available methods, be they menu, agent or
        implant methods, to allow tab completion."""

        #Inherit from parent class, but not kill, list or sleep
        blacklist_methods = ['kill', 'list', 'sleep']
        a = super().completenames(text, *ignored)
        #Agent methods
        b = []
        for meths in self.loaded_methods.values():
            for meth in meths:
                if meth[0] not in a and meth[0].startswith(text):
                    b.append(meth[0])
                else:
                    pass
        #Menu methods
        c=[]
        for nme in self.methods.keys():
            if str(nme[3:]).startswith(text):
                c.append(str(nme[3:]))
        return [opt for opt in (a+b+c) if opt not in blacklist_methods]

    def do_back(self, line):
        'Exit this submenu - back to main menu.'
        return True

    #################### Overrides #####################

    #Because the interact menu is speacial :)

    def do_list(self,line):
        """Alias for info to show agents acting on."""

        #In case someone does it out of habit!
        self.do_info(line)

    def do_sleep(self, line):
        """Override the menu sleep method and send sleep to the implant
        to allow implant sleep processing."""

        self.default('sleep ' + line)

    def do_kill(self, line):
        """Override the menu kill method to send kill to the implant
        for processing."""

        self.default('kill ' + line)

    def do_shell(self, line):
        """Override the inherited shell method, we now want shell to
        do the default menu behaviour, not execute local shell"""

        self.default('shell ' + line)


def main():
    print("Did you mean to run the agents menu as main, really?")

if __name__ == '__main__':
        main()
