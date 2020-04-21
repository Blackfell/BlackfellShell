#!/usr/bin/python3

import time
import os

from Crypto.PublicKey import RSA

from resources.listeners import bs_tcp as lnr
from common import module as mod
from common import bcolors as bc

class BSModule(mod.BSModule):
    def __init__(self, parent_menu):
        super().__init__()
        #module atts
        self.parent_menu = parent_menu
        self.root_menu = parent_menu.root_menu
        self.description = '''
        TCP Listener for the Blackfell Shell implant. Can handle multiple shell connections concurrently.
        '''

        #List YOUR class setup & attributes here
        self.add_setting('LHOST', self.root_menu.global_options['LHOST'], True)
        self.add_setting('LPORT', 443, True)
        self.add_setting('max_conns',100, False)
        self.add_setting('LOOT_DIR', self.root_menu.global_options['LOOT_DIR'], False)
        self.add_setting('name', "lnr-{}".format(len(self.root_menu.listeners) + 1), False)
        self.add_setting('RSA_KEY', self.root_menu.global_options['RSA_KEY'], True)

    def setup(self):
        """Method to test any module settings are aceptable before execution. Types, ranges etc."""
        #Override this with any pre-module tests you need
        try:
            self.set_option('LPORT', int(self.get_option('LPORT')))
        except:
            bc.err("LPORT invalid - must be integer. Cannot autoconvert.")
            return False
        #Max conns as integer
        try:
            self.set_option('max_conns', int(self.get_option('max_conns')))
        except:
            bc.err("max_conns invalid - must be integer. Cannot autoconvert.")
            return False
        #Check exit on exec
        if not isinstance(self.get_option('exit_on_exec'), bool):
            if self.get_option('exit_on_exec') == 'False':
                self.set_option('exit_on_exec', False)
            elif self.get_option('exit_on_exec') == 'True':
                self.set_option('exit_on_exec', True)
            else:
                bc.err("exit_on_exec invalid, must be boolean.")
                return False
        #Check listener name is unique
        for l in self.root_menu.listeners:
            if self.get_option('name') == l.name:
                bc.err("Listener name {} already registered. Pick another".format(self.options['name']))
                return False
        #Check if RSA Key valid
        if not os.path.exists(self.get_option('RSA_KEY')):
            bc.err("RSA Key {} not found".format(self.get_option('RSA_KEY')))
            return False
        else:
            with open(self.get_option('RSA_KEY')) as f:
                try:
                    key = RSA.import_key(f.read())
                except Exception as e:
                    bc.err("Key: {} not valid : {}".format(self.get_option('RSA_KEY'), e))
                    return False
        return True

    def run(self):
        """The main function called when the module executes"""
        #Override with what to do with this class when it runs
        exit_on_exec, LHOST, LPORT, max_conns, LOOT_DIR, name, RSA = [
                i['value'] for i in self.options.values() ]
        l = lnr.BSTCPListener(exit_on_exec, LHOST, LPORT, max_conns, LOOT_DIR, name, RSA)   #TODO - put listener resources in the right place!
        l.start()
        time.sleep(1.5)   #Wait for thread to start
        if l.success == True:
            self.root_menu.listeners.append(l)
            bc.success("Module executed.")
        else:
            bc.err("Run, but success flag not set. Check your listener status!")
            try:
                self.root_menu.listeners.append(l)
            except Exception as e:
                bc.warn("Could not register listener.")
        if self.get_option('exit_on_exec') and l.success:  #Add success criteria - we want to stay in if fail
            return True
        else:
            #Also - increment listener ID so we can crank out many more!!
            self.set_option('name',"listener-{}".format(len(self.root_menu.listeners) + 1))
            return False


def main():
    print("You're running the bs_tcp listener  module as main, did you mean to?")

if __name__ == '__main__':
    main()
