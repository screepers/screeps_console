
from screeps import ScreepsConnection
from settings import getSettings
from themes import themes
from types import FunctionType
import urwid


class Processor:

    apiclient = False
    aliases = {
        'theme': 'themes',
        'time': 'Game.time',
        'help': 'list'
    }

    def __init__(self):
        self.listbox = False
        self.listwalker = False
        self.edit = False

    def setDisplayWidgets(self, loop, frame, listbox, listwalker, edit):
        self.listbox = listbox
        self.listwalker = listwalker
        self.edit = edit
        self.loop = loop

    def getApiClient(self):
        if not self.apiclient:
            settings = getSettings()
            self.apiclient = ScreepsConnection(u=settings['screeps_username'],p=settings['screeps_password'],ptr=settings['screeps_ptr'])
        return self.apiclient

    def onInput(self, key):
        if not self.listbox:
            return
        if key == 'enter':
            self.onEnter(key)
            return
        return


    def onEnter(self, key):

        userInput = self.edit
        user_text = userInput.get_edit_text()


        # Check for builtin commands before passing to the screeps api.
        user_command_split = user_text.split(' ')
        first_command = user_command_split[0]

        ## Check to see if command is actually an alias
        if first_command in self.aliases:
            first_command = self.aliases[first_command]
            user_command_split[0] = first_command
            user_text = ' '.join(user_command_split)


        # Look for built in commands before attempting API call.
        builtin = Builtin()
        if hasattr(builtin, first_command):
            self.listwalker.append(urwid.Text(('logged_input', '> ' + user_text)))
            builtin_command = getattr(builtin, first_command)
            builtin_command(self)
            if len(self.listwalker) > 0:
                self.listbox.set_focus(len(self.listwalker)-1)
            userInput.set_edit_text('')
            return


        # Send command to Screeps API. Output will come from the console stream.
        if len(user_text) > 0:
            self.listwalker.append(urwid.Text(('logged_input', '> ' + user_text)))
            userInput.set_edit_text('')
            apiclient = self.getApiClient()
            result = apiclient.console(user_text)


class Builtin:


    def about(self, comp):
        about = 'Screeps Interactive Console by Robert Hafner <tedivm@tedivm.com>'
        comp.listwalker.append(urwid.Text(('logged_response', about)))
        return


    def clear(self, comp):
        comp.listbox.set_focus_pending = 0
        comp.listwalker[:] = [urwid.Text('')]
        return

    def exit(self, comp):
        raise urwid.ExitMainLoop()


    def list(self, comp):
        command_list = ''
        aliases = list(comp.aliases)
        builtin_list = [method for method in dir(self) if callable(getattr(self, method))]
        commands = builtin_list

        for alias in aliases:
            alias_real = comp.aliases[alias]
            if alias_real not in builtin_list:
                commands.append(alias)

        commands.sort()
        commands.reverse()
        for builtin_command in commands:
            if builtin_command != 'turtle':
                command_list = builtin_command + '  ' + command_list

        comp.listwalker.append(urwid.Text(('logged_response', command_list)))
        return


    def themes(self, comp):
        userInput = comp.edit
        user_text = userInput.get_edit_text()
        user_command_split = user_text.split(' ')
        if len(user_command_split) < 2 or user_command_split[1] == 'list':
            theme_names = themes.keys()
            theme_names.reverse()
            theme_list = ''
            for theme in theme_names:
                theme_list = theme + '  ' + theme_list

            comp.listwalker.append(urwid.Text(('logged_response', theme_list)))
            return

        theme = user_command_split[1]
        if theme in themes:
            comp.loop.screen.register_palette(themes[theme])
            comp.loop.screen.clear()

        return





    def turtle(self, comp):
        turtle = '''
 ________________
< How you doing? >
 ----------------
    \                                  ___-------___
     \                             _-~~             ~~-_
      \                         _-~                    /~-_
             /^\__/^\         /~  \                   /    \\
           /|  O|| O|        /      \_______________/        \\
          | |___||__|      /       /                \          \\
          |          \    /      /                    \          \\
          |   (_______) /______/                        \_________ \\
          |         / /         \                      /            \\
           \         \^\\\         \                  /               \     /
             \         ||           \______________/      _-_       //\__//
               \       ||------_-~~-_ ------------- \ --/~   ~\    || __/
                 ~-----||====/~     |==================|       |/~~~~~
                  (_(__/  ./     /                    \_\      \.
                         (_(___/                         \_____)_)
'''
        comp.listwalker.append(urwid.Text(('logged_response', turtle)))
        comp.listwalker.append(urwid.Text(('logged_response', '')))