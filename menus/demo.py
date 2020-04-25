import time

from common import bcolors as bc


def demo():
    """Print a series of demo BShell commands to console"""

    bc.info("The BlackfellShell can be used to run any python module written for it, but the key functionality it allows is running agents.")
    time.sleep(5)
    bc.info("All modules are called using the keyword 'use' like this:")
    time.sleep(5)
    print("BS >\r", end="")
    time.sleep(1)
    fake_type('BS > ','use auxiliary/example')
    print("")
    bc.info("Using module:  auxiliary/example")
    print("""
    Example module, for use in understanding the BShell.

    Hello world within the BShell. Prints your message a number of times.
    num_repeats must be a string.
    color can be green, red, orange or blue.
    """)
    print("BS : " + bc.green_format("modules/auxiliary/example", "") + " >")
    time.sleep(10)
    bc.info("Once you've activated a module, you'll switch to a new menu.")
    time.sleep(2)
    bc.info("This new menu will allow you to configure and run the module.")
    time.sleep(2)
    bc.info("Start by getting module info:")
    time.sleep(2)
    fake_type("BS : " + bc.green_format("modules/auxiliary/example", "") + " > ", \
            'info')
    print("")
    bc.info("Showing info for module:\n")
    print("""Option               Value                                    Default                        Required?
======================================================================================================
exit_on_exec         True                                     True                           True
message              None                                     None                           True
num_prints           None                                     None                           True
color                None                                     None                           False
            """)
    time.sleep(5)
    bc.info("Each option in the module can be set with the 'set' keyword")
    time.sleep(4)
    fake_type("BS : " + bc.green_format("modules/auxiliary/example", "") + " > ", \
            'set color red')
    print("BS : " + bc.green_format("modules/auxiliary/example", "") + " > ")
    time.sleep(4)
    bc.info("Let's check it made a change.")
    time.sleep(4)
    fake_type("BS : " + bc.green_format("modules/auxiliary/example", "") + " > ", \
            'info')
    print("")
    bc.info("Showing info for module:\n")
    print("""Option               Value                                    Default                        Required?
======================================================================================================
exit_on_exec         True                                     True                           True
message              None                                     None                           True
num_prints           None                                     None                           True
color                red                                      None                           False
            """)
    time.sleep(4)
    bc.info("If you didn't like that, the reset keyword will set options back to default.")
    time.sleep(4)
    fake_type("BS : " + bc.green_format("modules/auxiliary/example", "") + " > ", \
            'reset color')
    time.sleep(2)
    fake_type("BS : " + bc.green_format("modules/auxiliary/example", "") + " > ", \
            'info')
    print("")
    time.sleep(1)
    bc.info("Showing info for module:\n")
    print("""Option               Value                                    Default                        Required?
======================================================================================================
exit_on_exec         True                                     True                           True
message              None                                     None                           True
num_prints           None                                     None                           True
color                None                                     None                           False
            """)
    time.sleep(4)
    bc.info("You must set all required options.")
    time.sleep(4)
    bc.info("Modules will test for required options, and maybe other things when they run.")
    time.sleep(4)
    bc.info("Let's configure the rest of this module now.")
    time.sleep(5)
    fake_type("BS : " + bc.green_format("modules/auxiliary/example", "") + " > ", \
            'set message Hello, World.')
    time.sleep(2)
    fake_type("BS : " + bc.green_format("modules/auxiliary/example", "") + " > ", \
            'set color red')
    time.sleep(2)
    bc.info("You can use tab completion on most settings, just hit tab once you've started typing.")
    time.sleep(5)
    message = "BS : " + bc.green_format("modules/auxiliary/example", "") + " > "
    for i in 'set nu':
        message += i
        print('{}\r'.format(message), end="")
        time.sleep(0.1)
    time.sleep(1)
    print('{}<TAB>\r'.format(message), end="")
    time.sleep(0.5)
    print('{}<TAB>\r'.format(message), end="")
    time.sleep(1)
    message = message + 'm_prints'
    print('{}\r'.format(message), end="")
    time.sleep(4)
    fake_type(message, ' 8')
    time.sleep(4)
    print("")
    fake_type("BS : " + bc.green_format("modules/auxiliary/example", "") + " > ", \
            'info')
    print("")
    time.sleep(1)
    bc.info("Showing info for module:\n")
    print("""Option               Value                                    Default                        Required?
======================================================================================================
exit_on_exec         True                                     True                           True
message              Hello, World.                            None                           True
num_prints           8                                        None                           True
color                red                                      None                           False
            """)
    time.sleep(5)
    bc.info("Now you're all configured, you can run the module with the 'execute' keyword")
    time.sleep(5)
    fake_type("BS : " + bc.green_format("modules/auxiliary/example", "") + " > ", \
            'execute')
    time.sleep(1)
    bc.info("Setting up module...")
    bc.success("Setup complete. Executing...")
    bc.green_print("[-] ", "Print incoming!")
    for i in range(8):
        bc.err_print("Hello, World.", "")
    bc.green_print("[-] ", "Module executed, exiting.")
    time.sleep(5)
    bc.info("Most commands have help messages you can use, just type help in any menu.")
    time.sleep(3)
    bc.success("Good luck!")


def fake_type(prompt, string):
    """Type characters to teh screen in a vaguely showy way"""

    for i in string:
        prompt += i
        print('{}\r'.format(prompt), end="")
        time.sleep(0.1)
    print("")
