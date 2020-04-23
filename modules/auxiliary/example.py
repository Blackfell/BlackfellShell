#!/usr/bin/python3

from common import bcolors as bc
from common import module as mod

class BSModule(mod.BSModule):
    """BShell module class, inherited for all modules run via BShell"""

    def __init__(self, parent_menu):
        mod.BSModule.__init__(self)
        #put YOUR attributes here
        self.parent_menu = parent_menu
        self.description = '''
        Example module, for use in understanding the BShell.

        Hello world within the BShell. Prints your message a number of times.
        num_repeats must be a string.
        color can be green, red, orange or blue.
        '''
        #List YOUR class setup & attributes here
        self.add_setting('message',None, True)
        self.add_setting('num_prints',None, True)
        self.add_setting('color',None, False)


    def run(self):
        """Main module code, called when the module is executed
        This module prints user provided messages to the console"""

        bc.success("Print incoming!")
        #Override with what to do with this class when it runs
        for time in range(self.options['num_prints']['value']):
            if self.get_option('color') == 'red':
                bc.err_print(self.options['message']['value'],'')
            elif self.get_option('color')  == 'orange':
                bc.warn_print(self.options['message']['value'],'')
            elif self.get_option('color')  == 'blue':
                bc.blue_print(self.options['message']['value'],'')
            elif self.get_option('color')  == 'green':
                bc.green_print(self.options['message']['value'],'')
            else:
                print(self.get_option('message'))
        #Success variable can be used to check if sub-modules ran successfully
        #Unused in this case, but important if we don't want to exit failed modules.
        success = True
        if bool(self.get_option('exit_on_exec')) == True and success:
            bc.success("Module executed, exiting.")
            return True


    def setup(self):
        """Configures and tests the module, anything that sanity checks
        user input can be put in here"""

        #Override this with any pre-module tests you need
        acceptable_colors=['red', 'orange', 'blue', 'green', None]
        if self.get_option('color') not in acceptable_colors:
            bc.err_print("[!] ", "- Color {} invalid - must be set to red, orange, green, blue or None.".format(self.options['color'][0]))
            return False
        #Check if we can cast this particular variable to an integer
        try:
            self.set_option('num_prints', int(self.get_option('num_prints')))
        except:
            bc.err("num_prints {} invalid - must be integer. Cannot auto-convert.".format(self.options['num_prints'][0]))
            return False
        if not isinstance(self.get_option('num_prints'), int):
            bc.err("num_prints invalid - must be integer.")
            return False
        if not isinstance(self.get_option('message'), str):
            bc.err("num_prints invalid - must be integer.")
            return False
        if not self.check_bool('exit_on_exec'):
            return False

        return True


def main():
    print("You're running a module as main, did you mean to?")

if __name__ == '__main__':
    main()
