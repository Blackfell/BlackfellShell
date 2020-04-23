def do_test(self, line):
    """example function to say hello in the menu"""
    
    greet = 'World' if line == '' else line
    print("Hello, {}, you're in the menu.".format(greet))
    for agent in self.active_agents:
        agent.send_q.put('test ' + greet)

def complete_test(self, text, line, begidx, endidx):
    _AVAILABLE_LISTS = ['Dave', 'There', 'Maximillion, overlord of Zanthar.']
    return [i for i in _AVAILABLE_LISTS if i.startswith(text)]
