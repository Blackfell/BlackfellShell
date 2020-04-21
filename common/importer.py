#!/usr/bin/python3

"""Use custom meta hook to import modules available as strings.
Cp. PEP 302 http://www.python.org/dev/peps/pep-0302/#specification-part-2-registering-hooks
Blended with newer Python 3 guidance from:
https://www.python.org/dev/peps/pep-0302/
And replacing the imp call for a types call to avoid depracation
"""

import sys
import importlib
import types

class BSImporter(object):
    def __init__(self, modules_dict):
        self._modules = dict(modules_dict)

    def find_module(self, fullname, path):
        #print("Finding module!")
        if fullname in self._modules.keys():
            return self
        return None

    def get_code(self, fullname):
        try:
            return self._modules[fullname]
        except KeyError:
            return None

    def is_package(Self, fullname):
        return False


    def load_module(self, fullname):
        code = self.get_code(fullname)
        ispkg = self.is_package(fullname)
        #mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod = sys.modules.setdefault(fullname, types.ModuleType(fullname))
        mod.__file__ = "<%s>" % self.__class__.__name__
        mod.__loader__ = self
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        exec(code, mod.__dict__)
        #print("Mod: {}".format(dir(mod.__dict__)))
        return mod

def get_imported_funcs(module, name, debug=False):
    if debug:
        print(module)
        print(name)
        print(eval(name))
        for i in dir(module):
            if isinstance(eval(name+ '.' + str(i)), types.FunctionType):
                print("{} is an imported function!".format(i))
    return [i for i in dir(module) if isinstance(eval(name + '.' +str(i)), types.FunctionType)]


def bs_import(mods):
    sys.meta_path.append(BSImporter(mods))
    imported = []
    mod=funcs=''
    for mod_name in mods.keys():
        try:
            mod = importlib.import_module(mod_name)
            importlib.reload(mod)   #In case same names
            funcs = []
            for i in dir(mod):
                if isinstance(eval('mod.' + i), types.FunctionType):
                    funcs.append(i)
        except Exception as e:
            print("[!] - Error importing {}. Module code invalid?\n:{}".format(mod_name, e))
            return False, False
        #imported.append([mod, funcs])
    #print("meta path: {}".format(sys.meta_path))
        finally:
            sys.meta_path.pop() #Remove my appended thing
    #print("meta path: {}".format(sys.meta_path))
    return (mod, funcs)

def main():
    modules = {"test1" :
    """def main(args=None):
        print('Hello from Test1')""",
    "test2":
    """
def main(args=None):
    if not args:
        print('Hello from Test2!')
    else:
        hello2(args)
def hello2(name='TEST'):
    print('Hi again {}, Test2 here!'.format(name))"""
    }
    mods = bs_import(modules)
    #for mod, funcs in mods.items():
    #    for f in funcs:
#            eval('mod.' + f + '()')
    #print(mods)
    command = 'test2'
    cmd = command.split(' ')[0]
    args = ' '.join(command.split(' ')[1:])
    for m in mods.keys():
        if cmd in m.__name__:
            caller = getattr(m, 'main')
            caller(args)

if __name__ == '__main__':
    main()
