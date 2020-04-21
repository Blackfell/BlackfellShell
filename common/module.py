#!/usr/bin/python3

from common import bcolors as bc

class BSModule():
    def __init__(self):
        #put YOUR attributes here
        self.description = '''Base module class, for use in BS Modules'''

        #Setup YOUR class attributes here
        self.options = {
                'exit_on_exec' : {
                        'value' : False,
                        'default' : True,
                        'required' : True,
                        }
                }
        #Add settings via helper function
        self.add_setting('exit_on_exec', True, True)

    def add_setting(self, name, default, required):
        """Use this to set your module settings if you like, I think it's more dev/user friendly.
                Helper function to append a setting to the module options dictionary"""
        self.options[name] = {}
        self.options[name]['value'] = self.options[name]['default'] = default
        self.options[name]['required'] = required

    def get_options(self):
        """Return module options for printing"""
        return list(self.options.keys())

    def get_option(self, setting):
        return self.options[setting]['value']

    def info(self):
        """Return module infor for printing"""
        info_list=[]
        for option, value in self.options.items():
            info_list.append([str(option), str(value['value']), str(value['default']), str(value['required'])])
        return info_list

    def set_option(self, opt, val):
        """Apply a value to a given setting """
        #Don't allow us to add options!
        if not opt in self.options:
            bc.warn_print("[!] ", "- {} not a valid option!".format(opt))
            return False
        self.options[opt]['value'] = val
        return True


    def reset_option(self, line):
        """Reset a setting back to the default value"""
        self.options[line]['value'] = self.defaults[line]['default']

    def check_required(self):
        """This just checks required stuff is set to at least something, if you need more, write it in!"""
        for option, value in self.options.items():
            if value['required'] and value['value'] == None:
                return False
        #As long as no required are set None, you're good
        return True

    def module_test(self):
        """Override this with any pre-module tests you need"""
        return True

    def run(self):
        """Override with what to do with this class when it runs"""
        bc.green_print("[!] ", "- Module running!")

        if self.exit_on_exec == True:
            bc.green_print("[!] ", "- Module executed.")

    def check_bool(self, setting):
        """Check boolean values and try and cast a string to boolean"""
        candidate = self.get_option(setting)
        if not isinstance(candidate, bool):
            if candidate == 'False':
                candidate = False
            elif candidate == 'True':
                candidate = True
            else:
                bc.err("exit_on_exec invalid, must be boolean.")
                return False
            self.set_option(setting, candidate)
            return True
        else:
            #It's already bool
            return True

def main():
    print("You're running the base module as main, did you mean to?")

if __name__ == '__main__':
    main()
