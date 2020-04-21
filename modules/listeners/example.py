#!/usr/bin/python3 

from common import bcolors as bc
from common import module as mod

class BSModule(mod.BSModule):
    def __init__(self):
        #put YOUR attributes here
        self.description = '''
        Example Listener Module, for use in understanding the BShell.
        
        Rather than calling a real listener, it just prints the  configuration to the console.
        '''
        self.exit_on_exec = {
                'value' : True,
                'default' : True,
                'required' : True
                }
        self.message = {
                'value' : None,
                'default' : None,
                'required' : True
                }
        self.num_prints = {
                'value' : None,
                'default' : None,
                'required' : True
                }
        self.color = {
                'value' : None,
                'default' : None,
                'required' : False
                }

        #List YOUR class attributes here
        self.options = {
                'exit_on_exec': self.exit_on_exec,
                'message' : self.message,
                'num_prints' : self.num_prints,
                'color' : self.color
                }
    
    def run(self):
        col = self.color['value']
        msg = self.message['value']
        bc.green_print("[!] ", "- Print incoming!")
        #Override with what to do with this class when it runs
        for time in range(self.num_prints['value']):
            if col == 'red':
                bc.err_print(msg, "")
            elif col == 'orange':
                bc.warn_print(msg, "")
            elif self.color['value'] == 'blue':
                bc.blue_print(msg, "")
            elif self.color['value'] == 'green':
                bc.green_print(msg, "")
            else:
                print(msg)

        if bool(self.exit_on_exec['value']) == True:
            bc.green_print("[!] ", "- Module executed, exiting.")
            return True
    
    #Override the following methods if you want custom required checks and tests
    #Default is checking all required options are at least set
    '''    
    def check_required(self):
        #This just checks an attribute is set, if you need more, write it in!
        for option in self.options:
            if (some check beyond all required are not None):
                return False
        #As long as no required are set None, you're good
        return True
    '''
    def module_test(self):
        #Override this with any pre-module tests you need
        acceptable_colors=['red', 'orange', 'blue', 'green', None]
        if self.color['value'] not in acceptable_colors:
            bc.err_print("[!] ", "- Color {} invalid - must be set to red, orange, green, blue or None.".format(self.color['value']))
            return False
        #Check if we can cast this particular variable to an integer
        try:
            self.num_prints['value'] = int(self.num_prints['value'])
        except:
            bc.err_print("[!] ", "- num_prints invalid - must be integer. Cannot auto-convert.")
            return False
        if not isinstance(self.num_prints['value'], int):
            bc.err_print("[!] ", "- num_prints invalid - must be integer.")
            return False
        if not isinstance(self.message['value'], str):
            bc.err_print("[!] ", "- num_prints invalid - must be integer.")
            return False

        return True


def main():
    print("You're running a module as main, did you mean to?")

if __name__ == '__main__':
    main()
