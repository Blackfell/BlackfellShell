#!/usr/bin/python3

import cmd
import os
import glob
import sys
import readline
import signal
import time
import queue

from common import bcolors as bc


#Helper function for scrubbing file path matches
def scrub_matched(matched, prefix_length):
    filtered_matches=[]
    for i in matched:
        i_stripped =  i[ prefix_length : ]
        if not i_stripped.endswith('__.py') and not i_stripped.endswith('__'):
            if i_stripped.find('.py')>=0:
                filtered_matches.append(i_stripped[: i_stripped.find('.py') ])
            elif i_stripped.find('.yml')>=0:
                filtered_matches.append(i_stripped[: i_stripped.find('.yml') ])
            elif i_stripped.find('.yaml')>=0:
                filtered_matches.append(i_stripped[: i_stripped.find('.yaml') ])
            else:
                filtered_matches.append(i_stripped)
    return filtered_matches

#################### Main menu class #######################

class BlackfellShell(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.use_path = 'modules/'
        self.listeners = []
        rd_q = queue.Queue()
        wr_q = queue.Queue()
        self.q =  {
            'read' : rd_q,
            'write' : wr_q
            }
        self.root_menu = self
        self.q = self.root_menu.q
        self.resource_file = False
        self.resource_timeout = 0.1 #TODO set this as a flag instead of a timeout
        self.terminate_timeout = 3
        #Ensure os path completion works with slashes
        readline.set_completer_delims(' \n\t')

    def onecmd(self, line):
        if line == 'EOF':
            if not self.q['read'].empty() and self.q['read'].get() == "RESOURCE":
                self.q['write'].put("DONE")
            time.sleep(self.resource_timeout)   #probably end of resource file, so wait
        else:
            return super().onecmd(line)
    '''
    def onecmd(self, line):
        if line == 'EOF':
            if self.resource_file == True:
                self.resource_file = False
                pass
            else:
                pass
                time.sleep(self.resource_timeout)   #probably end of resource file, so wait
        else:
            return super().onecmd(line)
    '''

    ################# COMMANDS #######################

    #List commands
    def do_list(self, line):
        if line == 'listeners':
            self.list_listeners()
        elif line == 'agents':
            self.list_agents()
        elif line == 'payloads':
            bc.warn_print("[-] ", "- TODO - Impelement payload listing.")
        elif line == 'loot':
            bc.warn_print("[-] ", "- TODO - Impelement payload listing.")
        else:
            self.list_listeners()
            self.list_agents()

    def list_listeners(self):
        bc.green_print("\n[-] ", "Listeners:\n")
        format_string = "{:<40} {:<20} {:<10} {:<20}"
        underline = "=" * 100
        bc.bold_print(format_string.format("Name", "Status", "Agents", "Info"), "")
        bc.blue_print(underline, "")
        for l in self.root_menu.listeners:
            print(format_string.format(l.name, 'Alive' if l.isAlive()==1 else 'Dead' , len(l.agent_list), str(l.LHOST) + ':' + str(l.LPORT)))
        print("")

    def list_agents(self):
        bc.green_print("\n[-] ", "Agents:\n")
        format_string = "{:<30} {:<10} {:20} {:<10} {:<30}"
        underline = "=" * 100
        bc.bold_print(format_string.format("Name", "Activated", "Listener", "Status",  "Info"), "")
        bc.blue_print(underline, "")
        for l in self.root_menu.listeners:
            for a in l.agent_list:
                print(format_string.format(str(a.name), str(a.active), str(a.listener.name), 'Alive' if a.isAlive()==1 else 'Dead' , str(a.ip) + ":" + str(a.port)))
        print("")

    def help_list(self):
        print("")
        bc.blue_print('[-] ','List all agents & listeners. May be run without arguments.')
        print('Example:')
        print('\tlist agents')
        print('\tlist')
        print("")

    def complete_list(self, text, line, begidx, endidx):
        _AVAILABLE_LISTS = ('listeners', 'agents', 'payloads', 'loot')
        return [i for i in _AVAILABLE_LISTS if i.startswith(text)]

    #Kill commands
    def do_kill(self, line):
        if not line:
            input_str = bc.warn_format("[!]", " Do you want to kill all agents and listeners? [Y/n]:")
            if input(input_str.format(line)).lower() not in ['y', 'yes', 'ye']:
                return
        for l in self.root_menu.listeners:
            for a in l.agent_list:
                if line in l.name:
                    #l.terminate()
                    l.send_q.put('terminate')
                elif line in a.name:
                    #l.terminate_agent(a)
                    print("killing : {}".format(a.name))
                    l.send_q.put('terminate_agent {}'.format(a.name))
                #It's not our listener
                else:
                    bc.warn("{} not found, not terminating.".format(line))


    def help_kill(self):
        print("")
        bc.blue_print('[-] ','Kill a listener (and all associated agents), or a specific Agent.')
        print('Example:')
        print('\tkill listener 2')
        print('\tkill agent win-10-ent-1')
        print('\tkill agent *')
        print("")


    def complete_kill(self, text, line, begidx, endidx):
        l = [i for i in self.enum_listeners() if i.startswith(text)]
        a = [i for i in self.enum_agents() if i.startswith(text)]
        return [i for i in (l + a) if i.startswith(text)]

    #Module menu implementation menu implementation

    def help_use(self):
        print("")
        bc.blue_print('[-] ','Select a module to run.')
        print('Example:')
        print('\tuse listener/bs_http')
        print('\tuse implant/bs_rev_http')
        print("")
        #TODO - modules/droppers/exploits

    def complete_use(self, text, line, begidx, endidx):
        text = self.use_path + text
        if os.path.isdir(text):
            sm = scrub_matched(glob.glob(os.path.join(text, '*')) , len(self.use_path) )
            return sm
        else:
            sm = scrub_matched(glob.glob(text + '*'), len(self.use_path))
            return sm

    #TODO - info, load?

    ################## SUBMENUS #######################

    #Do in other menus
    #TODO - reload modules

    ################# UTILS ########################


    def post_loop(self):
        bc.bold_print("OKByeee!","")

    def enum_agents(self):
        agents = []
        for l in self.root_menu.listeners:
            for a in l.agent_list:
                agents.append(a.name)
        return agents

    def enum_listeners(self):
        listeners = []
        for l in self.root_menu.listeners:
            listeners.append(l.name)
        return listeners


    def do_shell(self, line):
        'Execute a local shell command direct in the BS prompt. Can be called with an exclamation point (!).'
        #TODO - warn about cd and pwd etc
        print(os.popen(line).read())

    def default(self, line):
        input_str = bc.warn_format("[-]", " Command not recognised, exec local shell command '{}'? [Y/n]:")
        if line == None:
            pass
        if input(input_str.format(line)).lower() in ['y', 'yes', 'ye']:
            print(os.popen(line).read())

    def do_exit(self, line):
        print("Exit implemented in children classes")

    def emptyline(self):
        pass

    def do_sleep(self, line):
        'Sleep the Blackfell Shell, for a number of seconds. Occasionally useful in scripting.'
        try:
            time.sleep(float(line))
        except Exception as e:
            bc.warn_print("[!] ", "Could not sleep for {} seconds. Exception:\n{}".format(iline, e))

    def sigint(self, signum, frame):
        if input("Are you sure you want to sigint? [y/n]:").lower() in ['y', 'ye', 'yes']:
            return True

    def do_exit(self, line, sigint=None):
        'Leave the Blackfell Shell Framework, terminating all agents & listeners. (-y to force)'
        input_str = bc.warn_format("[-]", " Do you want to exit, terminating all agents and listeners? [Y/n]:")
        if '-y' not in line and input(input_str.format(line)).lower() not in ['y', 'yes', 'ye']:
            return False
        else:
            for l in self.root_menu.listeners:
                l.terminate()
                l.join(self.terminate_timeout)
                if l.isAlive() == 1:
                    bc.err_print("[!] ", "- Could not elegantly kill listener: {}, continuing.".format(l.name))
            bc.blue_print("[!] ", "- All Listeners killed.")
            time.sleep(0.2)
            self.post_loop()
            sys.exit(0)
            return True


def main():
    bc.err_print("[!] ", "- You're running the Base Menu class as main, did you mean to do this?")

if __name__ == '__main__':
        main()
