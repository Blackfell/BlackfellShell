#!/usr/bin/python3

import cmd
import os
import importlib

from menus import base
from common import bcolors as bc

class BSUseModuleMenu(base.BlackfellShell):
    """Module menu, used to configure and deploy modules"""

    def __init__(self, parent_menu, module_path, module_friendly_path=None):
        super().__init__()
        self.module_path = module_path
        self.parent_menu = parent_menu      #This is the menu the module was launched from - TODO - change to root menu
        self.root_menu = self.parent_menu.root_menu
        self.q = self.root_menu.q
        if not module_friendly_path:
            self.module_friendly_path = self.module_path
        else:
            self.module_friendly_path = module_friendly_path
        append = " : " + bc.green_format(bc.bold_format(self.module_friendly_path), " > ")
        self.prompt = parent_menu.prompt[:2] + append
        self.set_up_module()

    def format_import_path(self):
        """Changes a module file path into a dot delimited string,
        which can be used in an import statement"""

        path_string = ""
        for i in self.module_path.split('/'):
            for j in i.split('\\'):  #Because windows path completion
                path_string += (j + '.')
        self.module_path = path_string[:-1]  #remove trailing dot
        #print("Module path got: {}".format(self.module_path))

    def set_up_module(self):
        """Setup functionality used to get module impormation and
        import the module code ready for running"""

        #Make sure import path is formatted
        self.format_import_path()
        imp = importlib.import_module(self.module_path)
        importlib.reload(imp)
        self.module_import = imp
        self.module_instance = self.module_import.BSModule(self)
        print(self.module_instance.description )


    ################# COMMANDS #######################

    #Set commands
    def do_set(self, line):
        """Set a module option, using the set_option method
        in the module itself"""

        cmd, args, line =  self.parseline(line)
        try:
            if self.module_instance.set_option(cmd, args) and args:
            #TODO - do menu - side verification of this
            #Like - if self.module_instance.set_attr(cmd, args) and getattr(self.module_instance.options, cmd)['value'] == args:
                bc.green_print("[-] ", "- {} set successfully to {}.".format(cmd, args))
            elif not args:
                bc.warn_print("[!] ", "- No value provided.")
            else:
                bc.err_print("[!] ", "- Error, {} could not be set to {}".format(cmd, args))
        except Exception as e:
            bc.err_print("\n[!] ", "- Exception whilst setting {}:\n{}\n".format(cmd, e))

    def help_set(self):
        """Help information for the set command"""

        print("")
        bc.blue_print('[-] ','Set module options and default values.')
        print('Example:')
        print('\tset LPORT 80')
        print('\tset NAME Windows-Server-19')
        print("")

    def complete_set(self, text, line, begidx, endidx):
        """Returns a list of module options to enable tab completion """

        _AVAILABLE_LISTS = self.module_instance.get_options()
        return [i for i in _AVAILABLE_LISTS if i.startswith(text)]

    #Reset commands
    def do_reset(self, line):
        """sets an option back to the option configured as module default"""

        #No parsing required as no arguments for this one
        try:
            if self.module_instance.reset_option(line):
            #TODO - do menu - side verification of this
            #Like - if self.module_instance.set_attr(cmd, args) and getattr(self.module_instance.options, cmd)['value'] == args:
                bc.green_print("[-] ", "- Reset successfully.")
            else:
                bc.err_print("\n[!] ", "- Error, {} could not be reset.\n".format(line))
        except Exception as e:
            bc.err_print("\n[!] ", "- Exception whilst resetting {}:\n{}\n".format(cmd, e))
    def help_reset(self):
        print("")
        bc.blue_print('[-] ','Reset agent options and default values.')
        print('Example:')
        print('\treset name')
        print('\treset LHOST')
        print("")

    def complete_reset(self, text, line, begidx, endidx):
        """Returns a list of module options to enable tab completion """

        _AVAILABLE_LISTS = self.module_instance.get_options()
        return [i for i in _AVAILABLE_LISTS if i.startswith(text)]

    #Info commands
    def do_info(self, line):
        """Shows all settings, along with default and current values to user"""

        print("")
        bc.blue_print("[-] ", "Showing info for module:\n")
        format_string = "{:<20} {:<40} {:<30} {:<10}"
        underline = "=" * 102
        bc.bold_print(format_string.format("Option", "Value", "Default", "Required?"), "")
        bc.blue_print(underline, "")
        '''
        for opt, dat in self.module_instance.options.items():
            default =
            required =
            print(format_string.format(opt, str(dat), str(default) , str(required)))
        '''
        for option in self.module_instance.info():
            print(format_string.format(option[0], option[1], option[2], option[3]))
        print("")


    def help_info(self):
        """Help information for the info command"""

        print("")
        bc.blue_print('[-] ','Show information on a selected module.')
        print("")

    #Execute commands
    def do_execute(self, line):
        """runs the module, calling requirement checks and setup functions
        beforehand. Will exit if checks return False"""

        bc.blue_print("[-] ", "- Seting up module...".format(line))
        if not self.module_instance.check_required():
            bc.err_print("[!] ","- Execute failed. Some required options not set.")
            return
        if not self.module_instance.setup():
            bc.err_print("[!] ","- Module test, failed.")
            return
        bc.green_print("[!] ", "- Setup complete. Executing...")
        if self.module_instance.run():
            #Exit on true was set, module will return true and module menu will be exited.
            return True

    def help_execute(self):
        """Help text for the exit command"""

        print("")
        bc.blue_print('[-] ','Test and execute module.')
        print("")

    ############## SUBMENU STUFF ###################

    #None - there be only back from here

    ################# UTILS ########################

    #Inherit shell, post_loop,  default

    def do_back(self, line):
        'Exit this submenu - back to main menu. Will NOT exit shell'
        input_str = bc.warn_format("[-]", " Do you want to go back? Check your module ran successfully. [Y/n]:")
        if input(input_str.format(line)).lower() in ['y', 'yes', 'ye']:
            return True

def main():
    print("Did you mean to run the use module menu as main, really?")

if __name__ == '__main__':
        main()
